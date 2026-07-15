from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, abort, jsonify, current_app)
from flask_login import login_required, current_user
from extensions import db
from models.student import Student
from models.participation import ParticipationHistory
from models.delegation import Delegation
from models.news import News
from models.agenda import AgendaItem
from models.document import Document
from models.vote import VoteSession, Vote
from models.event_config import EventConfig
from models.audit_log import AuditLog
from datetime import datetime
import os

student_bp = Blueprint('student', __name__)


@student_bp.context_processor
def inject_now():
    from datetime import datetime
    event_phase = EventConfig.get_phase()
    is_convened = False
    try:
        is_convened = current_user.student_profile.convened
    except Exception:
        pass
    return {'now': datetime.utcnow, 'event_phase': event_phase, 'is_convened': is_convened}


def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.student_login'))
        if current_user.role != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def get_student():
    return Student.query.filter_by(user_id=current_user.id).first()


def check_read_only(student):
    if student and student.read_only:
        return True
    return False


# ── DASHBOARD ──────────────────────────────────────────────────
@student_bp.route('/student')
@login_required
@student_required
def dashboard():
    student_profile = get_student()

    if student_profile and student_profile.delegation_id:
        delegation = Delegation.query.get(student_profile.delegation_id)
    else:
        delegation = None

    recent_news  = News.query.filter_by(published=True)\
                             .order_by(News.created_at.desc()).limit(4).all()
    current_item = AgendaItem.query.filter_by(status='now').first()
    next_item    = AgendaItem.query.filter_by(status='next')\
                                   .order_by(AgendaItem.order).first()

    if delegation and delegation.theme_id:
        docs = Document.query.filter(
            db.or_(Document.theme_id == delegation.theme_id, Document.theme_id.is_(None))
        ).order_by(Document.created_at.desc()).all()
    else:
        docs = Document.query.order_by(Document.created_at.desc()).all()

    read_only   = check_read_only(student_profile)
    event_phase = EventConfig.get_phase()

    return render_template('student/dashboard.html',
                           student=student_profile,
                           delegation=delegation,
                           recent_news=recent_news,
                           current_item=current_item,
                           next_item=next_item,
                           documentos=docs,
                           read_only=read_only,
                           event_phase=event_phase)


# ── MEU HISTÓRICO ──────────────────────────────────────────────
@student_bp.route('/student/historico')
@login_required
@student_required
def history():
    student_profile = get_student()
    participations = []
    if student_profile:
        participations = ParticipationHistory.query.filter_by(
            student_id=student_profile.id
        ).order_by(ParticipationHistory.year.desc()).all()

    return render_template('student/history.html',
                           student=student_profile,
                           participations=participations)


# ── PRESENÇA ───────────────────────────────────────────────────
@student_bp.route('/student/presenca', methods=['GET', 'POST'])
@login_required
@student_required
def attendance():
    student_profile = get_student()
    if check_read_only(student_profile):
        flash('O evento foi encerrado. A interface está em modo somente leitura.', 'warning')
        return redirect(url_for('student.dashboard'))

    delegation = None
    if student_profile and student_profile.delegation_id:
        delegation = Delegation.query.get(student_profile.delegation_id)

    if request.method == 'POST' and delegation:
        action = request.form.get('action')
        quick_mode = request.form.get('quick_mode')

        if action == 'registrar':
            delegation.presence_status = 'presente'
            db.session.commit()
            flash('Presença registrada com sucesso!', 'success')
            if quick_mode:
                from flask_login import logout_user
                logout_user()
                return redirect(url_for('auth.student_login'))
        elif action == 'modo_adaptado':
            delegation.presence_status = 'presente'
            student_profile.adapted_device = True
            db.session.commit()
            flash('Presença registrada em modo adaptado (dispositivo compartilhado).', 'success')
            if quick_mode:
                from flask_login import logout_user
                logout_user()
                return redirect(url_for('auth.student_login'))
        return redirect(url_for('student.attendance'))

    return render_template('student/attendance.html',
                           student=student_profile,
                           delegation=delegation)


# ── VOTAÇÃO ────────────────────────────────────────────────────
@student_bp.route('/student/votacao')
@login_required
@student_required
def voting():
    student_profile = get_student()
    if check_read_only(student_profile):
        flash('O evento foi encerrado. A interface está em modo somente leitura.', 'warning')
        return redirect(url_for('student.dashboard'))

    delegation = None
    if student_profile and student_profile.delegation_id:
        delegation = Delegation.query.get(student_profile.delegation_id)

    open_sessions = VoteSession.query.filter_by(status='open').all()

    voted_ids = set()
    if delegation:
        voted_ids = {
            v.session_id for v in
            Vote.query.filter_by(delegation_id=delegation.id).all()
        }

    presence_status = delegation.presence_status if delegation else 'ausente'

    return render_template('student/voting.html',
                           student=student_profile,
                           delegation=delegation,
                           open_sessions=open_sessions,
                           voted_ids=voted_ids,
                           presence_status=presence_status)


# ── DOCUMENTOS ─────────────────────────────────────────────────
@student_bp.route('/student/documentos')
@login_required
@student_required
def documentos():
    student_profile = get_student()
    delegation = None
    if student_profile and student_profile.delegation_id:
        delegation = Delegation.query.get(student_profile.delegation_id)

    cat = request.args.get('categoria', '')

    q = Document.query
    if cat:
        q = q.filter(Document.category == cat)
    if delegation and delegation.theme_id:
        q = q.filter(
            db.or_(Document.theme_id == delegation.theme_id, Document.theme_id.is_(None))
        )
    docs = q.order_by(Document.created_at.desc()).all()

    available_cats = [
        ('', 'Todas'),
        ('guias', 'Guias'),
        ('comunicados', 'Comunicados'),
        ('resolucoes', 'Resoluções'),
        ('mesa', 'Mesa'),
    ]

    return render_template('student/documentos.html',
                           student=student_profile,
                           documentos=docs,
                           current_cat=cat,
                           available_cats=available_cats)


