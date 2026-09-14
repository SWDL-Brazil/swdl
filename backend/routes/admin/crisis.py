from flask import redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required
from models.event_config import EventConfig
from models.urgent_alert import UrgentAlert
from extensions import db, socketio


@admin_bp.route('/crise/ativar', methods=['POST'])
@login_required
@admin_required
def crisis_activate():
    message = request.form.get('message', 'Crise diplomática ativada.')
    alert = UrgentAlert(message=message, active=True, created_by=current_user.id)
    db.session.add(alert)
    db.session.commit()
    socketio.emit('urgent_alert', alert.to_dict(), namespace='/')
    flash(f'Banner de crise ativado: "{message}"', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/crise/desativar', methods=['POST'])
@login_required
@admin_required
def crisis_deactivate():
    UrgentAlert.query.filter_by(active=True).update({'active': False})
    db.session.commit()
    socketio.emit('urgent_alert_hide', {}, namespace='/')
    flash('Banner de crise desativado.', 'info')
    return redirect(url_for('admin.dashboard'))
