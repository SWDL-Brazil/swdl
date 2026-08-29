# =============================================================
#  SWDL — Funções compartilhadas de agenda
# =============================================================
from datetime import datetime, timezone
from models.agenda import AgendaItem


def get_agenda_status():
    """Retorna (phase, first_dt, last_dt) baseado nos itens de agenda.
    phase: 'pre', 'during', 'post' ou None."""
    items = AgendaItem.query.filter(
        AgendaItem.event_date.isnot(None),
        AgendaItem.start_time.isnot(None)
    ).order_by(AgendaItem.event_date, AgendaItem.start_time).all()
    if not items:
        return None, None, None
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
            return 'pre', first_dt, last_dt
        if now > last_dt:
            return 'post', first_dt, last_dt
        return 'during', first_dt, last_dt
    except (ValueError, TypeError):
        return None, None, None
