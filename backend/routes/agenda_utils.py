# =============================================================
#  SWDL — Funções compartilhadas de agenda
# =============================================================
from datetime import datetime, date, timezone

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


def get_resolved_phase():
    """Fase efetiva do evento: cálculo da agenda (ou 'pre') + override manual.

    É a ÚNICA fonte de fase — o context processor e os dashboards usam esta
    função, assim o switcher 🟢/🔴/🔵 do admin vale em todas as telas.
    Retorna (phase, first_dt, last_dt)."""
    phase, first_dt, last_dt = get_agenda_status()
    phase = phase or 'pre'
    from models.event_config import EventConfig
    override = EventConfig.get_state()['phase_override']
    if override in ('pre', 'during', 'post'):
        phase = override
    return phase, first_dt, last_dt


def get_current_next():
    """Retorna (current, next) derivados do horário — card 'AO VIVO'/'Agora'.

    Substitui os filtros por status='now'/'next', que nunca são gravados no
    banco (a rota que os gravava foi removida). Status manual tem precedência;
    senão calcula pela hora local (mesma regra do antigo fallback da API).
    Memoizado por request (flask.g) — muda a cada minuto, então não entra no
    cache de processo."""
    from flask import g
    if hasattr(g, '_agenda_current_next'):
        return g._agenda_current_next

    from models.agenda import AgendaItem

    current   = AgendaItem.query.filter_by(status='now').first()
    next_item = AgendaItem.query.filter_by(status='next')\
                                .order_by(AgendaItem.order).first()
    if not current or not next_item:
        today   = date.today().isoformat()
        now_str = datetime.now().strftime('%H:%M')
        rows = AgendaItem.query.filter(
            AgendaItem.event_date == today
        ).order_by(AgendaItem.start_time, AgendaItem.order).all()
        for c in rows:
            start = c.start_time or '00:00'
            end   = c.end_time   or '23:59'
            if current is None and start <= now_str < end:
                current = c
            elif next_item is None and start > now_str:
                next_item = c

    g._agenda_current_next = (current, next_item)
    return g._agenda_current_next
