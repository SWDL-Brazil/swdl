# =============================================================
#  SWDL — routes/motion.py
#  Fila de moções do debate
# =============================================================
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify)
from flask_login import login_required, current_user
from extensions import db, socketio
from models.delegation import Delegation
from models.motion import Motion, MOTION_TYPES
from models.speech_log import SpeechLog
from datetime import datetime, timezone

motion_bp = Blueprint('motion', __name__)


def moderator_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def _emit_motion_update(committee):
    pending = Motion.pending_for_committee(committee)
    active = Motion.active_for_committee(committee)
    log = Motion.today_log(committee)
    socketio.emit('motion_queue_updated', {
        'committee': committee,
        'pending': [m.to_dict() for m in pending],
        'active': active.to_dict() if active else None,
        'log': [m.to_dict() for m in log[:20]],
    }, room='admin')


def _emit_telao_motions(committee):
    pending = Motion.pending_for_committee(committee)
    active = Motion.active_for_committee(committee)
    socketio.emit('motion_queue_display', {
        'committee': committee,
        'pending': [m.to_dict() for m in pending],
        'active': active.to_dict() if active else None,
    }, room='telao')


# ═══════ ADMIN ROUTES ═══════

@motion_bp.route('/admin/mocoes')
@login_required
@moderator_required
def motions_panel():
    committee_filter = request.args.get('committee', 'all')

    committees_query = db.session.query(Delegation.committee).filter(
        Delegation.committee.isnot(None),
        Delegation.committee != ''
    ).distinct().all()
    available_committees = sorted([c[0] for c in committees_query])

    pending = Motion.pending_for_committee(
        committee_filter if committee_filter != 'all' else None
    )
    active = Motion.active_for_committee(
        committee_filter if committee_filter != 'all' else None
    )
    log = Motion.today_log(
        committee_filter if committee_filter != 'all' else None
    )

    return render_template('admin/motions.html',
                           pending=pending,
                           active=active,
                           log=log,
                           motion_types=MOTION_TYPES,
                           committee_filter=committee_filter,
                           available_committees=available_committees)


@motion_bp.route('/admin/mocoes/nova', methods=['GET', 'POST'])
@login_required
@moderator_required
def motion_create():
    if request.method == 'POST':
        data = request.form
        motion_type = data.get('motion_type', 'moderated_caucus')
        info = MOTION_TYPES.get(motion_type, MOTION_TYPES['other'])

        motion = Motion(
            proposer_id=int(data['proposer_id']),
            committee=data['committee'],
            motion_type=motion_type,
            topic=data['topic'],
            total_time=int(data.get('total_time', info['default_total'])),
            speaking_time=int(data.get('speaking_time', info['default_speaking'])),
            status='pending',
        )
        db.session.add(motion)
        db.session.commit()

        _emit_motion_update(motion.committee)
        _emit_telao_motions(motion.committee)

        flash('Moção criada com sucesso!', 'success')
        return redirect(url_for('motion.motions_panel', committee=motion.committee))

    committee_filter = request.args.get('committee', 'all')
    committees_query = db.session.query(Delegation.committee).filter(
        Delegation.committee.isnot(None),
        Delegation.committee != ''
    ).distinct().all()
    available_committees = sorted([c[0] for c in committees_query])

    delegations = Delegation.query.filter_by(presence_status='votante')
    if committee_filter != 'all':
        delegations = delegations.filter_by(committee=committee_filter)
    delegations = delegations.order_by(Delegation.country).all()

    return render_template('admin/motion_form.html',
                           motion_types=MOTION_TYPES,
                           delegations=delegations,
                           available_committees=available_committees,
                           committee_filter=committee_filter)


@motion_bp.route('/admin/mocoes/<int:id>/aprovar', methods=['POST'])
@login_required
@moderator_required
def motion_approve(id):
    motion = Motion.query.get_or_404(id)
    if motion.status != 'pending':
        return jsonify({'status': 'error', 'message': 'Moção não está pendente'}), 400

    active = Motion.active_for_committee(motion.committee)
    if active:
        return jsonify({'status': 'error', 'message': 'Já há uma moção ativa neste comitê'}), 400

    motion.status = 'approved'
    motion.decided_at = datetime.now(timezone.utc)
    db.session.commit()

    _emit_motion_update(motion.committee)
    _emit_telao_motions(motion.committee)

    return jsonify({'status': 'success', 'motion': motion.to_dict()})


@motion_bp.route('/admin/mocoes/<int:id>/rejeitar', methods=['POST'])
@login_required
@moderator_required
def motion_reject(id):
    motion = Motion.query.get_or_404(id)
    if motion.status != 'pending':
        return jsonify({'status': 'error', 'message': 'Moção não está pendente'}), 400

    motion.status = 'rejected'
    motion.decided_at = datetime.now(timezone.utc)
    db.session.commit()

    _emit_motion_update(motion.committee)
    _emit_telao_motions(motion.committee)

    return jsonify({'status': 'success', 'motion': motion.to_dict()})


@motion_bp.route('/admin/mocoes/<int:id>/ativar', methods=['POST'])
@login_required
@moderator_required
def motion_activate(id):
    motion = Motion.query.get_or_404(id)
    if motion.status not in ('pending', 'approved'):
        return jsonify({'status': 'error', 'message': 'Moção não pode ser ativada'}), 400

    active = Motion.active_for_committee(motion.committee)
    if active and active.id != id:
        return jsonify({'status': 'error', 'message': 'Já há uma moção ativa'}), 400

    motion.status = 'active'
    motion.decided_at = datetime.now(timezone.utc)
    db.session.commit()

    socketio.emit('motion_activated', motion.to_dict(), room='telao')
    _emit_motion_update(motion.committee)
    _emit_telao_motions(motion.committee)

    return jsonify({'status': 'success', 'motion': motion.to_dict()})


