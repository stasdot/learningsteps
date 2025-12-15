import time
from typing import Any

# simple in-memory cache (process-local)
_CACHE: dict[str, tuple[float, Any]] = {}

DEFAULT_TTL = 60  # seconds


def get_cache(key: str):
    entry = _CACHE.get(key)
    if not entry:
        return None

    expires_at, value = entry
    if time.time() > expires_at:
        _CACHE.pop(key, None)
        return None

    return value


def set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL):
    _CACHE[key] = (time.time() + ttl, value)


def invalidate_cache(prefix: str | None = None):
    if prefix is None:
        _CACHE.clear()
        return

    for key in list(_CACHE.keys()):
        if key.startswith(prefix):
            _CACHE.pop(key, None)
