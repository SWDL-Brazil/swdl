"""Server-side debate timer state (in-memory, synced via Socket.IO)."""
import time

_state = {
    'start': 0.0,       # epoch when current run started
    'accumulated': 0.0,  # seconds accumulated before current run
    'running': False,
}


def get_state():
    """Return current elapsed seconds and running flag."""
    if _state['running']:
        elapsed = _state['accumulated'] + (time.time() - _state['start'])
    else:
        elapsed = _state['accumulated']
    return {'elapsed': int(elapsed), 'running': _state['running']}


def start():
    if not _state['running']:
        _state['start'] = time.time()
        _state['running'] = True
    return get_state()


def pause():
    if _state['running']:
        _state['accumulated'] += time.time() - _state['start']
        _state['running'] = False
    return get_state()


def reset():
    _state['start'] = 0.0
    _state['accumulated'] = 0.0
    _state['running'] = False
    return get_state()
