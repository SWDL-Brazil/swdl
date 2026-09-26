# =============================================================
#  SWDL — Funções compartilhadas de agenda
# =============================================================
from datetime import datetime, timezone

# TTL do cache de processo: a fase muda com o tempo (e não a cada request).
# Cada query paga ~180ms de latência em produção — ver Fase 0.
_CACHE_TTL = 10.0


def get_agenda_status():
    """Retorna (phase, first_dt, last_dt) baseado nos itens de agenda.
    phase: 'pre', 'during', 'post' ou None.
    Memoizado por request (flask.g) e por processo (perf_cache)."""
    from flask import g
    if hasattr(g, '_agenda_status'):
        return g._agenda_status

    from perf_cache import cache_get, cache_set
    cached = cache_get('agenda_status', ttl=_CACHE_TTL)
    if cached is not None:
        g._agenda_status = cached
        return cached

    from models.agenda import AgendaItem
    base_q = AgendaItem.query.filter(
        AgendaItem.event_date.isnot(None),
        AgendaItem.start_time.isnot(None)
    )
    first = base_q.order_by(AgendaItem.event_date, AgendaItem.start_time).limit(1).first()
    last  = base_q.order_by(AgendaItem.event_date.desc(), AgendaItem.start_time.desc()).limit(1).first()
    if not first:
        g._agenda_status = (None, None, None)
        cache_set('agenda_status', g._agenda_status, ttl=_CACHE_TTL)
        return g._agenda_status
    try:
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
    cache_set('agenda_status', g._agenda_status, ttl=_CACHE_TTL)
    return g._agenda_status


def get_agenda_bounds():
    """Retorna (first_dt, last_dt) sem fase. Memoizado por request."""
    phase, first_dt, last_dt = get_agenda_status()
    return first_dt, last_dt
