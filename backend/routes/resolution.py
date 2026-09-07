# =============================================================
#  SWDL — routes/resolution.py
#  Resoluções com cláusulas, emendas e votação por artigo
# =============================================================
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify)
from flask_login import login_required, current_user
from extensions import db, socketio
from models.delegation import Delegation
from models.resolution import Resolution, Amendment
from models.vote import VoteSession
from models.speech_log import SpeechLog
from datetime import datetime, timezone

resolution_bp = Blueprint('resolution', __name__)


def moderator_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def _emit_resolution_update(committee):
    resolutions = Resolution.for_committee(committee)
    socketio.emit('resolution_list_updated', {
        'committee': committee,
        'resolutions': [r.to_dict() for r in resolutions],
    }, room='admin')


def _emit_telao_resolution(committee):
    active = Resolution.query.filter_by(
        committee=committee, status='voting'
    ).first()
    submitted = Resolution.query.filter_by(
        committee=committee, status='submitted'
    ).order_by(Resolution.submitted_at.desc()).all()
    socketio.emit('resolution_display', {
        'committee': committee,
        'active': active.to_dict() if active else None,
        'submitted': [r.to_dict() for r in submitted[:5]],
    }, room='telao')


# ═══════ ADMIN ROUTES ═══════

@resolution_bp.route('/admin/resolucoes')
@login_required
@moderator_required
def resolutions_panel():
    committee_filter = request.args.get('committee', 'all')

    committees_query = db.session.query(Resolution.committee).filter(
        Resolution.committee.isnot(None),
        Resolution.committee != ''
    ).distinct().all()
    available_committees = sorted([c[0] for c in committees_query])

    if committee_filter != 'all':
        resolutions = Resolution.for_committee(committee_filter)
    else:
        resolutions = Resolution.query.order_by(Resolution.created_at.desc()).all()

    return render_template('admin/resolutions.html',
                           resolutions=resolutions,
                           committee_filter=committee_filter,
                           available_committees=available_committees)


@resolution_bp.route('/admin/resolucoes/<int:id>')
@login_required
@moderator_required
def resolution_detail(id):
    res = Resolution.query.get_or_404(id)
    return render_template('admin/resolution_view.html', resolution=res)


@resolution_bp.route('/admin/resolucoes/<id>/aprovar-submissao', methods=['POST'])
@login_required
@moderator_required
def resolution_approve_submission(id):
    res = Resolution.query.get_or_404(id)
    if res.status != 'submitted':
        return jsonify({'status': 'error', 'message': 'Resolução não está submetida'}), 400

    res.status = 'voting'
    res.voted_at = datetime.now(timezone.utc)
    db.session.commit()

    socketio.emit('resolution_voting', res.to_dict(), room='telao')
    _emit_resolution_update(res.committee)
    _emit_telao_resolution(res.committee)

    return jsonify({'status': 'success', 'resolution': res.to_dict()})


@resolution_bp.route('/admin/resolucoes/<id>/rejeitar-submissao', methods=['POST'])
@login_required
@moderator_required
def resolution_reject_submission(id):
    res = Resolution.query.get_or_404(id)
    if res.status != 'submitted':
        return jsonify({'status': 'error', 'message': 'Resolução não está submetida'}), 400

    res.status = 'rejected'
    res.voted_at = datetime.now(timezone.utc)
    db.session.commit()

    _emit_resolution_update(res.committee)
    _emit_telao_resolution(res.committee)

    return jsonify({'status': 'success', 'resolution': res.to_dict()})


@resolution_bp.route('/admin/resolucoes/<id>/emenda/<eid>/decidir', methods=['POST'])
@login_required
@moderator_required
def amendment_decide(id, eid):
    res = Resolution.query.get_or_404(id)
    amendment = Amendment.query.get_or_404(eid)
    if amendment.resolution_id != res.id:
        return jsonify({'status': 'error', 'message': 'Emenda não pertence a esta resolução'}), 400

    data = request.get_json(silent=True) or {}
    decision = data.get('decision', 'accepted')
    if decision not in ('accepted', 'rejected'):
        return jsonify({'status': 'error', 'message': 'Decisão inválida'}), 400

    amendment.status = decision
    amendment.decided_at = datetime.now(timezone.utc)

    if decision == 'accepted':
        clauses = res.preambulatory_clauses() if amendment.target_section == 'preambulatory' else res.operative_clauses()
        if amendment.target_index < len(clauses):
            clauses[amendment.target_index] = amendment.proposed_text
        else:
            clauses.append(amendment.proposed_text)

        if amendment.target_section == 'preambulatory':
            res.preambulatory = '\n'.join(clauses)
        else:
            res.operative = '\n'.join(clauses)

    db.session.commit()
    _emit_resolution_update(res.committee)

    return jsonify({'status': 'success', 'amendment': amendment.to_dict()})


@resolution_bp.route('/admin/resolucoes/<id>/votar-final', methods=['POST'])
@login_required
@moderator_required
def resolution_vote_final(id):
    res = Resolution.query.get_or_404(id)
    if res.status != 'voting':
        return jsonify({'status': 'error', 'message': 'Resolução não está em votação'}), 400

    data = request.get_json(silent=True) or {}
    decision = data.get('decision', 'passed')
    if decision not in ('passed', 'rejected'):
        return jsonify({'status': 'error', 'message': 'Decisão inválida'}), 400

    res.status = decision
    res.voted_at = datetime.now(timezone.utc)
    db.session.commit()

    socketio.emit('resolution_completed', res.to_dict(), room='telao')
    _emit_resolution_update(res.committee)
    _emit_telao_resolution(res.committee)

    return jsonify({'status': 'success', 'resolution': res.to_dict()})


