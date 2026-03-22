"""
roboat.analytics
~~~~~~~~~~~~~~~~~~~
High-level analytics and reporting layer.
Combines multiple API calls into ready-to-use summaries and comparisons.

Example::

    from roboat import RoboatClient
    from roboat.analytics import Analytics

    client = RoboatClient(cookie="...")
    an = Analytics(client)

    report = an.user_report(156)
    print(report)

    comp = an.compare_games([2753915549, 286090429])
    print(comp)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import threading


@dataclass
class UserReport:
    user_id: int
    username: str
    display_name: str
    is_banned: bool
    has_verified_badge: bool
    friend_count: int
    follower_count: int
    following_count: int
    badge_count: int
    group_count: int
    total_rap: int
    collectible_count: int
    presence_status: str
    avatar_url: Optional[str]
    games: List[dict] = field(default_factory=list)

    def __str__(self) -> str:
        banned  = " [BANNED]" if self.is_banned else ""
        verify  = " ✓" if self.has_verified_badge else ""
        lines = [
            f"",
            f"  ╔══ User Report {'═'*38}╗",
            f"  ║  {self.display_name} (@{self.username}){verify}{banned}",
            f"  ║  ID          : {self.user_id}",
            f"  ║  Status      : {self.presence_status}",
            f"  ╠{'═'*54}╣",
            f"  ║  Friends     : {self.friend_count:>10,}",
            f"  ║  Followers   : {self.follower_count:>10,}",
            f"  ║  Following   : {self.following_count:>10,}",
            f"  ║  Badges      : {self.badge_count:>10,}",
            f"  ║  Groups      : {self.group_count:>10,}",
            f"  ╠{'═'*54}╣",
            f"  ║  Total RAP   : {self.total_rap:>9,}R$",
            f"  ║  Collectibles: {self.collectible_count:>10,}",
        ]
        if self.games:
            lines.append(f"  ╠{'═'*54}╣")
            lines.append(f"  ║  Created Games ({len(self.games)}):")
            for g in self.games[:3]:
                lines.append(f"  ║    • {g.get('name','?')[:40]}")
        if self.avatar_url:
            lines.append(f"  ╠{'═'*54}╣")
            lines.append(f"  ║  Avatar: {self.avatar_url}")
        lines.append(f"  ╚{'═'*54}╝")
        return "\n".join(lines)


@dataclass
class GameComparison:
    games: list
    votes: list

    def __str__(self) -> str:
        lines = [
            "",
            f"  ╔══ Game Comparison {'═'*35}╗",
            f"  ║  {'Name':<30} {'Visits':>12} {'Playing':>8} {'👍%':>6}",
            f"  ╠{'═'*54}╣",
        ]
        vote_map = {v.universe_id: v for v in self.votes}
        for g in self.games:
            v = vote_map.get(g.id)
            ratio = f"{v.ratio}%" if v else "N/A"
            name = g.name[:28]
            lines.append(
                f"  ║  {name:<30} {g.visits:>12,} {g.playing:>8,} {ratio:>6}"
            )
        lines.append(f"  ╚{'═'*54}╝")
        return "\n".join(lines)


@dataclass
class GroupReport:
    group_id: int
    name: str
    owner_name: Optional[str]
    member_count: int
    role_count: int
    is_public: bool
    has_verified_badge: bool
    robux_balance: Optional[int]
    shout: Optional[str]
    ally_count: int
    enemy_count: int

    def __str__(self) -> str:
        verified = " ✓" if self.has_verified_badge else ""
        pub      = "Public" if self.is_public else "Private"
        balance  = f"{self.robux_balance:,}R$" if self.robux_balance is not None else "N/A"
        lines = [
            f"",
            f"  ╔══ Group Report {'═'*38}╗",
            f"  ║  {self.name}{verified}  [ID: {self.group_id}]",
            f"  ║  Owner       : {self.owner_name}",
            f"  ║  Access      : {pub}",
            f"  ╠{'═'*54}╣",
            f"  ║  Members     : {self.member_count:>10,}",
            f"  ║  Roles       : {self.role_count:>10,}",
            f"  ║  Allies      : {self.ally_count:>10,}",
            f"  ║  Enemies     : {self.enemy_count:>10,}",
            f"  ║  Balance     : {balance:>10}",
        ]
        if self.shout:
            shout_short = self.shout[:45] + "…" if len(self.shout) > 45 else self.shout
            lines.append(f"  ╠{'═'*54}╣")
            lines.append(f"  ║  Shout: {shout_short}")
        lines.append(f"  ╚{'═'*54}╝")
        return "\n".join(lines)


class Analytics:
    """
    High-level analytics layer that aggregates multiple API calls.
    All methods return rich dataclasses with formatted __str__ output.

    Args:
        client: A RoboatClient instance.

    Example::

        an = Analytics(client)
        print(an.user_report(156))
        print(an.compare_games([2753915549, 286090429]))
        print(an.group_report(7))
    """

    def __init__(self, client):
        self._c = client

    def user_report(self, user_id: int,
                    include_games: bool = True,
                    include_rap: bool = True) -> UserReport:
        """
        Build a comprehensive profile report for a user.
        Fetches user info, social counts, presence, avatar, groups,
        badges, and optionally games + RAP in parallel.
        """
        results: Dict[str, any] = {}
        errors: Dict[str, Exception] = {}

        def fetch(key, fn):
            try:
                results[key] = fn()
            except Exception as e:
                errors[key] = e
                results[key] = None

        tasks = [
            ("user",       lambda: self._c.users.get_user(user_id)),
            ("friends",    lambda: self._c.friends.get_friend_count(user_id)),
            ("followers",  lambda: self._c.friends.get_follower_count(user_id)),
            ("following",  lambda: self._c.friends.get_following_count(user_id)),
            ("presence",   lambda: self._c.presence.get_presence(user_id)),
            ("groups",     lambda: self._c.groups.get_user_groups(user_id)),
            ("badges",     lambda: self._c.badges.get_user_badges(user_id, limit=1)),
            ("avatar_url", lambda: self._c.thumbnails.get_avatar_url(user_id)),
        ]
        if include_games:
            tasks.append(("games", lambda: self._c.games.get_user_games(user_id, limit=5)))
        if include_rap:
            tasks.append(("collectibles", lambda: self._c.inventory.get_collectibles(user_id, limit=100)))

        threads = [threading.Thread(target=fetch, args=(k, fn)) for k, fn in tasks]
        for t in threads: t.start()
        for t in threads: t.join()

        user = results.get("user")
        if not user:
            raise ValueError(f"Could not fetch user {user_id}")

        collectibles = results.get("collectibles")
        total_rap = sum(a.recent_average_price for a in (collectibles.data if collectibles else []))
        collectible_count = len(collectibles.data) if collectibles else 0
        if collectibles and collectibles.next_cursor:
            try:
                total_rap = self._c.inventory.get_total_rap(user_id)
            except Exception:
                pass

        games_page = results.get("games")
        games_list = []
        if games_page:
            games_list = [{"name": g.name, "visits": g.visits} for g in games_page.data]

        badges_page = results.get("badges")
        # fix later
        badge_count = len(badges_page.data) if badges_page else 0

        return UserReport(
            user_id=user.id,
            username=user.name,
            display_name=user.display_name,
            is_banned=user.is_banned,
            has_verified_badge=user.has_verified_badge,
            friend_count=results.get("friends") or 0,
            follower_count=results.get("followers") or 0,
            following_count=results.get("following") or 0,
            badge_count=badge_count,
            group_count=len(results.get("groups") or []),
            total_rap=total_rap,
            collectible_count=collectible_count,
            presence_status=(results.get("presence") or type("P", (), {"status": "Unknown"})()).status,
            avatar_url=results.get("avatar_url"),
            games=games_list,
        )

    def compare_games(self, universe_ids: List[int]) -> GameComparison:
        """
        Fetch and compare multiple games side by side.
        Returns a GameComparison with visit counts, player counts, and vote ratios.
        """
        games = self._c.games.get_games(universe_ids)
        votes = self._c.games.get_votes(universe_ids)
        return GameComparison(games=games, votes=votes)

    def group_report(self, group_id: int) -> GroupReport:
        """
        Build a comprehensive report for a group.
        Fetches group info, roles, shout, allies, enemies, and optionally balance.
        """
        results: Dict[str, any] = {}

        def fetch(key, fn):
            try:
                results[key] = fn()
            except Exception:
                results[key] = None

        tasks = [
            ("group",   lambda: self._c.groups.get_group(group_id)),
            ("roles",   lambda: self._c.groups.get_roles(group_id)),
            ("shout",   lambda: self._c.groups.get_group_shout(group_id)),
            ("allies",  lambda: self._c.groups.get_allies(group_id)),
            ("enemies", lambda: self._c.groups.get_enemies(group_id)),
        ]
        if self._c.is_authenticated:
            tasks.append(("balance", lambda: self._c.economy.get_group_funds(group_id)))

        threads = [threading.Thread(target=fetch, args=(k, fn)) for k, fn in tasks]
        for t in threads: t.start()
        for t in threads: t.join()

        group = results.get("group")
        if not group:
            raise ValueError(f"Could not fetch group {group_id}")

        shout = results.get("shout")
        balance_obj = results.get("balance")

        return GroupReport(
            group_id=group.id,
            name=group.name,
            owner_name=group.owner_name,
            member_count=group.member_count,
            role_count=len(results.get("roles") or []),
            is_public=group.is_public,
            has_verified_badge=group.has_verified_badge,
            robux_balance=balance_obj.robux if balance_obj else None,
            shout=shout.body if shout else None,
            ally_count=len(results.get("allies") or []),
            enemy_count=len(results.get("enemies") or []),
        )

    def leaderboard(self, universe_ids: List[int],
                    by: str = "visits") -> List[dict]:
        """
        Rank games by a stat.

        Args:
            by: "visits", "playing", "favorites", "ratio" (vote %)

        Returns:
            Sorted list of dicts with game info + stat.
        """
        games  = self._c.games.get_games(universe_ids)
        votes  = self._c.games.get_votes(universe_ids)
        vmap   = {v.universe_id: v for v in votes}
        favs   = {uid: self._c.games.get_favorite_count(uid) for uid in universe_ids}

        rows = []
        for g in games:
            v = vmap.get(g.id)
            rows.append({
                "rank":      0,
                "name":      g.name,
                "id":        g.id,
                "visits":    g.visits,
                "playing":   g.playing,
                "favorites": favs.get(g.id, 0),
                "ratio":     v.ratio if v else 0.0,
            })

        key_map = {"visits": "visits", "playing": "playing",
                   "favorites": "favorites", "ratio": "ratio"}
        rows.sort(key=lambda r: r[key_map.get(by, "visits")], reverse=True)
        for i, row in enumerate(rows, 1):
            row["rank"] = i
        return rows

    def rich_leaderboard_str(self, universe_ids: List[int],
                              by: str = "visits") -> str:
        """Return a formatted string leaderboard table."""
        rows = self.leaderboard(universe_ids, by=by)
        header = f"  {'#':>3}  {'Name':<32} {'Visits':>12} {'Playing':>8} {'Ratio':>7}"
        divider = "  " + "─" * 68
        lines = [f"\n  🏆 Game Leaderboard (by {by})", divider, header, divider]
        for r in rows:
            lines.append(
                f"  {r['rank']:>3}. {r['name'][:30]:<32} "
                f"{r['visits']:>12,} {r['playing']:>8,} {r['ratio']:>6.1f}%"
            )
        lines.append(divider)
        return "\n".join(lines)
