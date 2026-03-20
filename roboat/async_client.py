"""
roboat.async_client
~~~~~~~~~~~~~~~~~~~~~~
Async version of RoboatClient using aiohttp for parallel, high-performance requests.
Mirrors the sync API exactly but every method is a coroutine.

Requires: pip install aiohttp

Example::

    import asyncio
    from roboat import AsyncRoboatClient

    async def main():
        async with AsyncRoboatClient(cookie="...") as client:
            # Fetch 1000 users in parallel — massively faster than sync
            user_ids = list(range(1, 1001))
            users = await client.users.get_users_by_ids(user_ids)

            # Parallel game + vote + thumbnail fetch
            game, votes, icon = await asyncio.gather(
                client.games.get_game(2753915549),
                client.games.get_votes([2753915549]),
                client.thumbnails.get_game_icons([2753915549]),
            )

    asyncio.run(main())
"""

from __future__ import annotations
import asyncio
from typing import List, Optional, Any

try:
    import aiohttp
    _AIOHTTP_AVAILABLE = True
except ImportError:
    _AIOHTTP_AVAILABLE = False

from .models import (
    User, Game, GameVotes, GameServer, Friend, Group, GroupRole,
    Badge, CatalogItem, UserPresence, Avatar, RobuxBalance, Page,
)
from .exceptions import (
    RateLimitedError, InvalidCookieError, UserNotFoundError,
    GameNotFoundError, ItemNotFoundError, RobloxAPIError,
    NotAuthenticatedError,
)


class AsyncRoboatClient:
    """
    High-performance async Roblox API client.

    Use as an async context manager::

        async with AsyncRoboatClient(cookie="...") as client:
            user = await client.users.get_user(156)

    Or manage the session manually::

        client = AsyncRoboatClient(cookie="...")
        await client.start()
        user = await client.users.get_user(156)
        await client.close()
    """

    _BASE_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "roboat-python/2.0-async",
    }

    def __init__(self, cookie: Optional[str] = None, timeout: int = 10):
        if not _AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp is required for AsyncRoboatClient. "
                "Install it with: pip install aiohttp"
            )
        self._cookie = cookie
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._csrf_token: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

        # Sub-APIs
        self.users      = _AsyncUsersAPI(self)
        self.games      = _AsyncGamesAPI(self)
        self.friends    = _AsyncFriendsAPI(self)
        self.catalog    = _AsyncCatalogAPI(self)
        self.groups     = _AsyncGroupsAPI(self)
        self.thumbnails = _AsyncThumbnailsAPI(self)
        self.badges     = _AsyncBadgesAPI(self)
        self.presence   = _AsyncPresenceAPI(self)
        self.economy    = _AsyncEconomyAPI(self)

    async def start(self) -> None:
        """Open the aiohttp session."""
        cookies = {}
        if self._cookie:
            cookies[".ROBLOSECURITY"] = self._cookie
        self._session = aiohttp.ClientSession(
            headers=self._BASE_HEADERS,
            cookies=cookies,
            timeout=self._timeout,
        )
        if self._cookie:
            await self._refresh_csrf()

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> "AsyncRoboatClient":
        await self.start()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def _refresh_csrf(self) -> None:
        try:
            async with self._session.post("https://auth.roblox.com/v2/logout") as r:
                token = r.headers.get("x-csrf-token")
                if token:
                    self._csrf_token = token
                    self._session.headers.update({"x-csrf-token": token})
        except Exception:
            pass

    def require_auth(self, name: str = "") -> None:
        if not self._cookie:
            raise NotAuthenticatedError(name)

    async def _handle(self, resp: aiohttp.ClientResponse) -> Any:
        if resp.status == 429:
            raise RateLimitedError()
        if resp.status == 401:
            raise InvalidCookieError()
        if resp.status == 404:
            url = str(resp.url)
            if "users" in url:    raise UserNotFoundError(url)
            if "games" in url:    raise GameNotFoundError(url)
            if "catalog" in url:  raise ItemNotFoundError(url)
        if not resp.ok:
            try:
                body = await resp.json()
                errs = body.get("errors", [])
                msg = "; ".join(e.get("message", "") for e in errs) or await resp.text()
            except Exception:
                msg = await resp.text()
            raise RobloxAPIError(f"HTTP {resp.status}: {msg}")
        try:
            return await resp.json()
        except Exception:
            return {}

    async def _get(self, url: str, **kwargs) -> Any:
        async with self._session.get(url, **kwargs) as r:
            return await self._handle(r)

    async def _post(self, url: str, **kwargs) -> Any:
        async with self._session.post(url, **kwargs) as r:
            if r.status == 403:
                await self._refresh_csrf()
                async with self._session.post(url, **kwargs) as r2:
                    return await self._handle(r2)
            return await self._handle(r)

    # ── Convenience shortcuts ──────────────────────────────────────────

    async def user_id(self) -> int:
        self.require_auth("user_id")
        data = await self._get("https://users.roblox.com/v1/users/authenticated")
        return data["id"]

    async def username(self) -> str:
        self.require_auth("username")
        data = await self._get("https://users.roblox.com/v1/users/authenticated")
        return data["name"]

    async def robux(self) -> int:
        self.require_auth("robux")
        uid = await self.user_id()
        data = await self._get(f"https://economy.roblox.com/v1/users/{uid}/currency")
        return data.get("robux", 0)

    @property
    def is_authenticated(self) -> bool:
        return self._cookie is not None

    def __repr__(self) -> str:
        auth = "authenticated" if self.is_authenticated else "unauthenticated"
        return f"<AsyncRoboatClient [{auth}]>"