@student_bp.route('/student/documentos/<int:id>/download')
@login_required
@student_required
def documento_download(id):
    from flask import send_file
    import os
    doc = Document.query.get_or_404(id)
    if not os.path.isfile(doc.file_path):
        flash('Arquivo não encontrado.', 'error')
        return redirect(url_for('student.documentos'))
    return send_file(
        doc.file_path,
        as_attachment=True,
        download_name=doc.filename(),
    )


# ── COMUNICADOS ────────────────────────────────────────────────
@student_bp.route('/student/comunicados')
@login_required
@student_required
def comunicados():
    news = News.query.filter_by(published=True)\
                     .order_by(News.created_at.desc()).all()
    return render_template('student/comunicados.html',
                           news=news)


# ── CERTIFICADOS ───────────────────────────────────────────────
@student_bp.route('/student/certificados')
@login_required
@student_required
def certificados():
    student_profile = get_student()
    return render_template('student/certificados.html',
                           student=student_profile)


# ── PERFIL ─────────────────────────────────────────────────────
@student_bp.route('/student/perfil')
@login_required
@student_required
def profile():
    student_profile = get_student()
    delegation = None
    if student_profile and student_profile.delegation_id:
        delegation = Delegation.query.get(student_profile.delegation_id)
    return render_template('student/profile.html',
                           student=student_profile,
                           delegation=delegation)


# ── DPO (Documento de Posição Oficial) ────────────────────────

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads', 'dpo'
)


@student_bp.route('/student/dpo/enviar', methods=['POST'])
@login_required
@student_required
def dpo_upload():
    student_profile = get_student()
    if not student_profile or not student_profile.delegation_id:
        flash('Você precisa estar vinculado a uma delegação para enviar DPO.', 'error')
        return redirect(url_for('student.profile'))

    delegation = Delegation.query.get(student_profile.delegation_id)
    if not delegation:
        flash('Delegação não encontrada.', 'error')
        return redirect(url_for('student.profile'))

    if 'dpo_file' not in request.files:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('student.profile'))

    file = request.files['dpo_file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('student.profile'))

    allowed = {'pdf'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        flash('Apenas arquivos PDF são permitidos.', 'error')
        return redirect(url_for('student.profile'))

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    safe_name = f"dpo_{delegation.id}_{delegation.country or 'delegacao'}.pdf"
    filepath = os.path.join(UPLOAD_FOLDER, safe_name)
    file.save(filepath)

    delegation.dpo_path = filepath
    delegation.dpo_uploaded = True
    db.session.commit()

    log = AuditLog(
        action='dpo_upload',
        target_type='delegation',
        target_id=delegation.id,
        target_name=f"{delegation.country or '?'} — {delegation.committee or '?'}",
        user_id=current_user.id,
        user_name=current_user.name or current_user.email,
        details=f'DPO enviado por {current_user.name}',
    )
    db.session.add(log)
    db.session.commit()

    flash('📄 DPO enviado com sucesso!', 'success')
    return redirect(url_for('student.profile'))


# ── API: registrar presença (AJAX) ─────────────────────────────
@student_bp.route('/api/student/presenca', methods=['POST'])
@login_required
@student_required
def api_attendance():
    student_profile = get_student()
    if check_read_only(student_profile):
        return jsonify({'ok': False, 'error': 'Evento encerrado. Modo somente leitura.'}), 403

    data = request.get_json(silent=True) or {}
    adapted = data.get('adapted', False)

    delegation = None
    if student_profile and student_profile.delegation_id:
        delegation = Delegation.query.get(student_profile.delegation_id)

    if not delegation:
        return jsonify({'ok': False, 'error': 'Delegação não encontrada.'}), 404

    delegation.presence_status = 'presente'
    if adapted:
        student_profile.adapted_device = True
    db.session.commit()

    return jsonify({'ok': True, 'presence_status': delegation.presence_status})


# ── API: verificar certificado (endpoint público) ──────────────
@student_bp.route('/api/certificado/validar')
def api_validate_certificate():
    hash_code = request.args.get('hash', '')
    if not hash_code:
        return jsonify({'ok': False, 'error': 'Hash é obrigatório.'}), 400

    student = Student.query.filter_by(certificate_hash=hash_code).first()
    if not student or not student.certificate_released:
        return jsonify({'ok': False, 'valid': False,
                        'error': 'Certificado não encontrado ou não liberado.'}), 404

    sig_valid = student.verify_signature(current_app.config.get('SECRET_KEY', 'swdl-secret')) if student.digital_signature else None

    return jsonify({
        'ok': True,
        'valid': True,
        'name': student.name,
        'certificate_url': student.certificate_url,
        'digital_signature': bool(student.digital_signature),
        'signature_valid': sig_valid,
        'signed_at': student.signed_at.isoformat() if student.signed_at else None,
    })


# ── WEBSOCKET: join student room ──────────────────────────────
from flask_socketio import emit, join_room
from extensions import socketio


@socketio.on('join_students')
def on_join_students(data):
    join_room('all_students')
    open_sessions = VoteSession.query.filter_by(status='open').all()
    emit('open_sessions', [s.to_dict() for s in open_sessions])
