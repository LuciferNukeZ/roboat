"""
roboat.events
~~~~~~~~~~~~~~~~
Polling-based event system.
Monitor friends coming online, new game visits, friend requests, etc.

Example::

    from roboat import RoboatClient
    from roboat.events import EventPoller

    client = RoboatClient(cookie="...")
    poller = EventPoller(client)

    @poller.on_friend_online
    def handle(user):
        print(f"{user.name} just came online!")

    @poller.on_visit_milestone
    def milestone(game, count):
        print(f"{game.name} just hit {count:,} visits!")

    poller.start(interval=30)  # poll every 30 seconds
"""

from __future__ import annotations
import threading
import time
from typing import Callable, Dict, List, Optional, Set


class EventPoller:
    """
    Background polling engine that fires callbacks when Roblox state changes.

    Args:
        client: An authenticated RoboatClient.
        interval: Polling interval in seconds (default: 30).

    Registering handlers::

        @poller.on("friend_online")
        def handler(user):
            print(user.name, "is online!")

    Starting / stopping::

        poller.start()         # background thread
        poller.stop()
        poller.run_once()      # manual single poll
    """

    def __init__(self, client, interval: float = 30.0):
        self._c = client
        self.interval = interval
        self._handlers: Dict[str, List[Callable]] = {}
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # State tracking
        self._known_friends: Set[int] = set()
        self._known_online: Set[int] = set()
        self._tracked_universes: Dict[int, int] = {}  # universe_id → last visit count
        self._visit_milestones: Dict[int, int] = {}   # universe_id → next milestone
        self._known_requests: Set[int] = set()
        self._last_message_count: int = -1

    # ── Registration decorators ───────────────────────────────────────

    def on(self, event: str) -> Callable:
        """Generic decorator: @poller.on("event_name")"""
        def decorator(fn: Callable) -> Callable:
            self._handlers.setdefault(event, []).append(fn)
            return fn
        return decorator

    @property
    def on_friend_online(self) -> Callable:
        """Fires when a friend comes online. Handler receives (User,)."""
        return self.on("friend_online")

    @property
    def on_friend_offline(self) -> Callable:
        """Fires when a friend goes offline. Handler receives (User,)."""
        return self.on("friend_offline")

    @property
    def on_new_friend(self) -> Callable:
        """Fires when you gain a new friend. Handler receives (User,)."""
        return self.on("new_friend")

    @property
    def on_friend_removed(self) -> Callable:
        """Fires when a friend is removed. Handler receives (user_id,)."""
        return self.on("friend_removed")

    @property
    def on_friend_request(self) -> Callable:
        """Fires on new friend request. Handler receives (User,)."""
        return self.on("friend_request")

    @property
    def on_new_message(self) -> Callable:
        """Fires when an unread message count increases. Handler receives (count,)."""
        return self.on("new_message")

    @property
    def on_visit_milestone(self) -> Callable:
        """
        Fires when a tracked game hits a visit milestone.
        Handler receives (Game, milestone_count).
        """
        return self.on("visit_milestone")

    # ── Game tracking ─────────────────────────────────────────────────

    def track_game(self, universe_id: int,
                   milestone_step: int = 1_000_000) -> None:
        """
        Add a universe to visit monitoring.

        Args:
            universe_id: The universe to watch.
            milestone_step: Fire an event every N visits (default: 1M).
        """
        self._tracked_universes[universe_id] = 0
        self._visit_milestones[universe_id] = milestone_step

    def untrack_game(self, universe_id: int) -> None:
        """Stop watching a universe for visit milestones."""
        self._tracked_universes.pop(universe_id, None)
        self._visit_milestones.pop(universe_id, None)

    # ── Control ───────────────────────────────────────────────────────

    def start(self, interval: Optional[float] = None, daemon: bool = True) -> None:
        """
        Start polling in a background thread.

        Args:
            interval: Override polling interval.
            daemon: If True, thread exits when main program exits.
        """
        if interval is not None:
            self.interval = interval
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=daemon)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background polling thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def run_once(self) -> None:
        """Run a single poll cycle (useful for testing or manual control)."""
        self._poll()

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._poll()
            except Exception:
                pass
            self._stop_event.wait(self.interval)

    # ── Poll logic ────────────────────────────────────────────────────

    def _fire(self, event: str, *args) -> None:
        for handler in self._handlers.get(event, []):
            try:
                handler(*args)
            except Exception:
                pass

    def _poll(self) -> None:
        self._poll_friends()
        self._poll_games()
        self._poll_messages()

    def _poll_friends(self) -> None:
        if not self._c.is_authenticated:
            return
        try:
            uid = self._c.user_id()
            friends = self._c.friends.get_friends(uid)
            current_ids = {f.id for f in friends}

            # New friends
            for f in friends:
                if f.id not in self._known_friends and self._known_friends:
                    self._fire("new_friend", f)

            # Removed friends
            for fid in (self._known_friends - current_ids):
                self._fire("friend_removed", fid)

            self._known_friends = current_ids

            # Online status
            if friends:
                presences = self._c.presence.get_presences(list(current_ids)[:50])
                current_online = {
                    p.user_id for p in presences if p.user_presence_type > 0
                }
                friend_map = {f.id: f for f in friends}

                for uid_p in (current_online - self._known_online):
                    if uid_p in friend_map:
                        self._fire("friend_online", friend_map[uid_p])

                for uid_p in (self._known_online - current_online):
                    if uid_p in friend_map:
                        self._fire("friend_offline", friend_map[uid_p])

                self._known_online = current_online

            # Friend requests
            requests_page = self._c.friends.get_friend_requests(limit=10)
            current_requests = {u.id for u in requests_page.data}
            for user in requests_page.data:
                if user.id not in self._known_requests and self._known_requests:
                    self._fire("friend_request", user)
            self._known_requests = current_requests

        except Exception:
            pass

    def _poll_games(self) -> None:
        if not self._tracked_universes:
            return
        try:
            ids = list(self._tracked_universes.keys())
            games = self._c.games.get_games(ids)
            for game in games:
                last = self._tracked_universes.get(game.id, 0)
                step = self._visit_milestones.get(game.id, 1_000_000)
                if last == 0:
                    self._tracked_universes[game.id] = game.visits
                    continue
                next_milestone = (last // step + 1) * step
                if game.visits >= next_milestone:
                    self._fire("visit_milestone", game, next_milestone)
                self._tracked_universes[game.id] = game.visits
        except Exception:
            pass

    def _poll_messages(self) -> None:
        if not self._c.is_authenticated:
            return
        try:
            count = self._c.messages.get_unread_count()
            if self._last_message_count >= 0 and count > self._last_message_count:
                self._fire("new_message", count)
            self._last_message_count = count
        except Exception:
            pass
