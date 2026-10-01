"""Server-side debate timer state (persisted in SystemConfig).

Antes era in-memory: reiniciar o worker (deploy/reboot) zerava o cronometro
do debate e o telao voltava para 00:00. Agora o estado mora no banco
(`debate_timer`) com `start` em epoch, entao mesmo um restart com o cronometro
rodando continua contando corretamente.
"""
import json
import time

KEY = 'debate_timer'
_state = {'start': 0.0, 'accumulated': 0.0, 'running': False}


def _load():
    """Le o estado persistido (cache de processo de 30s via SystemConfig)."""
    try:
        from models.system_config import SystemConfig
        raw = SystemConfig.get(KEY)
        data = json.loads(raw) if raw else None
    except Exception:
        data = None
    if isinstance(data, dict):
        _state['start'] = float(data.get('start') or 0.0)
        _state['accumulated'] = float(data.get('accumulated') or 0.0)
        _state['running'] = bool(data.get('running'))
    return _state


def _save():
    try:
        from models.system_config import SystemConfig
        SystemConfig.set(KEY, json.dumps(_state))
    except Exception:
        # Sem app/db context (ou DB fora do ar) o timer segue em memoria.
        pass


def get_state():
    """Return current elapsed seconds and running flag."""
    st = _load()
    if st['running']:
        elapsed = st['accumulated'] + (time.time() - st['start'])
    else:
        elapsed = st['accumulated']
    return {'elapsed': int(elapsed), 'running': st['running']}


def start():
    st = _load()
    if not st['running']:
        st['start'] = time.time()
        st['running'] = True
        _save()
    return get_state()


def pause():
    st = _load()
    if st['running']:
        st['accumulated'] += time.time() - st['start']
        st['running'] = False
        _save()
    return get_state()


def reset():
    st = _load()
    st['start'] = 0.0
    st['accumulated'] = 0.0
    st['running'] = False
    _save()
    return get_state()
