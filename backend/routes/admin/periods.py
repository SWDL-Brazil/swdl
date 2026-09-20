from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required
from models.event_period import EventPeriod
from extensions import db


@admin_bp.route('/periods')
@login_required
@admin_required
def periods_list():
    periods = EventPeriod.query.order_by(EventPeriod.order, EventPeriod.start_date).all()
    return render_template('admin/periods_list.html', periods=periods)


@admin_bp.route('/periods/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def period_create():
    if request.method == 'POST':
        period = EventPeriod(
            name       = request.form['name'],
            start_date = request.form['start_date'],
            end_date   = request.form['end_date'],
            order      = int(request.form.get('order', 0)),
            color      = request.form.get('color', 'navy'),
        )
        db.session.add(period)
        db.session.commit()
        flash('Período adicionado!', 'success')
        return redirect(url_for('admin.periods_list'))
    return render_template('admin/period_form.html', period=None)


@admin_bp.route('/periods/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def period_edit(id):
    period = EventPeriod.query.get_or_404(id)
    if request.method == 'POST':
        period.name       = request.form['name']
        period.start_date = request.form['start_date']
        period.end_date   = request.form['end_date']
        period.order      = int(request.form.get('order', 0))
        period.color      = request.form.get('color', 'navy')
        db.session.commit()
        flash('Período atualizado.', 'success')
        return redirect(url_for('admin.periods_list'))
    return render_template('admin/period_form.html', period=period)


@admin_bp.route('/periods/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def period_delete(id):
    period = EventPeriod.query.get_or_404(id)
    db.session.delete(period)
    db.session.commit()
    flash('Período removido.', 'info')
    return redirect(url_for('admin.periods_list'))
