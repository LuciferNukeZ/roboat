"""
roboat.social
~~~~~~~~~~~~~
Social graph tools — mutual friends, follow analysis,
presence monitoring, and relationship mapping.

Example::

    from roboat.social import SocialGraph

    sg = SocialGraph(client)

    # Find mutual friends between two users
    mutuals = sg.mutual_friends(156, 261)
    print(f"{len(mutuals)} mutual friends")

    # Check if user A follows user B
    follows = sg.does_follow(156, 261)

    # Get the most followed people in a friend group
    popular = sg.most_followed_in_group([156, 261, 1234])
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple
import threading


@dataclass
class UserNode:
    user_id: int
    username: str
    friend_count: int
    follower_count: int

    def __str__(self) -> str:
        return (
            f"@{self.username} [ID: {self.user_id}] "
            f"Friends: {self.friend_count:,}  Followers: {self.follower_count:,}"
        )


@dataclass
class PresenceSnapshot:
    """A point-in-time presence reading for multiple users."""
    timestamp: float
    online: List[int]    # user IDs that are online
    in_game: List[int]   # user IDs that are in a game
    in_studio: List[int] # user IDs in Roblox Studio
    offline: List[int]   # offline user IDs

    @property
    def total_online(self) -> int:
        return len(self.online) + len(self.in_game) + len(self.in_studio)

    def __str__(self) -> str:
        return (
            f"🟢 Online: {len(self.online)}  "
            f"🎮 In Game: {len(self.in_game)}  "
            f"🔧 Studio: {len(self.in_studio)}  "
            f"⚫ Offline: {len(self.offline)}"
        )


class SocialGraph:
    """
    Social graph analysis tools built on top of RoboatClient.

    Args:
        client: A RoboatClient instance.
    """

    def __init__(self, client):
        self._c = client

    # ── Mutual analysis ───────────────────────────────────────────────

    def mutual_friends(self, user_a: int, user_b: int) -> List[dict]:
        """
        Find friends that both user_a and user_b share.

        Returns:
            List of friend dicts that appear in both friend lists.
        """
        friends_a = {f.id: f for f in self._c.friends.get_friends(user_a)}
        friends_b = {f.id: f for f in self._c.friends.get_friends(user_b)}
        mutual_ids = set(friends_a.keys()) & set(friends_b.keys())
        return [friends_a[uid] for uid in mutual_ids]

    def mutual_friends_count(self, user_a: int, user_b: int) -> int:
        """Get just the count of mutual friends without returning all data."""
        friends_a = {f.id for f in self._c.friends.get_friends(user_a)}
        friends_b = {f.id for f in self._c.friends.get_friends(user_b)}
        return len(friends_a & friends_b)

    def does_follow(self, follower_id: int, target_id: int) -> bool:
        """
        Check if follower_id follows target_id.
        Checks the follower's following list for target_id.

        Returns:
            bool
        """
        from .utils import Paginator
        for user in Paginator(
            lambda c: self._c.friends.get_followings(follower_id, limit=100, cursor=c),
            max_items=5000,
        ):
            if user.id == target_id:
                return True
        return False

    def are_friends(self, user_a: int, user_b: int) -> bool:
        """Check if two users are friends with each other."""
        friends_a = {f.id for f in self._c.friends.get_friends(user_a)}
        return user_b in friends_a

    # ── Group analysis ────────────────────────────────────────────────

    def most_followed_in_group(self, user_ids: List[int]) -> List[UserNode]:
        """
        Given a list of user IDs, rank them by follower count.
        Fetches all data in parallel.

        Returns:
            List of UserNode sorted by follower count descending.
        """
        results: Dict[int, UserNode] = {}
        lock = threading.Lock()

        def fetch(uid: int):
            try:
                user = self._c.users.get_user(uid)
                fc   = self._c.friends.get_friend_count(uid)
                fl   = self._c.friends.get_follower_count(uid)
                node = UserNode(uid, user.name, fc, fl)
                with lock:
                    results[uid] = node
            except Exception:
                pass

        threads = [threading.Thread(target=fetch, args=(uid,)) for uid in user_ids]
        for t in threads: t.start()
        for t in threads: t.join()

        return sorted(results.values(), key=lambda n: n.follower_count, reverse=True)

    def friend_overlap_matrix(self, user_ids: List[int]) -> Dict[Tuple[int, int], int]:
        """
        Build a mutual friend count matrix for a group of users.
        Useful for visualising social clusters.

        Returns:
            Dict mapping (user_a, user_b) → mutual friend count.
        """
        friend_sets: Dict[int, Set[int]] = {}
        for uid in user_ids:
            try:
                friends = self._c.friends.get_friends(uid)
                friend_sets[uid] = {f.id for f in friends}
            except Exception:
                friend_sets[uid] = set()

        matrix: Dict[Tuple[int, int], int] = {}
        for i, a in enumerate(user_ids):
            for b in user_ids[i+1:]:
                count = len(friend_sets[a] & friend_sets[b])
                matrix[(a, b)] = count
                matrix[(b, a)] = count
        return matrix

    # ── Presence ──────────────────────────────────────────────────────

    def presence_snapshot(self, user_ids: List[int]) -> PresenceSnapshot:
        """
        Get a categorised presence snapshot for up to 50 users.

        Returns:
            PresenceSnapshot with users split by presence type.
        """
        import time
        presences = self._c.presence.get_presences(user_ids[:50])
        online    = [p.user_id for p in presences if p.user_presence_type == 1]
        in_game   = [p.user_id for p in presences if p.user_presence_type == 2]
        in_studio = [p.user_id for p in presences if p.user_presence_type == 3]
        offline   = [p.user_id for p in presences if p.user_presence_type == 0]
        return PresenceSnapshot(
            timestamp=time.time(),
            online=online,
            in_game=in_game,
            in_studio=in_studio,
            offline=offline,
        )

    def who_is_online(self, user_ids: List[int]) -> List[int]:
        """
        Filter a list of user IDs to only those currently online/in-game.

        Returns:
            List of user IDs that are not offline.
        """
        snap = self.presence_snapshot(user_ids)
        return snap.online + snap.in_game + snap.in_studio

    # ── Follow recommendations ────────────────────────────────────────

    def follow_suggestions(self, user_id: int,
                            depth: int = 2,
                            limit: int = 10) -> List[dict]:
        """
        Suggest users to follow based on friend-of-friend connections.
        Looks at friends of friends and ranks by frequency.

        Args:
            user_id: The seed user.
            depth: How many levels of friends to traverse (1 or 2).
            limit: Max number of suggestions.

        Returns:
            List of suggested user objects sorted by connection strength.
        """
        my_friends = {f.id for f in self._c.friends.get_friends(user_id)}
        my_friends.add(user_id)

        candidate_scores: Dict[int, int] = {}

        for fid in list(my_friends)[:20]:  # limit graph traversal
            try:
                fof = self._c.friends.get_friends(fid)
                for u in fof:
                    if u.id not in my_friends:
                        candidate_scores[u.id] = candidate_scores.get(u.id, 0) + 1
            except Exception:
                continue

        top_ids = sorted(candidate_scores, key=candidate_scores.__getitem__, reverse=True)[:limit]
        if not top_ids:
            return []
        return self._c.users.get_users_by_ids(top_ids)
