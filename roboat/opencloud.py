"""
roboat.opencloud
~~~~~~~~~~~~~~~~~~~
Roblox Open Cloud API — apis.roblox.com/cloud/v2
The modern, API-key authenticated developer API.

Unlike the cookie-based APIs, Open Cloud uses API keys with fine-grained
permission scopes. Get your key at: https://create.roblox.com/dashboard/credentials

Covers:
  - DataStores (read/write/list/delete)
  - Ordered DataStores
  - MessagingService (publish to topics)
  - Instances (read game hierarchy)
  - Subscriptions
  - User restrictions (ban/unban)

Example::

    from roboat import RoboatCloudClient

    cloud = RoboatCloudClient(api_key="roblox-KEY-xxxxx")

    # Write a datastore entry
    cloud.datastores.set(
        universe_id=123456,
        datastore="PlayerData",
        key="player_1234",
        value={"coins": 500, "level": 10},
    )

    # Publish a message to all game servers
    cloud.messaging.publish(
        universe_id=123456,
        topic="ServerAnnouncement",
        message="Update deploying in 5 minutes!",
    )
"""

from __future__ import annotations
import json
import requests
from typing import Any, Dict, List, Optional
from .exceptions import RobloxAPIError


class RoboatCloudClient:
    """
    Open Cloud client using API key authentication.

    Args:
        api_key: Your Roblox Open Cloud API key.
        timeout: Request timeout in seconds.

    Example::

        cloud = RoboatCloudClient(api_key="roblox-KEY-xxxxx")
        cloud.datastores.set(123456, "Store", "key", {"value": 1})
    """

    BASE = "https://apis.roblox.com/cloud/v2"
    DS_BASE = "https://apis.roblox.com/datastores/v1"
    ODS_BASE = "https://apis.roblox.com/ordered-data-stores/v1"

    def __init__(self, api_key: str, timeout: int = 10):
        self._key = api_key
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self.datastores = _DataStoreAPI(self)
        self.ordered_datastores = _OrderedDataStoreAPI(self)
        self.messaging = _MessagingAPI(self)
        self.instances = _InstancesAPI(self)
        self.users = _OpenCloudUsersAPI(self)

    def _get(self, url: str, **kwargs) -> Any:
        kwargs.setdefault("timeout", self._timeout)
        r = self._session.get(url, **kwargs)
        return self._handle(r)

    def _post(self, url: str, **kwargs) -> Any:
        kwargs.setdefault("timeout", self._timeout)
        r = self._session.post(url, **kwargs)
        return self._handle(r)

    def _patch(self, url: str, **kwargs) -> Any:
        kwargs.setdefault("timeout", self._timeout)
        r = self._session.patch(url, **kwargs)
        return self._handle(r)

    def _delete(self, url: str, **kwargs) -> Any:
        kwargs.setdefault("timeout", self._timeout)
        r = self._session.delete(url, **kwargs)
        return self._handle(r)

    def _handle(self, r: requests.Response) -> Any:
        if not r.ok:
            try:
                msg = r.json().get("message", r.text)
            except Exception:
                msg = r.text
            raise RobloxAPIError(f"HTTP {r.status_code}: {msg}")
        try:
            return r.json()
        except Exception:
            return r.text


