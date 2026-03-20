"""
tests/test_utils.py
~~~~~~~~~~~~~~~~~~~
Tests for roboat utility modules — zero network calls.
"""

import time
import threading
import pytest

from roboat.utils.cache import TTLCache, cached
from roboat.utils.ratelimit import TokenBucket
from roboat.utils.paginator import Paginator
from roboat.models import Page, User


# ── TTLCache ──────────────────────────────────────────────────────────── #

class TestTTLCache:
    def test_set_and_get(self):
        c = TTLCache(default_ttl=60)
        c.set("key", "value")
        assert c.get("key") == "value"

    def test_miss(self):
        c = TTLCache(default_ttl=60)
        assert c.get("nonexistent") is None

    def test_expiry(self):
        c = TTLCache(default_ttl=0.05)
        c.set("key", "value")
        assert c.get("key") == "value"
        time.sleep(0.1)
        assert c.get("key") is None

    def test_delete(self):
        c = TTLCache(default_ttl=60)
        c.set("key", "value")
        c.delete("key")
        assert c.get("key") is None

    def test_clear(self):
        c = TTLCache(default_ttl=60)
        c.set("a", 1)
        c.set("b", 2)
        c.clear()
        assert c.get("a") is None
        assert c.get("b") is None
        assert c.size == 0

    def test_size(self):
        c = TTLCache(default_ttl=60, max_size=10)
        for i in range(5):
            c.set(f"key{i}", i)
        assert c.size == 5

    def test_lru_eviction(self):
        c = TTLCache(default_ttl=60, max_size=3)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)
        c.get("a")  # access a — makes b the LRU
        c.set("d", 4)  # should evict b (LRU)
        assert c.get("a") == 1
        assert c.get("c") == 3
        assert c.get("d") == 4

    def test_custom_ttl(self):
        c = TTLCache(default_ttl=60)
        c.set("short", "value", ttl=0.05)
        assert c.get("short") == "value"
        time.sleep(0.1)
        assert c.get("short") is None

    def test_thread_safety(self):
        c = TTLCache(default_ttl=60, max_size=100)
        errors = []

        def writer(start):
            for i in range(start, start + 20):
                try:
                    c.set(f"key{i}", i)
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=writer, args=(i * 20,)) for i in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()

        assert not errors

    def test_stats(self):
        c = TTLCache(default_ttl=60, max_size=10)
        c.set("a", 1)
        c.set("b", 2)
        s = c.stats()
        assert s["total"] == 2
        assert s["alive"] == 2
        assert s["max_size"] == 10

    def test_overwrite(self):
        c = TTLCache(default_ttl=60)
        c.set("key", "old")
        c.set("key", "new")
        assert c.get("key") == "new"


# ── TokenBucket ───────────────────────────────────────────────────────── #

class TestTokenBucket:
    def test_consume_within_capacity(self):
        b = TokenBucket(rate=100, capacity=10)
        waited = b.consume()
        assert waited == 0.0

    def test_available(self):
        b = TokenBucket(rate=10, capacity=10)
        assert b.available > 0

    def test_multiple_consumes(self):
        b = TokenBucket(rate=100, capacity=5)
        for _ in range(5):
            b.consume()
        # All 5 should succeed immediately (within capacity)
        assert b.available >= 0

    def test_thread_safety(self):
        b = TokenBucket(rate=1000, capacity=100)
        results = []
        lock = threading.Lock()

        def consume_many():
            for _ in range(10):
                w = b.consume()
                with lock:
                    results.append(w)

        threads = [threading.Thread(target=consume_many) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()

        assert len(results) == 50
        assert all(w >= 0 for w in results)


# ── Paginator ─────────────────────────────────────────────────────────── #

class TestPaginator:
    def _make_fetch(self, pages):
        """Create a fake fetch function from a list of (items, next_cursor) tuples."""
        page_map = {}
        cursors = [None] + [f"cursor_{i}" for i in range(len(pages) - 1)]
        for i, (items, _) in enumerate(pages):
            next_c = cursors[i + 1] if i + 1 < len(cursors) else None
            page_map[cursors[i]] = Page(data=items, next_cursor=next_c)

        def fetch(cursor):
            return page_map.get(cursor, Page(data=[]))

        return fetch

    def test_single_page(self):
        fetch = self._make_fetch([([1, 2, 3], None)])
        p = Paginator(fetch)
        assert p.collect() == [1, 2, 3]

    def test_multiple_pages(self):
        fetch = self._make_fetch([
            ([1, 2, 3], "next"),
            ([4, 5, 6], "next2"),
            ([7, 8, 9], None),
        ])
        p = Paginator(fetch)
        assert p.collect() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_max_items(self):
        fetch = self._make_fetch([
            (list(range(10)), "next"),
            (list(range(10, 20)), None),
        ])
        p = Paginator(fetch, max_items=5)
        result = p.collect()
        assert len(result) == 5
        assert result == [0, 1, 2, 3, 4]

    def test_first(self):
        fetch = self._make_fetch([([1, 2, 3, 4, 5], None)])
        p = Paginator(fetch)
        assert p.first(3) == [1, 2, 3]

    def test_first_across_pages(self):
        fetch = self._make_fetch([
            ([1, 2], "next"),
            ([3, 4], "next2"),
            ([5, 6], None),
        ])
        p = Paginator(fetch)
        assert p.first(4) == [1, 2, 3, 4]

    def test_empty_result(self):
        fetch = self._make_fetch([([], None)])
        p = Paginator(fetch)
        assert p.collect() == []

    def test_iteration(self):
        fetch = self._make_fetch([([10, 20, 30], None)])
        p = Paginator(fetch)
        items = [x for x in p]
        assert items == [10, 20, 30]

    def test_max_items_zero(self):
        fetch = self._make_fetch([([1, 2, 3], None)])
        p = Paginator(fetch, max_items=0)
        assert p.collect() == []


# ── @cached decorator ─────────────────────────────────────────────────── #

class TestCachedDecorator:
    def test_caches_result(self):
        call_count = [0]

        class FakeAPI:
            def __init__(self):
                self._c = type("C", (), {"_cache": TTLCache(default_ttl=60)})()

            @cached(ttl=60)
            def fetch(self, x):
                call_count[0] += 1
                return x * 2

        api = FakeAPI()
        assert api.fetch(5) == 10
        assert api.fetch(5) == 10
        assert call_count[0] == 1  # called only once

    def test_different_args_not_cached(self):
        call_count = [0]

        class FakeAPI:
            def __init__(self):
                self._c = type("C", (), {"_cache": TTLCache(default_ttl=60)})()

            @cached(ttl=60)
            def fetch(self, x):
                call_count[0] += 1
                return x * 2

        api = FakeAPI()
        api.fetch(1)
        api.fetch(2)
        assert call_count[0] == 2

    def test_no_cache_attribute(self):
        """If _c has no _cache, function should still work normally."""
        call_count = [0]

        class FakeAPI:
            def __init__(self):
                self._c = object()

            @cached(ttl=60)
            def fetch(self, x):
                call_count[0] += 1
                return x

        api = FakeAPI()
        assert api.fetch(42) == 42
        assert call_count[0] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
