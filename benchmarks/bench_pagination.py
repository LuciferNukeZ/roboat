"""
benchmarks/bench_pagination.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Benchmarks for the Paginator utility — measures iteration overhead
across different page sizes and item counts.

Run: python benchmarks/bench_pagination.py
"""

import time
from roboat.utils.paginator import Paginator
from roboat.models import Page


def make_fetch(total_items: int, page_size: int):
    """Create a fake paginated fetch function."""
    items = list(range(total_items))
    pages = [items[i:i+page_size] for i in range(0, len(items), page_size)]
    cursors = [None] + [f"c{i}" for i in range(len(pages) - 1)]
    page_map = {}
    for i, chunk in enumerate(pages):
        next_c = f"c{i}" if i < len(pages) - 1 else None
        page_map[cursors[i]] = Page(data=chunk, next_cursor=next_c)

    def fetch(cursor):
        return page_map.get(cursor, Page(data=[]))

    return fetch


def bench(label: str, total: int, page_size: int):
    fetch = make_fetch(total, page_size)
    p = Paginator(fetch)

    start = time.perf_counter()
    result = p.collect()
    elapsed = time.perf_counter() - start

    pages = (total + page_size - 1) // page_size
    print(f"  {label:<45} {len(result):>6} items  {pages:>4} pages  {elapsed*1000:.2f}ms")
    assert len(result) == total


if __name__ == "__main__":
    print("roboat Paginator Benchmark")
    print("=" * 70)
    print()

    print("── Collect all items ────────────────────────────────────────────────")
    bench("100 items, page_size=10",    100,    10)
    bench("1,000 items, page_size=25",  1_000,  25)
    bench("5,000 items, page_size=100", 5_000,  100)
    bench("10,000 items, page_size=100",10_000, 100)

    print()
    print("── First N items ────────────────────────────────────────────────────")
    for n in [10, 50, 100, 500]:
        fetch = make_fetch(10_000, 100)
        p = Paginator(fetch)
        start = time.perf_counter()
        result = p.first(n)
        elapsed = time.perf_counter() - start
        print(f"  first({n}) from 10,000 items{'':<20} {len(result):>6} items  {elapsed*1000:.2f}ms")

    print()
    print("Done.\n")