class _DataStoreAPI:
    """Standard DataStore operations via Open Cloud."""

    def __init__(self, cloud: RoboatCloudClient):
        self._c = cloud

    def list_stores(self, universe_id: int,
                    prefix: str = "", limit: int = 100) -> List[dict]:
        """List all DataStores in a universe."""
        data = self._c._get(
            f"{self._c.DS_BASE}/universes/{universe_id}/standard-datastores",
            params={"prefix": prefix, "limit": limit},
        )
        return data.get("datastores", [])

    def list_keys(self, universe_id: int, datastore: str,
                  scope: str = "global", prefix: str = "",
                  limit: int = 100, cursor: Optional[str] = None) -> dict:
        """List all keys in a DataStore."""
        params = {
            "datastoreName": datastore,
            "scope": scope,
            "prefix": prefix,
            "limit": limit,
        }
        if cursor:
            params["cursor"] = cursor
        return self._c._get(
            f"{self._c.DS_BASE}/universes/{universe_id}/standard-datastores/datastore/entries",
            params=params,
        )

    def get(self, universe_id: int, datastore: str, key: str,
            scope: str = "global") -> Any:
        """
        Get a DataStore entry value.

        Returns:
            The raw value (dict, list, str, int, etc.)
        """
        r = self._c._session.get(
            f"{self._c.DS_BASE}/universes/{universe_id}/standard-datastores/datastore/entries/entry",
            params={"datastoreName": datastore, "entryKey": key, "scope": scope},
            timeout=self._c._timeout,
        )
        if r.status_code == 404:
            return None
        if not r.ok:
            raise RobloxAPIError(f"HTTP {r.status_code}: {r.text}")
        try:
            return r.json()
        except Exception:
            return r.text

    def set(self, universe_id: int, datastore: str, key: str,
            value: Any, scope: str = "global",
            match_version: Optional[str] = None,
            exclusive_create: bool = False,
            user_ids: Optional[List[int]] = None,
            attributes: Optional[dict] = None) -> dict:
        """
        Set a DataStore entry.

        Args:
            value: Any JSON-serialisable value.
            match_version: Only update if current version matches (optimistic lock).
            exclusive_create: Only set if key does not already exist.
            user_ids: Associate user IDs with this entry (for GDPR compliance).
            attributes: Arbitrary metadata dict.

        Returns:
            dict with version info.
        """
        params = {"datastoreName": datastore, "entryKey": key, "scope": scope}
        if match_version:     params["matchVersion"] = match_version
        if exclusive_create:  params["exclusiveCreate"] = "true"
        headers = {}
        if user_ids:
            headers["roblox-entry-userids"] = json.dumps(user_ids)
        if attributes:
            headers["roblox-entry-attributes"] = json.dumps(attributes)
        r = self._c._session.post(
            f"{self._c.DS_BASE}/universes/{universe_id}/standard-datastores/datastore/entries/entry",
            params=params,
            headers=headers,
            data=json.dumps(value),
            timeout=self._c._timeout,
        )
        if not r.ok:
            raise RobloxAPIError(f"HTTP {r.status_code}: {r.text}")
        return r.json()

    def increment(self, universe_id: int, datastore: str, key: str,
                  delta: float, scope: str = "global") -> Any:
        """Increment a numeric DataStore value by delta."""
        r = self._c._session.post(
            f"{self._c.DS_BASE}/universes/{universe_id}/standard-datastores/datastore/entries/entry/increment",
            params={"datastoreName": datastore, "entryKey": key,
                    "scope": scope, "incrementBy": delta},
            timeout=self._c._timeout,
        )
        if not r.ok:
            raise RobloxAPIError(f"HTTP {r.status_code}: {r.text}")
        try:
            return r.json()
        except Exception:
            return r.text

    def delete(self, universe_id: int, datastore: str, key: str,
               scope: str = "global") -> None:
        """Delete a DataStore entry."""
        r = self._c._session.delete(
            f"{self._c.DS_BASE}/universes/{universe_id}/standard-datastores/datastore/entries/entry",
            params={"datastoreName": datastore, "entryKey": key, "scope": scope},
            timeout=self._c._timeout,
        )
        if not r.ok and r.status_code != 404:
            raise RobloxAPIError(f"HTTP {r.status_code}: {r.text}")

    def list_versions(self, universe_id: int, datastore: str, key: str,
                      scope: str = "global", limit: int = 10) -> dict:
        """List all versions of a DataStore entry."""
        return self._c._get(
            f"{self._c.DS_BASE}/universes/{universe_id}/standard-datastores/datastore/entries/entry/versions",
            params={"datastoreName": datastore, "entryKey": key,
                    "scope": scope, "limit": limit},
        )

    def get_version(self, universe_id: int, datastore: str, key: str,
                    version_id: str, scope: str = "global") -> Any:
        """Get a specific historical version of a DataStore entry."""
        r = self._c._session.get(
            f"{self._c.DS_BASE}/universes/{universe_id}/standard-datastores/datastore/entries/entry/versions/version",
            params={"datastoreName": datastore, "entryKey": key,
                    "versionId": version_id, "scope": scope},
            timeout=self._c._timeout,
        )
        if not r.ok:
            raise RobloxAPIError(f"HTTP {r.status_code}: {r.text}")
        try:
            return r.json()
        except Exception:
            return r.text


