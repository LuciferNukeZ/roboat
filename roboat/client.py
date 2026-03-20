"""
roboat.client
~~~~~~~~~~~~~~~~
RoboatClient and ClientBuilder — main entry points.
"""

from __future__ import annotations
import requests
from typing import Optional

from .exceptions import (
    RateLimitedError, InvalidCookieError, UserNotFoundError,
    GameNotFoundError, ItemNotFoundError, GroupNotFoundError,
    BadgeNotFoundError, RobloxAPIError, NotAuthenticatedError,
)
from .utils.cache import TTLCache
from .utils.ratelimit import TokenBucket


class ClientBuilder:
    """
    Fluent builder for RoboatClient — roboat-style.

    Example::

        client = (
            ClientBuilder()
            .set_cookie("ROBLOSECURITY")
            .set_timeout(15)
            .set_cache_ttl(60)
            .set_rate_limit(10)
            .build()
        )
    """

    def __init__(self):
        self._oauth_token: Optional[str] = None
        self._timeout: int = 10
        self._proxies: Optional[dict] = None
        self._cache_ttl: float = 30.0
        self._cache_size: int = 512
        self._rate_limit: float = 10.0

    def set_oauth_token(self, cookie: str) -> "ClientBuilder":
        self._cookie = cookie
        return self

    def set_timeout(self, seconds: int) -> "ClientBuilder":
        self._timeout = seconds
        return self

    def set_proxy(self, http: str, https: Optional[str] = None) -> "ClientBuilder":
        self._proxies = {"http": http, "https": https or http}
        return self

    def set_cache_ttl(self, seconds: float) -> "ClientBuilder":
        """Set how long API responses are cached (0 to disable)."""
        self._cache_ttl = seconds
        return self

    def set_cache_size(self, max_entries: int) -> "ClientBuilder":
        self._cache_size = max_entries
        return self

    def set_rate_limit(self, requests_per_second: float) -> "ClientBuilder":
        """Throttle requests to avoid 429s."""
        self._rate_limit = requests_per_second
        return self

    def build(self) -> "RoboatClient":
        return RoboatClient(
            oauth_token=self._oauth_token,
            timeout=self._timeout,
            proxies=self._proxies,
            cache_ttl=self._cache_ttl,
            cache_size=self._cache_size,
            rate_limit=self._rate_limit,
        )


