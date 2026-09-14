from flask import render_template
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, moderator_required
from extensions import socketio


@admin_bp.route('/cronometro')
@login_required
@moderator_required
def cronometro_panel():
    """Painel de controle do cronômetro de oratória."""
    return render_template('admin/cronometro.html')


@socketio.on('admin_timer_start')
def on_admin_timer_start(data):
    if not current_user.is_authenticated or not current_user.is_moderator():
        return
    duration = int((data or {}).get('duration', 90))
    socketio.emit('speech_timer_start', {'duration': duration}, room='telao')


@socketio.on('admin_timer_stop')
def on_admin_timer_stop(data):
    if not current_user.is_authenticated or not current_user.is_moderator():
        return
    socketio.emit('speech_timer_stop', {}, room='telao')


@socketio.on('admin_timer_reset')
def on_admin_timer_reset(data):
    if not current_user.is_authenticated or not current_user.is_moderator():
        return
    socketio.emit('speech_timer_reset', {}, room='telao')
