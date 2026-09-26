"""Cache de processo para valores lidos do banco.

Motivação: em produção cada round-trip ao banco custa ~180ms (latência de
rede medida na Fase 0), então valores que mudam pouco (fase do evento,
config, alertas, status da agenda) são cacheados em memória por N segundos.

Uso:
    from perf_cache import cache_get, cache_set, cache_clear
    v = cache_get('chave', ttl=10)
    if v is None:
        v = carregar_do_banco()
        cache_set('chave', v, ttl=10)

Nunca guarde objetos ORM vivos (podem ficar detached e estourar ao acessar
atributo) — guarde strings, tuplas, listas de strings ou dicts.
"""
import time
from threading import Lock

_store = {}
_lock = Lock()
DEFAULT_TTL = 10.0


def cache_get(key, ttl=DEFAULT_TTL):
    """Retorna o valor cacheado ou None se ausente/expirado."""
    with _lock:
        hit = _store.get(key)
        if hit is None:
            return None
        expires_at, value = hit
        if time.monotonic() > expires_at:
            _store.pop(key, None)
            return None
        return value


def cache_set(key, value, ttl=DEFAULT_TTL):
    with _lock:
        _store[key] = (time.monotonic() + ttl, value)


def cache_clear(prefix=''):
    """Limpa tudo (prefixo='') ou só as chaves que começam com o prefixo."""
    with _lock:
        if not prefix:
            _store.clear()
            return
        for k in [k for k in _store if k.startswith(prefix)]:
            _store.pop(k, None)
