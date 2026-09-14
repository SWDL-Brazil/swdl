from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, moderator_required
from models.speaker import SpeakerEntry
from models.delegation import Delegation
from extensions import db, socketio


@admin_bp.route('/oradores')
@login_required
@moderator_required
def oradores_panel():
    """Painel para admin selecionar oradores."""
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

    return render_template('admin/oradores.html',
                           delegations=delegations,
                           committee_filter=committee_filter,
                           available_committees=available_committees)


@admin_bp.route('/oradores/toggle', methods=['POST'])
@login_required
@moderator_required
def oradores_toggle():
    """AJAX — adiciona/remove delegacao da lista de oradores."""
    data = request.get_json(silent=True) or {}
    deleg_id = data.get('id')
    if not deleg_id:
        return jsonify({'status': 'error', 'message': 'ID obrigatório'}), 400

    deleg = Delegation.query.get(deleg_id)
    if not deleg:
        return jsonify({'status': 'error', 'message': 'Delegação não encontrada'}), 404

    deleg.orador = not deleg.orador
    db.session.commit()

    orador_payload = {
        'id':        deleg.id,
        'country':   deleg.country or '?',
        'flag':      deleg.country_flag or '',
        'flag_url':  deleg.flag_url or '',
        'committee': deleg.committee or '',
    }
    socketio.emit('oradores_toggle', {
        'orador': deleg.orador,
        'delegacao': orador_payload,
    }, room='telao')

    return jsonify({
        'status': 'success',
        'orador': deleg.orador,
        'id': deleg.id,
        'country': deleg.country,
        'flag': deleg.country_flag or '',
        'flag_url': deleg.flag_url or '',
        'committee': deleg.committee or '',
    })


@admin_bp.route('/oradores/telao', methods=['POST'])
@login_required
@moderator_required
def oradores_control_screen():
    """Controla exibição da lista de oradores no telão."""
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'show')
    current_app.logger.debug(f'[ORADORES] Controle telao: action={action} (por {current_user.email})')

    if action == 'show':
        committee_filter = data.get('committee', 'all')
        q = Delegation.query.filter(Delegation.orador == True)
        if committee_filter != 'all':
            q = q.filter_by(committee=committee_filter)
        oradores = q.order_by(Delegation.country).all()

        payload = {
            'committee': committee_filter,
            'oradores': [{
                'id':        d.id,
                'country':   d.country or '?',
                'flag':      d.country_flag or '',
                'flag_url':  d.flag_url or '',
                'committee': d.committee or '',
            } for d in oradores],
        }
        socketio.emit('oradores_show', payload, room='telao')
    else:
        socketio.emit('oradores_hide', {}, room='telao')

    return jsonify({'status': 'success', 'action': action})
