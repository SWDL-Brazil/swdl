from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from routes.admin._helpers import admin_bp, moderator_required
from models.delegation import Delegation
from extensions import db, socketio


@admin_bp.route('/chamada')
@login_required
@moderator_required
def chamada_panel():
    """Painel de chamada — admin marca presença de cada delegação."""
    committee_filter = request.args.get('committee', 'all')

    committees_query = db.session.query(Delegation.committee).filter(
        Delegation.committee.isnot(None),
        Delegation.committee != ''
    ).distinct().all()
    available_committees = sorted([c[0] for c in committees_query])

    q = Delegation.query
    if committee_filter != 'all':
        q = q.filter_by(committee=committee_filter)
    delegations = q.order_by(Delegation.country).all()

    return render_template('admin/chamada.html',
                           delegations=delegations,
                           committee_filter=committee_filter,
                           available_committees=available_committees)


@admin_bp.route('/delegacoes/<int:id>/presenca/<string:status>', methods=['POST'])
@login_required
@moderator_required
def set_presence(id, status):
    """AJAX — atualiza presença e emite via WebSocket para o telão."""
    allowed = ('ausente', 'presente', 'votante')
    if status not in allowed:
        return jsonify({'status': 'error', 'message': 'Status inválido'}), 400

    deleg = Delegation.query.get_or_404(id)
    deleg.presence_status = status
    db.session.commit()

    socketio.emit('chamada_update', {
        'id':         deleg.id,
        'country':    deleg.country or '?',
        'flag':       deleg.country_flag or '',
        'flag_url':   deleg.flag_url or '',
        'committee':  deleg.committee or '',
        'status':     status,
    }, room='telao')

    return jsonify({'status': 'success', 'presence': status})


@admin_bp.route('/chamada/telao', methods=['POST'])
@login_required
@moderator_required
def chamada_control_screen():
    """Controla exibição da chamada no telão público."""
    data   = request.get_json(silent=True) or {}
    action = data.get('action', 'show')

    if action == 'show':
        committee_filter = data.get('committee', 'all')
        q = Delegation.query
        if committee_filter != 'all':
            q = q.filter_by(committee=committee_filter)
        delegations = q.order_by(Delegation.country).all()

        payload = {
            'committee': committee_filter,
            'delegations': [{
                'id':         d.id,
                'country':    d.country or '?',
                'flag':       d.country_flag or '',
                'flag_url':   d.flag_url or '',
                'committee':  d.committee or '',
                'status':     d.presence_status or 'ausente',
            } for d in delegations],
        }
        socketio.emit('chamada_show', payload, room='telao')
    else:
        socketio.emit('chamada_hide', {}, room='telao')

    return jsonify({'status': 'success', 'action': action})