# ── Sub-APIs ──────────────────────────────────────────────────────────── #

class _AsyncUsersAPI:
    BASE = "https://users.roblox.com/v1"

    def __init__(self, c): self._c = c

    async def get_user(self, user_id: int) -> User:
        data = await self._c._get(f"{self.BASE}/users/{user_id}")
        return User.from_dict(data)

    async def get_users_by_ids(self, user_ids: List[int],
                                exclude_banned: bool = False) -> List[User]:
        # Chunk into batches of 100
        results = []
        for i in range(0, len(user_ids), 100):
            chunk = user_ids[i:i + 100]
            data = await self._c._post(
                f"{self.BASE}/users",
                json={"userIds": chunk, "excludeBannedUsers": exclude_banned},
            )
            results.extend(User.from_dict(u) for u in data.get("data", []))
        return results

    async def get_users_by_usernames(self, usernames: List[str]) -> List[User]:
        data = await self._c._post(
            f"{self.BASE}/usernames/users",
            json={"usernames": usernames, "excludeBannedUsers": False},
        )
        return [User.from_dict(u) for u in data.get("data", [])]

    async def search_users(self, keyword: str, limit: int = 10) -> Page:
        data = await self._c._get(
            f"{self.BASE}/users/search",
            params={"keyword": keyword, "limit": limit},
        )
        return Page.from_dict(data, User)


class _AsyncGamesAPI:
    BASE  = "https://games.roblox.com/v1"
    BASE2 = "https://games.roblox.com/v2"

    def __init__(self, c): self._c = c

    async def get_games(self, universe_ids: List[int]) -> List[Game]:
        data = await self._c._get(
            f"{self.BASE}/games",
            params={"universeIds": ",".join(str(i) for i in universe_ids)},
        )
        return [Game.from_dict(g) for g in data.get("data", [])]

    async def get_game(self, universe_id: int) -> Game:
        games = await self.get_games([universe_id])
        return games[0] if games else None

    async def get_visits(self, universe_ids: List[int]) -> dict:
        games = await self.get_games(universe_ids)
        return {g.id: g.visits for g in games}

    async def get_votes(self, universe_ids: List[int]) -> List[GameVotes]:
        data = await self._c._get(
            f"{self.BASE}/games/votes",
            params={"universeIds": ",".join(str(i) for i in universe_ids)},
        )
        return [GameVotes.from_dict(v) for v in data.get("data", [])]

    async def get_servers(self, place_id: int, limit: int = 10) -> Page:
        data = await self._c._get(
            f"{self.BASE}/games/{place_id}/servers/Public",
            params={"limit": limit},
        )
        servers = [GameServer.from_dict(s) for s in data.get("data", [])]
        return Page(data=servers, next_cursor=data.get("nextPageCursor"))

    async def get_user_games(self, user_id: int, limit: int = 50) -> Page:
        data = await self._c._get(
            f"{self.BASE2}/users/{user_id}/games",
            params={"limit": limit},
        )
        return Page.from_dict(data, Game)


class _AsyncFriendsAPI:
    BASE = "https://friends.roblox.com/v1"

    def __init__(self, c): self._c = c

    async def get_friends(self, user_id: int) -> List[Friend]:
        data = await self._c._get(f"{self.BASE}/users/{user_id}/friends")
        return [Friend.from_dict(f) for f in data.get("data", [])]

    async def get_friend_count(self, user_id: int) -> int:
        data = await self._c._get(f"{self.BASE}/users/{user_id}/friends/count")
        return data.get("count", 0)

    async def get_follower_count(self, user_id: int) -> int:
        data = await self._c._get(f"{self.BASE}/users/{user_id}/followers/count")
        return data.get("count", 0)

    async def get_followers(self, user_id: int, limit: int = 100,
                             cursor: Optional[str] = None) -> Page:
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        data = await self._c._get(f"{self.BASE}/users/{user_id}/followers", params=params)
        return Page.from_dict(data, Friend)


