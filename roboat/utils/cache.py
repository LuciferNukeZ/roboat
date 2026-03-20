"""
roboat.utils.cache
~~~~~~~~~~~~~~~~~~~~~
Simple TTL-based in-memory response cache.
Prevents hammering the API with identical requests.
"""

from __future__ import annotations
import time
import threading
import functools
from typing import Any, Optional, Dict, Tuple


class TTLCache:
    """
    Thread-safe in-memory cache with per-entry TTL.

    Args:
        default_ttl: Default time-to-live in seconds (default: 30s).
        max_size: Max entries before LRU eviction (default: 512).

    Example::

        cache = TTLCache(default_ttl=30)
        cache.set("user:156", user_data)
        value = cache.get("user:156")  # None if expired
    """

    def __init__(self, default_ttl: float = 30.0, max_size: int = 512):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._access: Dict[str, float] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                self._access.pop(key, None)
                return None
            self._access[key] = time.monotonic()
            return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        with self._lock:
            if len(self._store) >= self.max_size:
                self._evict_lru()
            expires_at = time.monotonic() + (ttl if ttl is not None else self.default_ttl)
            self._store[key] = (value, expires_at)
            self._access[key] = time.monotonic()

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)
            self._access.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self._access.clear()

    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._access:
            return
        lru_key = min(self._access, key=self._access.__getitem__)
        self._store.pop(lru_key, None)
        self._access.pop(lru_key, None)

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._store)

    def stats(self) -> dict:
        with self._lock:
            now = time.monotonic()
            alive = sum(1 for _, (_, exp) in self._store.items() if exp > now)
            return {"total": len(self._store), "alive": alive, "max_size": self.max_size}


def cached(ttl: float = 30.0, key_fn: Optional[Any] = None):
    """
    Method decorator: cache the result for `ttl` seconds.
    Uses the instance's ``_cache`` attribute (a TTLCache).

    Args:
        ttl: Cache lifetime in seconds.
        key_fn: Optional callable(args, kwargs) → str for custom key.

    Example::

        class UsersAPI:
            @cached(ttl=60)
            def get_user(self, user_id):
                ...
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(self_or_cls, *args, **kwargs):
            cache: Optional[TTLCache] = getattr(
                getattr(self_or_cls, "_c", self_or_cls), "_cache", None
            )
            if cache is None:
                return fn(self_or_cls, *args, **kwargs)
            if key_fn:
                cache_key = key_fn(args, kwargs)
            else:
                cache_key = f"{fn.__qualname__}:{args}:{sorted(kwargs.items())}"
            hit = cache.get(cache_key)
            if hit is not None:
                return hit
            result = fn(self_or_cls, *args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
