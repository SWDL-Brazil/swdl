# =============================================================
#  SWDL — Funções compartilhadas de agenda
# =============================================================
from datetime import datetime, timezone

# TTL do cache de processo: a fase muda com o tempo (e não a cada request).
# Cada query paga ~180-200ms de latência em produção — ver Fase 0.
# Invalidação: agenda.py limpa 'agenda_status' a cada escrita de item.
_CACHE_TTL = 60.0


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

    from extensions import db
    from models.agenda import AgendaItem
    from sqlalchemy import func, select

    # 1 única query: min(data+início) e max(data+fim) via agregados.
    # Antes eram 2 round-trips (cada um ~180ms de latência em produção).
    start_key = AgendaItem.event_date + ' ' + AgendaItem.start_time
    end_key   = AgendaItem.event_date + ' ' + func.coalesce(AgendaItem.end_time, '23:59')
    first_s, last_s = db.session.execute(
        select(func.min(start_key), func.max(end_key)).where(
            AgendaItem.event_date.isnot(None),
            AgendaItem.start_time.isnot(None),
        )
    ).one()

    if not first_s:
        g._agenda_status = (None, None, None)
        cache_set('agenda_status', g._agenda_status, ttl=_CACHE_TTL)
        return g._agenda_status
    try:
        first_dt = datetime.strptime(first_s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        last_dt  = datetime.strptime(last_s,  "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
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