class _AsyncCatalogAPI:
    BASE = "https://catalog.roblox.com/v1"

    def __init__(self, c): self._c = c

    async def search(self, keyword: str = "", category: str = "All",
                     limit: int = 30, cursor: Optional[str] = None) -> Page:
        params = {"category": category, "limit": limit}
        if keyword: params["keyword"] = keyword
        if cursor:  params["cursor"] = cursor
        data = await self._c._get(f"{self.BASE}/search/items", params=params)
        return Page.from_dict(data, CatalogItem)

    async def get_item_details(self, items: List[dict]) -> List[CatalogItem]:
        data = await self._c._post(
            f"{self.BASE}/catalog/items/details",
            json={"items": items},
        )
        return [CatalogItem.from_dict(i) for i in data.get("data", [])]


class _AsyncGroupsAPI:
    BASE = "https://groups.roblox.com/v1"

    def __init__(self, c): self._c = c

    async def get_group(self, group_id: int) -> Group:
        data = await self._c._get(f"{self.BASE}/groups/{group_id}")
        return Group.from_dict(data)

    async def get_roles(self, group_id: int) -> List[GroupRole]:
        data = await self._c._get(f"{self.BASE}/groups/{group_id}/roles")
        return [GroupRole.from_dict(r) for r in data.get("roles", [])]

    async def get_members(self, group_id: int, limit: int = 100,
                          cursor: Optional[str] = None) -> Page:
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        data = await self._c._get(f"{self.BASE}/groups/{group_id}/users", params=params)
        return Page.from_dict(data)


class _AsyncThumbnailsAPI:
    BASE = "https://thumbnails.roblox.com/v1"

    def __init__(self, c): self._c = c

    def _urls(self, data: dict) -> dict:
        return {
            item["targetId"]: item.get("imageUrl", "")
            for item in data.get("data", [])
            if item.get("state") == "Completed"
        }

    async def get_user_avatars(self, user_ids: List[int],
                                size: str = "420x420") -> dict:
        data = await self._c._get(
            f"{self.BASE}/users/avatar",
            params={"userIds": ",".join(str(i) for i in user_ids),
                    "size": size, "format": "Png"},
        )
        return self._urls(data)

    async def get_game_icons(self, universe_ids: List[int],
                              size: str = "512x512") -> dict:
        data = await self._c._get(
            f"{self.BASE}/games/icons",
            params={"universeIds": ",".join(str(i) for i in universe_ids),
                    "size": size, "format": "Png"},
        )
        return self._urls(data)

    async def get_asset_thumbnails(self, asset_ids: List[int],
                                    size: str = "420x420") -> dict:
        data = await self._c._get(
            f"{self.BASE}/assets",
            params={"assetIds": ",".join(str(i) for i in asset_ids),
                    "size": size, "format": "Png"},
        )
        return self._urls(data)


class _AsyncBadgesAPI:
    BASE = "https://badges.roblox.com/v1"

    def __init__(self, c): self._c = c

    async def get_badge(self, badge_id: int) -> Badge:
        data = await self._c._get(f"{self.BASE}/badges/{badge_id}")
        return Badge.from_dict(data)

    async def get_universe_badges(self, universe_id: int, limit: int = 10) -> Page:
        data = await self._c._get(
            f"{self.BASE}/universes/{universe_id}/badges",
            params={"limit": limit},
        )
        return Page.from_dict(data, Badge)

    async def get_user_badges(self, user_id: int, limit: int = 100) -> Page:
        data = await self._c._get(
            f"{self.BASE}/users/{user_id}/badges",
            params={"limit": limit},
        )
        return Page.from_dict(data, Badge)


class _AsyncPresenceAPI:
    BASE = "https://presence.roblox.com/v1"

    def __init__(self, c): self._c = c

    async def get_presences(self, user_ids: List[int]) -> List[UserPresence]:
        data = await self._c._post(
            f"{self.BASE}/presence/users",
            json={"userIds": user_ids},
        )
        return [UserPresence.from_dict(p) for p in data.get("userPresences", [])]

    async def get_presence(self, user_id: int) -> UserPresence:
        results = await self.get_presences([user_id])
        return results[0] if results else UserPresence(user_id=user_id)


class _AsyncEconomyAPI:
    BASE = "https://economy.roblox.com/v1"

    def __init__(self, c): self._c = c

    async def get_robux_balance(self, user_id: int) -> RobuxBalance:
        self._c.require_auth("get_robux_balance")
        data = await self._c._get(f"{self.BASE}/users/{user_id}/currency")
        return RobuxBalance(robux=data.get("robux", 0))

    async def get_asset_resale_data(self, asset_id: int) -> dict:
        return await self._c._get(f"{self.BASE}/assets/{asset_id}/resale-data")

    async def get_asset_resellers(self, asset_id: int, limit: int = 10) -> Page:
        data = await self._c._get(
            f"{self.BASE}/assets/{asset_id}/resellers",
            params={"limit": limit},
        )
        return Page.from_dict(data)
