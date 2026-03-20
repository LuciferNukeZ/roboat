"""
roboat.utils.paginator
~~~~~~~~~~~~~~~~~~~~~~~~~
Lazy paginator that auto-fetches all pages from any cursor-based endpoint.
"""

from __future__ import annotations
from typing import Callable, Iterator, List, Optional, TypeVar, Generic

T = TypeVar("T")


class Paginator(Generic[T]):
    """
    Lazy iterator over all pages of a cursor-based Roblox endpoint.

    Args:
        fetch_fn: Function that accepts ``cursor`` and returns a ``Page``.
        limit: Items per page.
        max_items: Stop after this many items (None = fetch all).

    Example::

        # Fetch ALL friends, one page at a time
        for friend in Paginator(lambda c: client.friends.get_friends(156, cursor=c)):
            print(friend)

        # First 500 followers only
        followers = list(Paginator(
            lambda c: client.friends.get_followers(156, limit=100, cursor=c),
            max_items=500,
        ))
    """

    def __init__(
        self,
        fetch_fn: Callable,
        limit: int = 100,
        max_items: Optional[int] = None,
    ):
        self._fetch = fetch_fn
        self._limit = limit
        self._max_items = max_items

    def __iter__(self) -> Iterator[T]:
        cursor = None
        count = 0
        while True:
            page = self._fetch(cursor)
            for item in page.data:
                yield item
                count += 1
                if self._max_items and count >= self._max_items:
                    return
            cursor = page.next_cursor
            if not cursor:
                break

    def collect(self) -> List[T]:
        """Eagerly collect all results into a list."""
        return list(self)

    def first(self, n: int = 1) -> List[T]:
        """Collect the first N items."""
        items = []
        for item in self:
            items.append(item)
            if len(items) >= n:
                break
        return items