class _OrderedDataStoreAPI:
    """Ordered DataStore (leaderboard-style) operations."""

    def __init__(self, cloud: RoboatCloudClient):
        self._c = cloud

    def list(self, universe_id: int, datastore: str,
             scope: str = "global", max_page_size: int = 10,
             order_by: str = "desc", filter_str: Optional[str] = None,
             page_token: Optional[str] = None) -> dict:
        """
        List entries in an Ordered DataStore (sorted by value).

        Args:
            order_by: "desc" (highest first) or "asc" (lowest first)
            filter_str: e.g. "entry >= 100 && entry <= 500"

        Returns:
            dict with entries[] and nextPageToken.
        """
        params = {
            "max_page_size": max_page_size,
            "order_by": order_by,
        }
        if filter_str:  params["filter"] = filter_str
        if page_token:  params["page_token"] = page_token
        return self._c._get(
            f"{self._c.ODS_BASE}/universes/{universe_id}/orderedDataStores/{datastore}/scopes/{scope}/entries",
            params=params,
        )

    def get(self, universe_id: int, datastore: str, key: str,
            scope: str = "global") -> dict:
        return self._c._get(
            f"{self._c.ODS_BASE}/universes/{universe_id}/orderedDataStores/{datastore}/scopes/{scope}/entries/{key}"
        )

    def create(self, universe_id: int, datastore: str, key: str,
               value: int, scope: str = "global") -> dict:
        return self._c._post(
            f"{self._c.ODS_BASE}/universes/{universe_id}/orderedDataStores/{datastore}/scopes/{scope}/entries",
            params={"id": key},
            json={"value": value},
        )

    def update(self, universe_id: int, datastore: str, key: str,
               value: int, scope: str = "global",
               allow_missing: bool = False) -> dict:
        """Update an entry's value. Set allow_missing=True to upsert."""
        params = {}
        if allow_missing:
            params["allow_missing"] = "true"
        return self._c._patch(
            f"{self._c.ODS_BASE}/universes/{universe_id}/orderedDataStores/{datastore}/scopes/{scope}/entries/{key}",
            params=params,
            json={"value": value},
        )

    def increment(self, universe_id: int, datastore: str, key: str,
                  by: int, scope: str = "global") -> dict:
        return self._c._post(
            f"{self._c.ODS_BASE}/universes/{universe_id}/orderedDataStores/{datastore}/scopes/{scope}/entries/{key}:increment",
            json={"amount": by},
        )

    def delete(self, universe_id: int, datastore: str, key: str,
               scope: str = "global") -> None:
        self._c._delete(
            f"{self._c.ODS_BASE}/universes/{universe_id}/orderedDataStores/{datastore}/scopes/{scope}/entries/{key}"
        )