class RoboatClient:
    """
    Full-featured Roblox API client.

    Sub-APIs:
        client.users        — User lookup, search, username history
        client.games        — Games, visits, servers, votes, passes
        client.catalog      — Avatar shop, items, resale, bundles
        client.groups       — Groups, roles, members, wall, audit log
        client.friends      — Friends, followers, followings, requests
        client.thumbnails   — Thumbnail URLs for any resource type
        client.badges       — Badges and award dates
        client.economy      — Robux, transactions, resellers
        client.presence     — Online / in-game status
        client.avatar       — Avatar assets, colors, scales, outfits
        client.trades       — Trade list, details, send, accept, decline
        client.messages     — Private messages and chat
        client.inventory    — Inventory, collectibles, ownership checks
        client.develop      — Universe/place management, datastores, stats
        client.events       — Polling-based event system
    """

    _BASE_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "roboat-python/2.0",
    }

    def __init__(
        self,
        oauth_token: Optional[str] = None,
        timeout: int = 10,
        proxies: Optional[dict] = None,
        cache_ttl: float = 30.0,
        cache_size: int = 512,
        rate_limit: float = 10.0,
    ):
        self._oauth_token: Optional[str] = None
        self._csrf_token: Optional[str] = None
        self._timeout = timeout
        self._cache = TTLCache(default_ttl=cache_ttl, max_size=cache_size)
        self._bucket = TokenBucket(rate=rate_limit, capacity=rate_limit * 2)

        self._session = requests.Session()
        self._session.headers.update(self._BASE_HEADERS)
        if proxies:
            self._session.proxies.update(proxies)

        # Lazy-import and attach all sub-APIs
        from .users      import UsersAPI
        from .games      import GamesAPI
        from .catalog    import CatalogAPI
        from .groups     import GroupsAPI
        from .friends    import FriendsAPI
        from .thumbnails import ThumbnailsAPI
        from .badges     import BadgesAPI
        from .economy    import EconomyAPI
        from .presence   import PresenceAPI
        from .avatar     import AvatarAPI
        from .trades     import TradesAPI
        from .messages   import MessagesAPI, ChatAPI
        from .inventory  import InventoryAPI
        from .develop    import DevelopAPI
        from .events     import EventPoller

        self.users      = UsersAPI(self)
        self.games      = GamesAPI(self)
        self.catalog    = CatalogAPI(self)
        self.groups     = GroupsAPI(self)
        self.friends    = FriendsAPI(self)
        self.thumbnails = ThumbnailsAPI(self)
        self.badges     = BadgesAPI(self)
        self.economy    = EconomyAPI(self)
        self.presence   = PresenceAPI(self)
        self.avatar     = AvatarAPI(self)
        self.trades     = TradesAPI(self)
        self.messages   = MessagesAPI(self)
        self.chat       = ChatAPI(self)
        self.inventory  = InventoryAPI(self)
        self.develop    = DevelopAPI(self)
        self.events     = EventPoller(self)

        if cookie:
            self.set_cookie(cookie)

    # ── Auth ──────────────────────────────────────────────────────────

    def set_oauth_token(self, cookie: str) -> None:
        """Set the OAuth access token for authenticated requests."""
        self._oauth_token = oauth_token
        self._session.headers.update({"Authorization": f"Bearer {self._oauth_token}"})
        self._refresh_csrf()

    def _refresh_csrf(self) -> None:
        try:
            r = self._session.post("https://auth.roblox.com/v2/logout", timeout=self._timeout)
            token = r.headers.get("x-csrf-token")
            if token:
                self._csrf_token = token
                self._session.headers.update({"x-csrf-token": token})
        except Exception:
            pass

    @property
    def is_authenticated(self) -> bool:
        return self._oauth_token is not None

    def require_auth(self, name: str = "") -> None:
        if not self.is_authenticated:
            raise NotAuthenticatedError(name)

    # ── HTTP helpers ──────────────────────────────────────────────────

    def _handle_response(self, resp: requests.Response) -> dict:
        if resp.status_code == 429:
            raise RateLimitedError()
        if resp.status_code == 401:
            raise InvalidCookieError()
        if resp.status_code == 404:
            url = resp.url
            if "users"   in url: raise UserNotFoundError(f"Not found: {url}")
            if "games"   in url: raise GameNotFoundError(f"Not found: {url}")
            if "catalog" in url: raise ItemNotFoundError(f"Not found: {url}")
            if "groups"  in url: raise GroupNotFoundError(f"Not found: {url}")
            if "badges"  in url: raise BadgeNotFoundError(f"Not found: {url}")
        if resp.status_code == 403:
            token = resp.headers.get("x-csrf-token")
            if token:
                self._csrf_token = token
                self._session.headers.update({"x-csrf-token": token})
        if not resp.ok:
            try:
                body = resp.json()
                errs = body.get("errors", [])
                msg = "; ".join(e.get("message", "") for e in errs) if errs else resp.text
            except Exception:
                msg = resp.text
            raise RobloxAPIError(f"HTTP {resp.status_code}: {msg}")
        try:
            return resp.json()
        except Exception:
            return {}

    def _get(self, url: str, **kwargs) -> dict:
        self._bucket.consume()
        kwargs.setdefault("timeout", self._timeout)
        resp = self._session.get(url, **kwargs)
        return self._handle_response(resp)

    def _post(self, url: str, **kwargs) -> dict:
        self._bucket.consume()
        kwargs.setdefault("timeout", self._timeout)
        resp = self._session.post(url, **kwargs)
        if resp.status_code == 403:
            self._refresh_csrf()
            resp = self._session.post(url, **kwargs)
        return self._handle_response(resp)

    def _patch(self, url: str, **kwargs) -> dict:
        self._bucket.consume()
        kwargs.setdefault("timeout", self._timeout)
        resp = self._session.patch(url, **kwargs)
        if resp.status_code == 403:
            self._refresh_csrf()
            resp = self._session.patch(url, **kwargs)
        return self._handle_response(resp)

    def _delete(self, url: str, **kwargs) -> dict:
        self._bucket.consume()
        kwargs.setdefault("timeout", self._timeout)
        resp = self._session.delete(url, **kwargs)
        if resp.status_code == 403:
            self._refresh_csrf()
            resp = self._session.delete(url, **kwargs)
        return self._handle_response(resp)

    # ── Top-level shortcuts ───────────────────────────────────────────

    def user_id(self) -> int:
        """Get the authenticated user's ID."""
        self.require_auth("user_id")
        return self.users.get_authenticated_user()["id"]

    def username(self) -> str:
        """Get the authenticated user's username."""
        self.require_auth("username")
        return self.users.get_authenticated_user()["name"]

    def display_name(self) -> str:
        """Get the authenticated user's display name."""
        self.require_auth("display_name")
        return self.users.get_authenticated_user()["displayName"]

    def robux(self) -> int:
        """Deprecated: use economy.get_robux_balance() directly."""
        raise NotImplementedError("Use client.economy.get_robux_balance(user_id) instead.")
        """Get the authenticated user's Robux balance."""
        self.require_auth("robux")
        uid = self.user_id()
        return self.economy.get_robux_balance(uid).robux

    def total_rap(self) -> int:
        """Get total RAP (Recent Average Price) of authenticated user's limiteds."""
        self.require_auth("total_rap")
        uid = self.user_id()
        return self.inventory.get_total_rap(uid)

    def invalidate_cache(self) -> None:
        """Clear the entire response cache."""
        self._cache.clear()

    def cache_stats(self) -> dict:
        """Return cache utilization stats."""
        return self._cache.stats()

    def __repr__(self) -> str:
        auth = "authenticated" if self.is_authenticated else "unauthenticated"
        cache = self._cache.stats()
        return f"<RoboatClient [{auth}] cache={cache['alive']}/{cache['max_size']}>"
