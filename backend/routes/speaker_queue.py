# =============================================================
#  SWDL — routes/speaker_queue.py
#  Fila de oradores com tracking de discursos
# =============================================================
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify)
from flask_login import login_required, current_user
from extensions import db, socketio
from models.delegation import Delegation
from models.speaker import SpeakerEntry
from models.speech_log import SpeechLog
from datetime import datetime, timezone

speaker_bp = Blueprint('speaker', __name__)


def moderator_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def _emit_queue_update(committee=None):
    queue = SpeakerEntry.current_queue(committee)
    payload = {
        'committee': committee or 'all',
        'queue': [e.to_dict() for e in queue],
    }
    socketio.emit('speaker_queue_updated', payload, room='admin')


def _emit_telao_queue(committee=None):
    queue = SpeakerEntry.current_queue(committee)
    active = SpeakerEntry.active_speaker(committee)
    payload = {
        'committee': committee or 'all',
        'queue': [e.to_dict() for e in queue],
        'active': active.to_dict() if active else None,
    }
    socketio.emit('speaker_queue_display', payload, room='telao')


@speaker_bp.route('/admin/speaker-queue')
@login_required
@moderator_required
def speaker_queue_panel():
    committee_filter = request.args.get('committee', 'all')

    committees_query = db.session.query(Delegation.committee).filter(
        Delegation.committee.isnot(None),
        Delegation.committee != ''
    ).distinct().all()
    available_committees = sorted([c[0] for c in committees_query])

    queue = SpeakerEntry.current_queue(
        committee_filter if committee_filter != 'all' else None
    )
    active = SpeakerEntry.active_speaker(
        committee_filter if committee_filter != 'all' else None
    )
    log = SpeakerEntry.today_log(
        committee_filter if committee_filter != 'all' else None
    )

    delegations = Delegation.query.filter_by(presence_status='votante')
    if committee_filter != 'all':
        delegations = delegations.filter_by(committee=committee_filter)
    delegations = delegations.order_by(Delegation.country).all()

    return render_template('admin/speaker_queue.html',
                           queue=queue,
                           active=active,
                           log=log,
                           delegations=delegations,
                           committee_filter=committee_filter,
                           available_committees=available_committees)


@speaker_bp.route('/admin/speaker-queue/add', methods=['POST'])
@login_required
@moderator_required
def speaker_queue_add():
    data = request.get_json(silent=True) or {}
    deleg_id = data.get('delegation_id')
    speaking_time = int(data.get('speaking_time', 60))
    topic = data.get('topic', '')

    if not deleg_id:
        return jsonify({'status': 'error', 'message': 'Delegação obrigatória'}), 400

    deleg = Delegation.query.get(deleg_id)
    if not deleg:
        return jsonify({'status': 'error', 'message': 'Delegação não encontrada'}), 404

    active = SpeakerEntry.active_speaker(deleg.committee)
    if active:
        return jsonify({'status': 'error', 'message': 'Já há um orador ativo neste comitê'}), 400

    last = SpeakerEntry.query.filter_by(
        committee=deleg.committee, status='pending'
    ).order_by(SpeakerEntry.position.desc()).first()
    next_pos = (last.position + 1) if last else 1

    entry = SpeakerEntry(
        delegation_id=deleg.id,
        committee=deleg.committee,
        topic=topic,
        speaking_time=speaking_time,
        position=next_pos,
        status='pending',
    )
    db.session.add(entry)
    db.session.commit()

    _emit_queue_update(deleg.committee)
    _emit_telao_queue(deleg.committee)

    return jsonify({'status': 'success', 'entry': entry.to_dict()})


@speaker_bp.route('/admin/speaker-queue/reorder', methods=['POST'])
@login_required
@moderator_required
def speaker_queue_reorder():
    data = request.get_json(silent=True) or {}
    order = data.get('order', [])
    committee = data.get('committee', 'all')

    for i, entry_id in enumerate(order):
        entry = SpeakerEntry.query.get(entry_id)
        if entry and entry.status == 'pending':
            entry.position = i + 1

    db.session.commit()
    _emit_queue_update(committee if committee != 'all' else None)
    _emit_telao_queue(committee if committee != 'all' else None)

    return jsonify({'status': 'success'})


@speaker_bp.route('/admin/speaker-queue/<int:id>/start', methods=['POST'])
@login_required
@moderator_required
def speaker_queue_start(id):
    entry = SpeakerEntry.query.get_or_404(id)

    current_active = SpeakerEntry.active_speaker(entry.committee)
    if current_active and current_active.id != id:
        return jsonify({'status': 'error', 'message': 'Já há um orador ativo'}), 400

    entry.status = 'speaking'
    entry.started_at = datetime.now(timezone.utc)
    db.session.commit()

    socketio.emit('speech_timer_start', {'duration': entry.speaking_time}, room='telao')
    socketio.emit('speaker_started', entry.to_dict(), room='telao')
    _emit_queue_update(entry.committee)
    _emit_telao_queue(entry.committee)

    return jsonify({'status': 'success', 'entry': entry.to_dict()})


