from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from routes.admin._helpers import admin_bp, moderator_required
from models.event_config import EventConfig
from extensions import db, socketio


@admin_bp.route('/invocar', methods=['POST'])
@login_required
@moderator_required
def invocar_sessao():
    """Redireciona os alunos ativos para a URL fornecida."""
    from flask import request
    target_url = request.form.get('target_url', '').strip()
    if not target_url:
        flash('A URL de destino é obrigatória para invocar a sessão.', 'error')
        return redirect(url_for('admin.invocar_page'))

    label = request.form.get('label', target_url).strip()
    EventConfig.set_invoke(target_url, label)

    socketio.emit('invoke_session', {'url': target_url, 'label': label}, room='all_students')

    flash(f'Alunos invocados para: {label}', 'success')
    return redirect(url_for('admin.invocar_page'))


@admin_bp.route('/invocar/parar', methods=['POST'])
@login_required
@moderator_required
def invocar_parar():
    """Para a invocação ativa."""
    EventConfig.clear_invoke()
    socketio.emit('invoke_clear', {}, room='all_students')
    flash('Invocacao encerrada.', 'info')
    return redirect(url_for('admin.invocar_page'))


@admin_bp.route('/invocar')
@login_required
@moderator_required
def invocar_page():
    """Página dedicada para invocar alunos."""
    active_invoke = EventConfig.get_invoke()
    return render_template('admin/invocar.html', active_invoke=active_invoke)