@motion_bp.route('/admin/mocoes/<int:id>/completar', methods=['POST'])
@login_required
@moderator_required
def motion_complete(id):
    motion = Motion.query.get_or_404(id)
    motion.status = 'completed'
    motion.completed_at = datetime.now(timezone.utc)
    db.session.commit()

    socketio.emit('motion_completed', motion.to_dict(), room='telao')
    _emit_motion_update(motion.committee)
    _emit_telao_motions(motion.committee)

    return jsonify({'status': 'success', 'motion': motion.to_dict()})


@motion_bp.route('/admin/mocoes/<int:id>/notes', methods=['POST'])
@login_required
@moderator_required
def motion_notes(id):
    motion = Motion.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    motion.chair_notes = data.get('notes', '')
    db.session.commit()
    return jsonify({'status': 'success'})


@motion_bp.route('/admin/mocoes/telao', methods=['POST'])
@login_required
@moderator_required
def motion_telao():
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'show')
    committee = data.get('committee', 'all')

    if action == 'show':
        pending = Motion.pending_for_committee(
            committee if committee != 'all' else None
        )
        active = Motion.active_for_committee(
            committee if committee != 'all' else None
        )
        socketio.emit('motion_queue_show', {
            'committee': committee,
            'pending': [m.to_dict() for m in pending],
            'active': active.to_dict() if active else None,
        }, room='telao')
        return jsonify({'status': 'success'})
    else:
        socketio.emit('motion_queue_hide', {}, room='telao')
        return jsonify({'status': 'success'})


# ═══════ STUDENT ROUTES ═══════

@motion_bp.route('/delegado/mocoes')
@login_required
def student_motions():
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        abort(403)

    student = getattr(current_user, 'student', None)
    if not student:
        abort(403)

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation or not delegation.committee:
        abort(403)

    committee = delegation.committee
    pending = Motion.pending_for_committee(committee)
    active = Motion.active_for_committee(committee)
    log = Motion.today_log(committee)

    return render_template('student/motions.html',
                           pending=pending,
                           active=active,
                           log=log,
                           motion_types=MOTION_TYPES,
                           delegation=delegation,
                           committee=committee)


@motion_bp.route('/delegado/mocoes/nova', methods=['POST'])
@login_required
def student_motion_create():
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        return jsonify({'status': 'error', 'message': 'Não autorizado'}), 403

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation or not delegation.committee:
        return jsonify({'status': 'error', 'message': 'Delegação não encontrada'}), 400

    if delegation.presence_status == 'ausente':
        return jsonify({'status': 'error', 'message': 'Você precisa estar presente para propor moções'}), 400

    active = Motion.active_for_committee(delegation.committee)
    if active:
        return jsonify({'status': 'error', 'message': 'Já há uma moção ativa no comitê'}), 400

    data = request.get_json(silent=True) or {}
    motion_type = data.get('motion_type', 'moderated_caucus')
    topic = data.get('topic', '').strip()
    if not topic:
        return jsonify({'status': 'error', 'message': 'Tópico obrigatório'}), 400

    info = MOTION_TYPES.get(motion_type, MOTION_TYPES['other'])
    total_time = int(data.get('total_time', info['default_total']))
    speaking_time = int(data.get('speaking_time', info['default_speaking']))

    motion = Motion(
        proposer_id=delegation.id,
        committee=delegation.committee,
        motion_type=motion_type,
        topic=topic,
        total_time=total_time,
        speaking_time=speaking_time,
        status='pending',
    )
    db.session.add(motion)
    db.session.commit()

    SpeechLog.log(
        delegation_id=delegation.id,
        committee=delegation.committee,
        log_type='motion_proposed',
        topic=topic,
        reference_id=motion.id,
        reference_type='motion',
    )

    _emit_motion_update(delegation.committee)
    _emit_telao_motions(delegation.committee)

    return jsonify({'status': 'success', 'motion': motion.to_dict()})


@motion_bp.route('/delegado/mocoes/<int:id>/secondar', methods=['POST'])
@login_required
def student_motion_second(id):
    if not current_user.is_authenticated or current_user.role not in ('student', 'delegate'):
        return jsonify({'status': 'error', 'message': 'Não autorizado'}), 403

    motion = Motion.query.get_or_404(id)
    if motion.status != 'pending':
        return jsonify({'status': 'error', 'message': 'Moção não está pendente'}), 400

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation:
        return jsonify({'status': 'error', 'message': 'Delegação não encontrada'}), 400

    if motion.proposer_id == delegation.id:
        return jsonify({'status': 'error', 'message': 'Não pode secondar sua própria moção'}), 400

    if motion.seconded_by_id:
        return jsonify({'status': 'error', 'message': 'Moção já possui seconding'}), 400

    motion.seconded_by_id = delegation.id
    db.session.commit()

    SpeechLog.log(
        delegation_id=delegation.id,
        committee=delegation.committee,
        log_type='motion_seconded',
        topic=motion.topic,
        reference_id=motion.id,
        reference_type='motion',
    )

    _emit_motion_update(motion.committee)

    return jsonify({'status': 'success', 'motion': motion.to_dict()})
