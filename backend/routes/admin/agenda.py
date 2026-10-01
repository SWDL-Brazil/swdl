import logging
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required
from models.agenda import AgendaItem
from models.theme import Theme
from models.event_period import EventPeriod
from extensions import db
from perf_cache import cache_clear

logger = logging.getLogger(__name__)


def _valid_date(s):
    """AAAA-MM-DD (aceita também AAAA-MM-DDTHH:MM:SS de inputs date+time)."""
    try:
        datetime.strptime(s or '', '%Y-%m-%d')
        return True
    except ValueError:
        return False


def _valid_time(s, required=False):
    """HH:MM ou HH:MM:SS; opcional salvo quando required=True."""
    if not s:
        return not required
    try:
        datetime.strptime(s, '%H:%M')
        return True
    except ValueError:
        pass
    try:
        datetime.strptime(s, '%H:%M:%S')
        return True
    except ValueError:
        return False


def _next_order(day, period_id):
    """Próximo order dentro do grupo (período → dia) — item novo vai ao fim."""
    from sqlalchemy import func
    q = db.session.query(func.max(AgendaItem.order)).filter(
        AgendaItem.day == day,
        (AgendaItem.period_id == period_id) if period_id
        else AgendaItem.period_id.is_(None),
    )
    return (q.scalar() or 0) + 1


def _validate_form():
    """Valida data/horários do form. Retorna mensagem de erro ou None."""
    event_date = request.form.get('event_date', '')
    start_time = request.form.get('start_time', '')
    end_time   = request.form.get('end_time', '')
    if not _valid_date(event_date):
        return 'Data inválida. Use o formato AAAA-MM-DD.'
    if not _valid_time(start_time, required=True):
        return 'Horário de início inválido. Use HH:MM.'
    if not _valid_time(end_time):
        return 'Horário de término inválido. Use HH:MM.'
    if end_time and start_time and end_time[:5] < start_time[:5]:
        return 'O horário de término deve ser depois do início.'
    return None


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
        err = _validate_form()
        if err:
            flash(err, 'error')
            return redirect(url_for('admin.agenda_create'))
        try:
            period_id_raw = request.form.get('period_id', '')
            day   = int(request.form.get('day', 1))
            period_id = int(period_id_raw) if period_id_raw else None
            item = AgendaItem(
                day         = day,
                event_date  = request.form.get('event_date', ''),
                start_time  = request.form['start_time'],
                end_time    = request.form.get('end_time', ''),
                title       = request.form['title'],
                description = request.form.get('description', ''),
                location    = request.form.get('location', ''),
                status      = request.form.get('status', 'auto'),
                committee   = request.form.get('committee', ''),
                order       = _next_order(day, period_id),
                period_id   = period_id,
            )
            db.session.add(item)
            db.session.commit()
            cache_clear('agenda_status')
            flash('Item de agenda adicionado!', 'success')
            return redirect(url_for('admin.agenda_list'))
        except Exception as e:
            db.session.rollback()
            logger.error('Erro ao criar item de agenda: %s', e, exc_info=True)
            flash(f'Erro ao salvar: {e}', 'error')
            return redirect(url_for('admin.agenda_create'))
    themes = Theme.query.order_by(Theme.name).all()
    periods = EventPeriod.query.order_by(EventPeriod.order).all()
    return render_template('admin/agenda_form.html', item=None, themes=themes, periods=periods)


@admin_bp.route('/agenda/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def agenda_edit(id):
    item = AgendaItem.query.get_or_404(id)
    if request.method == 'POST':
        err = _validate_form()
        if err:
            flash(err, 'error')
            return redirect(url_for('admin.agenda_edit', id=id))
        try:
            period_id_raw = request.form.get('period_id', '')
            item.day         = int(request.form.get('day', 1))
            item.event_date  = request.form.get('event_date', '')
            item.start_time  = request.form['start_time']
            item.end_time    = request.form.get('end_time', '')
            item.title       = request.form['title']
            item.description = request.form.get('description', '')
            item.location    = request.form.get('location', '')
            item.status      = request.form.get('status', 'auto')
            item.committee   = request.form.get('committee', '')
            # O form não tem campo 'order' — preserva o valor do drag-and-drop
            item.period_id   = int(period_id_raw) if period_id_raw else None
            db.session.commit()
            cache_clear('agenda_status')
            flash('Agenda atualizada.', 'success')
            return redirect(url_for('admin.agenda_list'))
        except Exception as e:
            db.session.rollback()
            logger.error('Erro ao editar item de agenda: %s', e, exc_info=True)
            flash(f'Erro ao salvar: {e}', 'error')
            return redirect(url_for('admin.agenda_edit', id=id))
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
    cache_clear('agenda_status')
    flash('Item removido.', 'info')
    return redirect(url_for('admin.agenda_list'))


@admin_bp.route('/agenda/reorder', methods=['POST'])
@login_required
@admin_required
def agenda_reorder():
    """Reordena itens da agenda via drag-and-drop (Sortable.js)."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get('items'), list):
        return jsonify({'error': 'missing items'}), 400
    try:
        entries = [e for e in data['items'] if isinstance(e, dict)]
        ids = [e.get('id') for e in entries]
        # 1 query em vez de 1 get() por item (N+1 ≈ 180ms cada em produção)
        items = {i.id: i for i in
                 AgendaItem.query.filter(AgendaItem.id.in_(ids)).all()}
        for entry in entries:
            item = items.get(entry.get('id'))
            if item and isinstance(entry.get('order'), int):
                item.order = entry['order']
        db.session.commit()
        cache_clear('agenda_status')
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        logger.error('Erro ao reordenar agenda: %s', e, exc_info=True)
        return jsonify({'error': str(e)}), 500
