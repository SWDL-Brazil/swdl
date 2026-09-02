# =============================================================
#  SWDL — Funções compartilhadas de agenda
# =============================================================
from datetime import datetime, timezone


def get_agenda_status():
    """Retorna (phase, first_dt, last_dt) baseado nos itens de agenda.
    phase: 'pre', 'during', 'post' ou None.
    Memoizado por request via flask.g."""
    from flask import g
    if hasattr(g, '_agenda_status'):
        return g._agenda_status

    from models.agenda import AgendaItem
    items = AgendaItem.query.filter(
        AgendaItem.event_date.isnot(None),
        AgendaItem.start_time.isnot(None)
    ).order_by(AgendaItem.event_date, AgendaItem.start_time).all()
    if not items:
        g._agenda_status = (None, None, None)
        return g._agenda_status
    try:
        first = items[0]
        last = items[-1]
        first_dt = datetime.strptime(
            f"{first.event_date} {first.start_time}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=timezone.utc)
        last_end = last.end_time or '23:59'
        last_dt = datetime.strptime(
            f"{last.event_date} {last_end}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if now < first_dt:
            g._agenda_status = ('pre', first_dt, last_dt)
        elif now > last_dt:
            g._agenda_status = ('post', first_dt, last_dt)
        else:
            g._agenda_status = ('during', first_dt, last_dt)
    except (ValueError, TypeError):
        g._agenda_status = (None, None, None)
    return g._agenda_status


def get_agenda_bounds():
    """Retorna (first_dt, last_dt) sem fase. Memoizado por request."""
    phase, first_dt, last_dt = get_agenda_status()
    return first_dt, last_dt