@speaker_bp.route('/admin/speaker-queue/<int:id>/skip', methods=['POST'])
@login_required
@moderator_required
def speaker_queue_skip(id):
    entry = SpeakerEntry.query.get_or_404(id)
    entry.status = 'skipped'
    entry.ended_at = datetime.now(timezone.utc)
    db.session.commit()

    _emit_queue_update(entry.committee)
    _emit_telao_queue(entry.committee)

    return jsonify({'status': 'success', 'entry': entry.to_dict()})


@speaker_bp.route('/admin/speaker-queue/<int:id>/end', methods=['POST'])
@login_required
@moderator_required
def speaker_queue_end(id):
    entry = SpeakerEntry.query.get_or_404(id)
    entry.status = 'done'
    entry.ended_at = datetime.now(timezone.utc)
    if entry.started_at:
        delta = entry.ended_at - entry.started_at
        entry.duration_used = int(delta.total_seconds())

    SpeechLog.log(
        delegation_id=entry.delegation_id,
        committee=entry.committee,
        log_type='speech',
        duration_sec=entry.duration_used,
        topic=entry.topic,
    )

    db.session.commit()

    socketio.emit('speech_timer_stop', {}, room='telao')
    socketio.emit('speaker_ended', entry.to_dict(), room='telao')
    _emit_queue_update(entry.committee)
    _emit_telao_queue(entry.committee)

    return jsonify({'status': 'success', 'entry': entry.to_dict()})


@speaker_bp.route('/admin/speaker-queue/<int:id>/start-next', methods=['POST'])
@login_required
@moderator_required
def speaker_queue_start_next(id):
    entry = SpeakerEntry.query.get_or_404(id)

    entry.status = 'done'
    entry.ended_at = datetime.now(timezone.utc)
    if entry.started_at:
        delta = entry.ended_at - entry.started_at
        entry.duration_used = int(delta.total_seconds())

    next_entry = SpeakerEntry.query.filter_by(
        committee=entry.committee, status='pending'
    ).order_by(SpeakerEntry.position).first()

    db.session.commit()

    if next_entry:
        next_entry.status = 'speaking'
        next_entry.started_at = datetime.now(timezone.utc)
        db.session.commit()

        socketio.emit('speech_timer_start', {'duration': next_entry.speaking_time}, room='telao')
        socketio.emit('speaker_started', next_entry.to_dict(), room='telao')

    _emit_queue_update(entry.committee)
    _emit_telao_queue(entry.committee)

    return jsonify({
        'status': 'success',
        'finished': entry.to_dict(),
        'next': next_entry.to_dict() if next_entry else None,
    })


@speaker_bp.route('/admin/speaker-queue/clear', methods=['POST'])
@login_required
@moderator_required
def speaker_queue_clear():
    data = request.get_json(silent=True) or {}
    committee = data.get('committee', 'all')

    q = SpeakerEntry.query.filter_by(status='pending')
    if committee and committee != 'all':
        q = q.filter_by(committee=committee)
    count = q.delete(synchronize_session=False)
    db.session.commit()

    _emit_queue_update(committee if committee != 'all' else None)
    _emit_telao_queue(committee if committee != 'all' else None)

    return jsonify({'status': 'success', 'removed': count})


@speaker_bp.route('/admin/speaker-queue/telao', methods=['POST'])
@login_required
@moderator_required
def speaker_queue_telao():
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'show')
    committee = data.get('committee', 'all')

    if action == 'show':
        queue = SpeakerEntry.current_queue(
            committee if committee != 'all' else None
        )
        active = SpeakerEntry.active_speaker(
            committee if committee != 'all' else None
        )
        socketio.emit('speaker_queue_show', {
            'committee': committee,
            'queue': [e.to_dict() for e in queue],
            'active': active.to_dict() if active else None,
        }, room='telao')
        return jsonify({'status': 'success'})
    else:
        socketio.emit('speaker_queue_hide', {}, room='telao')
        return jsonify({'status': 'success'})


def _handle_speaker_timer_expired(entry_id):
    entry = SpeakerEntry.query.get(entry_id)
    if entry and entry.status == 'speaking':
        entry.status = 'done'
        entry.ended_at = datetime.now(timezone.utc)
        entry.duration_used = entry.speaking_time
        db.session.commit()

        socketio.emit('speaker_ended', entry.to_dict(), room='telao')
        _emit_queue_update(entry.committee)
        _emit_telao_queue(entry.committee)
