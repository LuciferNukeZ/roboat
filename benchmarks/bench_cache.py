"""
benchmarks/bench_cache.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Performance benchmarks for the TTLCache implementation.
Measures throughput under concurrent reads/writes.

Run: python benchmarks/bench_cache.py
"""

import time
import threading
import statistics
from roboat.utils.cache import TTLCache


def bench(label: str, fn, iterations: int = 10_000) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter() - start
    ops_per_sec = iterations / elapsed
    print(f"  {label:<40} {ops_per_sec:>12,.0f} ops/sec  ({elapsed*1000:.1f}ms total)")
    return ops_per_sec


def bench_sequential():
    print("\n── Sequential ─────────────────────────────────────────")
    cache = TTLCache(default_ttl=60, max_size=1000)

    bench("set (new keys)", lambda: cache.set(f"key_{time.time()}", "v"))
    bench("set (same key)", lambda: cache.set("constant", "value"))
    bench("get (hit)",      lambda: cache.get("constant"))
    bench("get (miss)",     lambda: cache.get("nonexistent_key_xyz"))
    bench("set+get cycle",  lambda: (cache.set("cycle", 1), cache.get("cycle")))


def bench_concurrent():
    print("\n── Concurrent (8 threads) ─────────────────────────────")
    cache = TTLCache(default_ttl=60, max_size=500)
    iterations = 5_000
    results = []

    def worker():
        start = time.perf_counter()
        for i in range(iterations):
            cache.set(f"t_{threading.get_ident()}_{i}", i)
            cache.get(f"t_{threading.get_ident()}_{i}")
        results.append(time.perf_counter() - start)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    start = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    total = time.perf_counter() - start

    total_ops = 8 * iterations * 2
    print(f"  {'8 threads × 5000 set+get':<40} {total_ops/total:>12,.0f} ops/sec  ({total*1000:.1f}ms total)")


def bench_eviction():
    print("\n── Eviction (max_size=100) ────────────────────────────")
    cache = TTLCache(default_ttl=60, max_size=100)
    # Fill cache
    for i in range(100):
        cache.set(f"k{i}", i)

    def evict_cycle():
        cache.set(f"new_{time.monotonic()}", "v")

    bench("eviction trigger", evict_cycle, iterations=1000)


def bench_ttl_expiry():
    print("\n── TTL Expiry ─────────────────────────────────────────")
    cache = TTLCache(default_ttl=0.001, max_size=1000)
    cache.set("k", "v")
    time.sleep(0.01)

    misses = 0
    start = time.perf_counter()
    for _ in range(1000):
        if cache.get("k") is None:
            misses += 1
    elapsed = time.perf_counter() - start
    print(f"  {'expired key lookup':<40} {1000/elapsed:>12,.0f} ops/sec  (all {misses} expired correctly)")


if __name__ == "__main__":
    print("roboat Cache Benchmark")
    print("=" * 60)
    bench_sequential()
    bench_concurrent()
    bench_eviction()
    bench_ttl_expiry()
    print("\n" + "=" * 60)
    print("Done.\n")