class _MessagingAPI:
    """MessagingService — publish to all running game servers."""

    def __init__(self, cloud: RoboatCloudClient):
        self._c = cloud

    def publish(self, universe_id: int, topic: str, message: str) -> None:
        """
        Publish a message to a topic. All live servers subscribed to this
        topic via MessagingService:SubscribeAsync will receive it instantly.

        Args:
            universe_id: The universe to target.
            topic: Topic name (max 80 chars).
            message: Message content (max 1024 chars after base64 encoding).
        """
        self._c._post(
            f"https://apis.roblox.com/messaging-service/v1/universes/{universe_id}/topics/{topic}",
            json={"message": message},
        )

    def publish_shutdown(self, universe_id: int,
                         message: str = "Server shutting down.") -> None:
        """Convenience: broadcast a shutdown announcement to all servers."""
        self.publish(universe_id, "ServerShutdown", message)

    def announce(self, universe_id: int, text: str) -> None:
        """Convenience: broadcast a server-wide announcement."""
        self.publish(universe_id, "GlobalAnnouncement", text)


class _InstancesAPI:
    """Read the game hierarchy (place instances) via Open Cloud."""

    def __init__(self, cloud: RoboatCloudClient):
        self._c = cloud

    def get_instance(self, universe_id: int, place_id: int,
                     instance_id: str = "root") -> dict:
        """
        Get an instance from the place hierarchy.

        Args:
            instance_id: The instance's UUID, or "root" for the DataModel.

        Returns:
            dict with id, name, parent, details, hasChildren, engineInstance.
        """
        return self._c._get(
            f"{self._c.BASE}/universes/{universe_id}/places/{place_id}/instances/{instance_id}"
        )

    def get_children(self, universe_id: int, place_id: int,
                     instance_id: str = "root") -> dict:
        """List the children of an instance."""
        return self._c._get(
            f"{self._c.BASE}/universes/{universe_id}/places/{place_id}/instances/{instance_id}/children"
        )


class _OpenCloudUsersAPI:
    """User-related Open Cloud endpoints (restrictions, info)."""

    def __init__(self, cloud: RoboatCloudClient):
        self._c = cloud

    def get_user_restriction(self, universe_id: int, user_id: int) -> dict:
        """
        Get the ban/restriction status of a user in a universe.

        Returns:
            dict with active, startTime, duration, privateReason, displayReason
        """
        return self._c._get(
            f"{self._c.BASE}/universes/{universe_id}/user-restrictions/{user_id}"
        )

    def ban_user(self, universe_id: int, user_id: int,
                 duration: Optional[int] = None,
                 display_reason: str = "You have been banned.",
                 private_reason: str = "",
                 exclude_alt_accounts: bool = False) -> dict:
        """
        Ban a user from a universe.

        Args:
            duration: Ban duration in seconds. None = permanent.
            display_reason: Shown to the player.
            private_reason: Internal notes (not shown to player).
            exclude_alt_accounts: If False, alt accounts are also banned.

        Returns:
            dict with restriction details.
        """
        payload: dict = {
            "gameJoinRestriction": {
                "active": True,
                "displayReason": display_reason,
                "privateReason": private_reason,
                "excludeAltAccounts": exclude_alt_accounts,
            }
        }
        if duration is not None:
            payload["gameJoinRestriction"]["duration"] = f"{duration}s"
        return self._c._patch(
            f"{self._c.BASE}/universes/{universe_id}/user-restrictions/{user_id}",
            json=payload,
        )

    def unban_user(self, universe_id: int, user_id: int) -> dict:
        """Remove a ban from a user."""
        return self._c._patch(
            f"{self._c.BASE}/universes/{universe_id}/user-restrictions/{user_id}",
            json={"gameJoinRestriction": {"active": False}},
        )

    def list_restrictions(self, universe_id: int,
                          max_page_size: int = 100,
                          page_token: Optional[str] = None) -> dict:
        """List all active user restrictions in a universe."""
        params = {"maxPageSize": max_page_size}
        if page_token:
            params["pageToken"] = page_token
        return self._c._get(
            f"{self._c.BASE}/universes/{universe_id}/user-restrictions",
            params=params,
        )
