"""SWDL Admin — shared helpers, decorators, context processor, and utility routes."""
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify, send_file, current_app)
from flask_login import login_required, current_user
from extensions import db, socketio
from models.news         import News
from models.agenda       import AgendaItem
from models.inscription  import Inscription
from models.delegation   import Delegation
from models.user         import User
from models.student      import Student
from models.document     import Document
from models.event_config import EventConfig
from models.audit_log   import AuditLog
from models.category    import Category
from models.theme      import Theme
from models.urgent_alert import UrgentAlert
from datetime import datetime, timezone
from routes.agenda_utils import get_agenda_status
import os, uuid as _uuid, hmac, hashlib

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator: so admin (nao diretores)."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def moderator_required(f):
    """Decorator: admin ou diretor (mesa)."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def get_current_delegation():
    """Return the delegation for the current user, or None."""
    if not current_user.is_authenticated:
        return None
    return Delegation.query.filter_by(user_id=current_user.id).first()


@admin_bp.context_processor
def inject_globals():
    try:
        phase, _, _ = get_agenda_status()
        override = EventConfig.get_phase_override()
        if override in ('pre', 'during', 'post'):
            phase = override
        active_invoke = EventConfig.get_invoke()
        active_alerts = UrgentAlert.query.filter_by(active=True).order_by(UrgentAlert.created_at.desc()).all()
        return dict(event_phase=phase or 'pre', active_invoke=active_invoke,
                    active_alerts=active_alerts,
                    is_admin=current_user.is_admin() if current_user.is_authenticated else False)
    except Exception:
        from flask import current_app
        current_app.logger.error('Context processor error', exc_info=True)
        db.session.rollback()
        return dict(event_phase='pre', active_invoke=None, active_alerts=[])


@admin_bp.route('/phase/set/<phase>', methods=['POST'])
@login_required
@admin_required
def phase_set(phase):
    """Override manual da fase (pre/during/post). Limpa o override com 'auto'."""
    if phase == 'auto':
        EventConfig.set_phase_override(None)
        flash('🔄 Fase voltou ao calculo automatico (agenda).', 'success')
    elif phase in ('pre', 'during', 'post'):
        EventConfig.set_phase_override(phase)
        labels = {'pre': '🟢 PRE-EVENTO', 'during': '🔴 DURANTE A SIMULACAO', 'post': '🔵 POS-EVENTO'}
        flash(f'Fase alterada para {labels[phase]}', 'success')
    else:
        flash('Fase invalida.', 'error')
        return redirect(url_for('admin.dashboard'))
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/uploads/<path:filename>')
@login_required
def serve_upload(filename):
    """Serve arquivos enviados via upload."""
    from config import Config
    filepath = os.path.realpath(os.path.join(Config.UPLOAD_FOLDER, filename))
    if not filepath.startswith(os.path.realpath(Config.UPLOAD_FOLDER)):
        abort(403)
    if not os.path.isfile(filepath):
        abort(404)
    mimetype = 'application/octet-stream'
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
        mimetype = f'image/{filename.rsplit(".", 1)[-1].lower()}'
    elif filename.lower().endswith('.pdf'):
        mimetype = 'application/pdf'
    return send_file(filepath, mimetype=mimetype)


def _ensure_participation_history(student):
    """Cria ou atualiza ParticipationHistory para o ano atual."""
    from models.participation import ParticipationHistory
    if not student.delegation:
        return
    year = datetime.now(timezone.utc).year
    deleg = student.delegation
    data = dict(
        committee=deleg.committee,
        committee_name=deleg.theme.name if deleg.theme else (deleg.committee or ''),
        country=deleg.country or '',
        country_flag=deleg.country_flag or '',
        role='delegate',
        delegation_name=f"{deleg.country or ''} @ {deleg.committee or ''}",
    )
    entry = ParticipationHistory.query.filter_by(
        student_id=student.id, year=year
    ).first()
    if not entry:
        entry = ParticipationHistory(student_id=student.id, year=year, **data)
        db.session.add(entry)
    else:
        for k, v in data.items():
            setattr(entry, k, v)


def _cleanup_orphan_delegation(deleg_id):
    """Remove uma delegacao que ficou sem alunos, desde que nao tenha votos,
    DPO ou presence registrada (evita perda de dados)."""
    from models.vote import Vote
    d = Delegation.query.get(deleg_id)
    if not d:
        return
    if d.students:
        return
    if Vote.query.filter_by(delegation_id=d.id).first():
        return
    if d.dpo_path or d.dpo_uploaded:
        return
    if d.presence_status and d.presence_status != 'ausente':
        return
    db.session.delete(d)


def _sign_certificate(student):
    """Gera uma assinatura HMAC-SHA256 para o certificado."""
    if not student.verification_code:
        return None
    secret = current_app.config.get('SECRET_KEY', 'swdl-secret')
    student.digital_signature = student.compute_signature(secret)
    student.signed_at = datetime.now(timezone.utc)
    db.session.commit()
    return student.digital_signature


def _log_audit(action, target_type, target_id, target_name='', details=''):
    log = AuditLog(
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        user_id=current_user.id,
        user_name=current_user.name or current_user.email,
        details=details,
    )
    db.session.add(log)
    db.session.commit()
