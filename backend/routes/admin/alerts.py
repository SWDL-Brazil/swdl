"""SWDL Admin — Urgent Alerts (Ticker) routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required
from models.urgent_alert import UrgentAlert
from extensions import db


@admin_bp.route('/alertas')
@login_required
@admin_required
def alerts_list():
    alerts = UrgentAlert.query.order_by(UrgentAlert.created_at.desc()).all()
    return render_template('admin/alerts_list.html', alerts=alerts)


@admin_bp.route('/alertas/criar', methods=['POST'])
@login_required
@admin_required
def alert_create():
    message = request.form.get('message', '').strip()
    if not message:
        flash('A mensagem é obrigatória.', 'error')
        return redirect(url_for('admin.alerts_list'))
    alert = UrgentAlert(message=message, active=True, created_by=current_user.id)
    db.session.add(alert)
    db.session.commit()
    flash('🚨 Alerta urgente ativado!', 'success')
    return redirect(url_for('admin.alerts_list'))


@admin_bp.route('/alertas/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def alert_toggle(id):
    alert = UrgentAlert.query.get_or_404(id)
    alert.active = not alert.active
    db.session.commit()
    flash(f'Alerta {"ativado" if alert.active else "desativado"}.', 'info')
    return redirect(url_for('admin.alerts_list'))


@admin_bp.route('/alertas/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def alert_delete(id):
    alert = UrgentAlert.query.get_or_404(id)
    db.session.delete(alert)
    db.session.commit()
    flash('Alerta removido.', 'info')
    return redirect(url_for('admin.alerts_list'))