@resolution_bp.route('/admin/resolucoes/telao', methods=['POST'])
@login_required
@moderator_required
def resolution_telao():
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'show')
    committee = data.get('committee', 'all')

    if action == 'show':
        _emit_telao_resolution(committee if committee != 'all' else None)
        return jsonify({'status': 'success'})
    else:
        socketio.emit('resolution_hide', {}, room='telao')
        return jsonify({'status': 'success'})


# ═══════ STUDENT ROUTES ═══════

@resolution_bp.route('/delegado/resolucoes')
@login_required
def student_resolutions():
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        abort(403)

    student = getattr(current_user, 'student', None)
    if not student:
        abort(403)

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation or not delegation.committee:
        abort(403)

    committee = delegation.committee
    resolutions = Resolution.for_committee(committee)

    return render_template('student/resolutions.html',
                           resolutions=resolutions,
                           delegation=delegation,
                           committee=committee)


@resolution_bp.route('/delegado/resolucoes/nova', methods=['POST'])
@login_required
def student_resolution_create():
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        return jsonify({'status': 'error', 'message': 'Não autorizado'}), 403

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation or not delegation.committee:
        return jsonify({'status': 'error', 'message': 'Delegação não encontrada'}), 400

    data = request.get_json(silent=True) or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'status': 'error', 'message': 'Título obrigatório'}), 400

    resolution = Resolution(
        title=title,
        committee=delegation.committee,
        preambulatory=data.get('preambulatory', ''),
        operative=data.get('operative', ''),
        proposer_id=delegation.id,
        status='draft',
    )
    db.session.add(resolution)
    db.session.commit()

    SpeechLog.log(
        delegation_id=delegation.id,
        committee=delegation.committee,
        log_type='resolution_created',
        topic=title,
        reference_id=resolution.id,
        reference_type='resolution',
    )

    return jsonify({'status': 'success', 'resolution': resolution.to_dict()})


@resolution_bp.route('/delegado/resolucoes/<id>/editar', methods=['POST'])
@login_required
def student_resolution_edit(id):
    res = Resolution.query.get_or_404(id)
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        return jsonify({'status': 'error', 'message': 'Não autorizado'}), 403

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation or res.proposer_id != delegation.id:
        return jsonify({'status': 'error', 'message': 'Sem permissão'}), 403

    if res.status != 'draft':
        return jsonify({'status': 'error', 'message': 'Só pode editar resoluções em rascunho'}), 400

    data = request.get_json(silent=True) or {}
    if 'title' in data:
        res.title = data['title']
    if 'preambulatory' in data:
        res.preambulatory = data['preambulatory']
    if 'operative' in data:
        res.operative = data['operative']
    db.session.commit()

    return jsonify({'status': 'success', 'resolution': res.to_dict()})


@resolution_bp.route('/delegado/resolucoes/<id>/submeter', methods=['POST'])
@login_required
def student_resolution_submit(id):
    res = Resolution.query.get_or_404(id)
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        return jsonify({'status': 'error', 'message': 'Não autorizado'}), 403

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation or res.proposer_id != delegation.id:
        return jsonify({'status': 'error', 'message': 'Sem permissão'}), 403

    if res.status != 'draft':
        return jsonify({'status': 'error', 'message': 'Só pode submeter resoluções em rascunho'}), 400

    res.status = 'submitted'
    res.submitted_at = datetime.now(timezone.utc)
    db.session.commit()

    _emit_resolution_update(res.committee)
    _emit_telao_resolution(res.committee)

    return jsonify({'status': 'success', 'resolution': res.to_dict()})


@resolution_bp.route('/delegado/resolucoes/<id>/apoiar', methods=['POST'])
@login_required
def student_resolution_cosponsor(id):
    res = Resolution.query.get_or_404(id)
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        return jsonify({'status': 'error', 'message': 'Não autorizado'}), 403

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation:
        return jsonify({'status': 'error', 'message': 'Delegação não encontrada'}), 400

    if delegation.id == res.proposer_id:
        return jsonify({'status': 'error', 'message': 'Não pode apoiar sua própria resolução'}), 400

    res.add_co_sponsor(delegation.id)
    db.session.commit()

    return jsonify({'status': 'success', 'resolution': res.to_dict()})


@resolution_bp.route('/delegado/resolucoes/<id>/emendar', methods=['POST'])
@login_required
def student_resolution_amend(id):
    res = Resolution.query.get_or_404(id)
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        return jsonify({'status': 'error', 'message': 'Não autorizado'}), 403

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation:
        return jsonify({'status': 'error', 'message': 'Delegação não encontrada'}), 400

    if res.status not in ('draft', 'submitted'):
        return jsonify({'status': 'error', 'message': 'Não é possível emendar nesta fase'}), 400

    data = request.get_json(silent=True) or {}
    target_section = data.get('target_section', 'operative')
    target_index = int(data.get('target_index', 0))
    proposed_text = data.get('proposed_text', '').strip()

    if not proposed_text:
        return jsonify({'status': 'error', 'message': 'Texto proposto obrigatório'}), 400

    clauses = res.preambulatory_clauses() if target_section == 'preambulatory' else res.operative_clauses()
    if target_index >= len(clauses):
        original_text = ''
    else:
        original_text = clauses[target_index]

    amendment = Amendment(
        resolution_id=res.id,
        proposer_id=delegation.id,
        amendment_type=data.get('amendment_type', 'friendly'),
        target_section=target_section,
        target_index=target_index,
        original_text=original_text,
        proposed_text=proposed_text,
        status='pending',
    )
    db.session.add(amendment)
    db.session.commit()

    _emit_resolution_update(res.committee)

    return jsonify({'status': 'success', 'amendment': amendment.to_dict()})
