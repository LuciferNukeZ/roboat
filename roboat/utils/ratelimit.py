"""
roboat.utils.ratelimit
~~~~~~~~~~~~~~~~~~~~~~~~~
Token-bucket rate limiter + exponential backoff retry decorator.
Prevents 429s before they happen and recovers from them automatically.
"""

from __future__ import annotations
import time
import threading
import functools
from typing import Callable, Optional


class TokenBucket:
    """
    Thread-safe token bucket for rate limiting.

    Args:
        rate: Tokens replenished per second.
        capacity: Maximum burst size.

    Example::

        bucket = TokenBucket(rate=10, capacity=20)
        bucket.consume()  # blocks if empty
    """

    def __init__(self, rate: float = 10.0, capacity: float = 20.0):
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def consume(self, tokens: float = 1.0) -> float:
        """
        Consume tokens, blocking until available.
        Returns the time waited in seconds.
        """
        waited = 0.0
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last
                self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
                self._last = now
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return waited
            sleep_for = (tokens - self._tokens) / self.rate
            time.sleep(sleep_for)
            waited += sleep_for

    @property
    def available(self) -> float:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            return min(self.capacity, self._tokens + elapsed * self.rate)


def retry(
    max_attempts: int = 3,
    backoff: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (),
) -> Callable:
    """
    Decorator: retry a function with exponential backoff.

    Args:
        max_attempts: Maximum number of tries.
        backoff: Initial wait in seconds.
        backoff_factor: Multiplier applied each retry.
        exceptions: Exception types to retry on (default: RateLimitedError).

    Example::

        @retry(max_attempts=3, backoff=1.0)
        def fetch():
            return client.users.get_user(123)
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            from roboat.exceptions import RateLimitedError
            catch = exceptions or (RateLimitedError,)
            delay = backoff
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except catch as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        delay *= backoff_factor
            raise last_exc
        return wrapper
    return decorator
