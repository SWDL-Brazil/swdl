from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required
from models.agenda import AgendaItem
from models.theme import Theme
from models.event_period import EventPeriod
from extensions import db, socketio


@admin_bp.route('/agenda')
@login_required
@admin_required
def agenda_list():
    items = AgendaItem.query.order_by(
        AgendaItem.event_date, AgendaItem.day, AgendaItem.order,
        AgendaItem.start_time).all()
    periods = EventPeriod.query.order_by(EventPeriod.order).all()
    return render_template('admin/agenda_list.html', items=items, periods=periods)


@admin_bp.route('/agenda/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def agenda_create():
    if request.method == 'POST':
        item = AgendaItem(
            day         = int(request.form.get('day', 1)),
            event_date  = request.form.get('event_date', ''),
            start_time  = request.form['start_time'],
            end_time    = request.form.get('end_time', ''),
            title       = request.form['title'],
            description = request.form.get('description', ''),
            location    = request.form.get('location', ''),
            status      = request.form.get('status', 'auto'),
            committee   = request.form.get('committee', ''),
            order       = int(request.form.get('order', 0)),
            period_id   = int(request.form['period_id']) if request.form.get('period_id') else None,
        )
        db.session.add(item)
        db.session.commit()
        flash('Item de agenda adicionado!', 'success')
        return redirect(url_for('admin.agenda_list'))
    themes = Theme.query.order_by(Theme.name).all()
    periods = EventPeriod.query.order_by(EventPeriod.order).all()
    return render_template('admin/agenda_form.html', item=None, themes=themes, periods=periods)


@admin_bp.route('/agenda/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def agenda_edit(id):
    item = AgendaItem.query.get_or_404(id)
    if request.method == 'POST':
        item.day         = int(request.form.get('day', 1))
        item.event_date  = request.form.get('event_date', '')
        item.start_time  = request.form['start_time']
        item.end_time    = request.form.get('end_time', '')
        item.title       = request.form['title']
        item.description = request.form.get('description', '')
        item.location    = request.form.get('location', '')
        item.status      = request.form.get('status', 'auto')
        item.committee   = request.form.get('committee', '')
        item.order       = int(request.form.get('order', 0))
        item.period_id   = int(request.form['period_id']) if request.form.get('period_id') else None
        db.session.commit()
        flash('Agenda atualizada.', 'success')
        return redirect(url_for('admin.agenda_list'))
    themes = Theme.query.order_by(Theme.name).all()
    periods = EventPeriod.query.order_by(EventPeriod.order).all()
    return render_template('admin/agenda_form.html', item=item, themes=themes, periods=periods)


@admin_bp.route('/agenda/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def agenda_delete(id):
    item = AgendaItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item removido.', 'info')
    return redirect(url_for('admin.agenda_list'))


@admin_bp.route('/agenda/<int:id>/status/<string:status>', methods=['POST'])
@login_required
@admin_required
def agenda_set_status(id, status):
    """Muda status de um item rapidamente (ex: marcar como 'now')."""
    allowed = ('now', 'next', 'done', 'break', 'vote', 'crisis', 'open')
    if status not in allowed:
        abort(400)
    # Se marcando como 'now', remove 'now' dos outros
    if status == 'now':
        AgendaItem.query.filter_by(status='now').update({'status': 'done'})
    item = AgendaItem.query.get_or_404(id)
    item.status = status
    db.session.commit()
    flash(f'Status atualizado para "{status}".', 'success')
    return redirect(url_for('admin.agenda_list'))


@admin_bp.route('/agenda/reorder', methods=['POST'])
@login_required
@admin_required
def agenda_reorder():
    """Reordena itens da agenda via drag-and-drop (Sortable.js)."""
    data = request.get_json()
    if not data or 'items' not in data:
        return jsonify({'error': 'missing items'}), 400
    for entry in data['items']:
        item = AgendaItem.query.get(entry.get('id'))
        if item:
            item.order = entry.get('order', item.order)
    db.session.commit()
    return jsonify({'ok': True})
