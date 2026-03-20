"""
roboat.develop
~~~~~~~~~~~~~~
Developer / Publishing API — develop.roblox.com + Open Cloud
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any
from .models import Page
import requests as _req
import json as _json


@dataclass
class Universe:
    id: int
    name: str
    description: str
    created: str
    updated: str
    root_place_id: int
    is_archived: bool
    is_active: bool
    privacy_type: str
    creator_type: str
    creator_id: int
    creator_name: str

    @classmethod
    def from_dict(cls, d: dict) -> "Universe":
        creator = d.get("creator", {})
        return cls(
            id=d.get("id", 0), name=d.get("name", ""),
            description=d.get("description", ""),
            created=d.get("created", ""), updated=d.get("updated", ""),
            root_place_id=d.get("rootPlaceId", 0),
            is_archived=d.get("isArchived", False),
            is_active=d.get("isActive", True),
            privacy_type=d.get("privacyType", ""),
            creator_type=creator.get("type", ""),
            creator_id=creator.get("id", 0),
            creator_name=creator.get("name", ""),
        )

    def __str__(self) -> str:
        status = "Active" if self.is_active else "Inactive"
        arch = " [Archived]" if self.is_archived else ""
        return f"Universe: {self.name}{arch} [ID: {self.id}] {status}"


@dataclass
class Place:
    id: int
    universe_id: int
    name: str
    description: str
    max_players: int
    server_fill: str
    is_root_place: bool

    @classmethod
    def from_dict(cls, d: dict) -> "Place":
        return cls(
            id=d.get("id", 0), universe_id=d.get("universeId", 0),
            name=d.get("name", ""), description=d.get("description", ""),
            max_players=d.get("maxPlayerCount", 0),
            server_fill=d.get("socialSlotType", ""),
            is_root_place=d.get("isRootPlace", False),
        )


@dataclass
class DataStore:
    name: str
    created: str

    @classmethod
    def from_dict(cls, d: dict) -> "DataStore":
        return cls(name=d.get("name", ""), created=d.get("createdTime", ""))


@dataclass
class PlaceVersion:
    version_number: int
    version_type: str
    created: str
    creator_id: int
    creator_type: str

    @classmethod
    def from_dict(cls, d: dict) -> "PlaceVersion":
        return cls(
            version_number=d.get("versionNumber", 0),
            version_type=d.get("versionType", ""),
            created=d.get("created", ""),
            creator_id=d.get("creatorTargetId", 0),
            creator_type=d.get("creatorType", ""),
        )


@dataclass
class TeamCreateMember:
    user_id: int
    username: str
    display_name: str

    @classmethod
    def from_dict(cls, d: dict) -> "TeamCreateMember":
        return cls(
            user_id=d.get("id", 0),
            username=d.get("name", ""),
            display_name=d.get("displayName", ""),
        )


@dataclass
class PluginInfo:
    id: int
    name: str
    description: str
    comments_enabled: bool
    version_id: int

    @classmethod
    def from_dict(cls, d: dict) -> "PluginInfo":
        return cls(
            id=d.get("id", 0), name=d.get("name", ""),
            description=d.get("description", ""),
            comments_enabled=d.get("commentsEnabled", False),
            version_id=d.get("versionId", 0),
        )


class DevelopAPI:
    BASE    = "https://develop.roblox.com/v1"
    BASE2   = "https://develop.roblox.com/v2"
    CLOUD   = "https://apis.roblox.com/datastores/v1"
    ODS     = "https://apis.roblox.com/ordered-data-stores/v1"
    MSGR    = "https://apis.roblox.com/messaging-service/v1"
    OCCLOUD = "https://apis.roblox.com/cloud/v2"

    def __init__(self, client):
        self._c = client

    # ── Universes ─────────────────────────────────────────────────────

    def get_universes_by_user(self, user_id: int, is_archived: bool = False,
                               limit: int = 50, cursor: Optional[str] = None) -> Page:
        params = {"isArchived": is_archived, "limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/user/universes", params=params)
        return Page(data=[Universe.from_dict(u) for u in data.get("data", [])],
                    next_cursor=data.get("nextPageCursor"))

    def get_universes_by_group(self, group_id: int, is_archived: bool = False,
                                limit: int = 50, cursor: Optional[str] = None) -> Page:
        params = {"isArchived": is_archived, "limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/groups/{group_id}/universes", params=params)
        return Page(data=[Universe.from_dict(u) for u in data.get("data", [])],
                    next_cursor=data.get("nextPageCursor"))

    def get_universe(self, universe_id: int) -> Universe:
        return Universe.from_dict(self._c._get(f"{self.BASE}/universes/{universe_id}"))

    def get_multiverse_details(self, universe_ids: List[int]) -> List[Universe]:
        data = self._c._get(
            f"{self.BASE}/universes/multiget",
            params={"ids": ",".join(str(i) for i in universe_ids)},
        )
        return [Universe.from_dict(u) for u in data.get("data", [])]

    def get_universe_settings(self, universe_id: int) -> dict:
        self._c.require_auth("get_universe_settings")
        return self._c._get(f"{self.BASE}/universes/{universe_id}/configuration")

    def update_universe_settings(self, universe_id: int, **settings) -> dict:
        self._c.require_auth("update_universe_settings")
        return self._c._patch(
            f"{self.BASE}/universes/{universe_id}/configuration", json=settings
        )

    def activate_universe(self, universe_id: int) -> None:
        self._c.require_auth("activate_universe")
        self._c._post(f"{self.BASE}/universes/{universe_id}/activate")

    def deactivate_universe(self, universe_id: int) -> None:
        self._c.require_auth("deactivate_universe")
        self._c._post(f"{self.BASE}/universes/{universe_id}/deactivate")

    # ── Places ────────────────────────────────────────────────────────

    def get_places(self, universe_id: int, limit: int = 10,
                   cursor: Optional[str] = None) -> Page:
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/universes/{universe_id}/places", params=params)
        return Page(data=[Place.from_dict(p) for p in data.get("data", [])],
                    next_cursor=data.get("nextPageCursor"))

    def update_place(self, place_id: int, universe_id: int,
                     name: Optional[str] = None,
                     description: Optional[str] = None,
                     max_players: Optional[int] = None) -> dict:
        self._c.require_auth("update_place")
        payload = {}
        if name is not None:        payload["name"] = name
        if description is not None: payload["description"] = description
        if max_players is not None: payload["maxPlayerCount"] = max_players
        return self._c._patch(
            f"{self.BASE}/universes/{universe_id}/places/{place_id}/configuration",
            json=payload,
        )

    def get_place_versions(self, place_id: int, limit: int = 10,
                           cursor: Optional[str] = None) -> Page:
        self._c.require_auth("get_place_versions")
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/places/{place_id}/versions", params=params)
        return Page(data=[PlaceVersion.from_dict(v) for v in data.get("data", [])],
                    next_cursor=data.get("nextPageCursor"))

    # ── Stats ─────────────────────────────────────────────────────────

    def get_game_stats(self, universe_id: int, stat_type: str = "Visits",
                       granularity: str = "Daily",
                       start_time: Optional[str] = None,
                       end_time: Optional[str] = None) -> List[dict]:
        self._c.require_auth("get_game_stats")
        params = {"type": stat_type, "granularity": granularity}
        if start_time: params["startTime"] = start_time
        if end_time:   params["endTime"] = end_time
        return self._c._get(
            f"{self.BASE}/universes/{universe_id}/stats", params=params
        ).get("data", [])

    def get_revenue_summary(self, universe_id: int, granularity: str = "Monthly") -> dict:
        self._c.require_auth("get_revenue_summary")
        return self._c._get(
            f"{self.BASE}/universes/{universe_id}/revenue/summary/{granularity}"
        )

    # ── Team Create ────────────────────────────────────────────────────

    def get_team_create_settings(self, universe_id: int) -> dict:
        self._c.require_auth("get_team_create_settings")
        return self._c._get(f"{self.BASE}/universes/{universe_id}/teamcreate")

    def update_team_create(self, universe_id: int, is_enabled: bool) -> dict:
        self._c.require_auth("update_team_create")
        return self._c._patch(
            f"{self.BASE}/universes/{universe_id}/teamcreate",
            json={"isEnabled": is_enabled},
        )

    def get_team_create_members(self, universe_id: int, limit: int = 50,
                                 cursor: Optional[str] = None) -> Page:
        self._c.require_auth("get_team_create_members")
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE}/universes/{universe_id}/teamcreate/memberships",
            params=params,
        )
        return Page(data=[TeamCreateMember.from_dict(m) for m in data.get("data", [])],
                    next_cursor=data.get("nextPageCursor"))

    def add_team_create_member(self, universe_id: int, user_id: int) -> None:
        self._c.require_auth("add_team_create_member")
        self._c._post(
            f"{self.BASE}/universes/{universe_id}/teamcreate/memberships",
            json={"userId": user_id},
        )

    def remove_team_create_member(self, universe_id: int, user_id: int) -> None:
        self._c.require_auth("remove_team_create_member")
        self._c._delete(
            f"{self.BASE}/universes/{universe_id}/teamcreate/memberships",
            params={"userId": user_id},
        )

    # ── Plugins ───────────────────────────────────────────────────────

    def get_plugins(self, plugin_ids: List[int]) -> List[PluginInfo]:
        data = self._c._get(
            f"{self.BASE}/plugins",
            params={"pluginIds": ",".join(str(i) for i in plugin_ids)},
        )
        return [PluginInfo.from_dict(p) for p in data.get("data", [])]

    def update_plugin(self, plugin_id: int, name: Optional[str] = None,
                      description: Optional[str] = None,
                      comments_enabled: Optional[bool] = None) -> None:
        self._c.require_auth("update_plugin")
        payload = {}
        if name is not None:             payload["name"] = name
        if description is not None:      payload["description"] = description
        if comments_enabled is not None: payload["commentsEnabled"] = comments_enabled
        self._c._patch(f"{self.BASE}/plugins/{plugin_id}", json=payload)

    # ── DataStores (Open Cloud) ────────────────────────────────────────

    def _cloud_headers(self, api_key: str) -> dict:
        return {"x-api-key": api_key, "Content-Type": "application/json"}

    def list_datastores(self, universe_id: int, api_key: str,
                        prefix: str = "", limit: int = 100) -> List[DataStore]:
        r = _req.get(
            f"{self.CLOUD}/universes/{universe_id}/standard-datastores",
            params={"prefix": prefix, "limit": limit},
            headers={"x-api-key": api_key},
        )
        r.raise_for_status()
        return [DataStore.from_dict(d) for d in r.json().get("datastores", [])]

    def get_datastore_entry(self, universe_id: int, datastore_name: str,
                             entry_key: str, api_key: str,
                             scope: str = "global") -> Any:
        r = _req.get(
            f"{self.CLOUD}/universes/{universe_id}/standard-datastores/datastore/entries/entry",
            params={"datastoreName": datastore_name, "entryKey": entry_key, "scope": scope},
            headers={"x-api-key": api_key},
        )
        if r.status_code == 404: return None
        r.raise_for_status()
        try: return r.json()
        except Exception: return r.text

    def set_datastore_entry(self, universe_id: int, datastore_name: str,
                             entry_key: str, value: Any, api_key: str,
                             scope: str = "global",
                             user_ids: Optional[List[int]] = None) -> dict:
        headers = {"x-api-key": api_key, "Content-Type": "application/json"}
        if user_ids:
            headers["roblox-entry-userids"] = _json.dumps(user_ids)
        r = _req.post(
            f"{self.CLOUD}/universes/{universe_id}/standard-datastores/datastore/entries/entry",
            params={"datastoreName": datastore_name, "entryKey": entry_key, "scope": scope},
            headers=headers,
            data=_json.dumps(value),
        )
        r.raise_for_status()
        return r.json()

    def increment_datastore_entry(self, universe_id: int, datastore_name: str,
                                   entry_key: str, delta: float,
                                   api_key: str, scope: str = "global") -> Any:
        r = _req.post(
            f"{self.CLOUD}/universes/{universe_id}/standard-datastores/datastore/entries/entry/increment",
            params={"datastoreName": datastore_name, "entryKey": entry_key,
                    "scope": scope, "incrementBy": delta},
            headers={"x-api-key": api_key},
        )
        r.raise_for_status()
        try: return r.json()
        except Exception: return r.text

    def delete_datastore_entry(self, universe_id: int, datastore_name: str,
                                entry_key: str, api_key: str,
                                scope: str = "global") -> None:
        r = _req.delete(
            f"{self.CLOUD}/universes/{universe_id}/standard-datastores/datastore/entries/entry",
            params={"datastoreName": datastore_name, "entryKey": entry_key, "scope": scope},
            headers={"x-api-key": api_key},
        )
        if r.status_code not in (200, 404): r.raise_for_status()

    def list_datastore_keys(self, universe_id: int, datastore_name: str,
                             api_key: str, scope: str = "global",
                             prefix: str = "", limit: int = 100,
                             cursor: Optional[str] = None) -> dict:
        params = {"datastoreName": datastore_name, "scope": scope,
                  "prefix": prefix, "limit": limit}
        if cursor: params["cursor"] = cursor
        r = _req.get(
            f"{self.CLOUD}/universes/{universe_id}/standard-datastores/datastore/entries",
            params=params, headers={"x-api-key": api_key},
        )
        r.raise_for_status()
        return r.json()

    def list_datastore_versions(self, universe_id: int, datastore_name: str,
                                 entry_key: str, api_key: str,
                                 scope: str = "global", limit: int = 10) -> dict:
        r = _req.get(
            f"{self.CLOUD}/universes/{universe_id}/standard-datastores/datastore/entries/entry/versions",
            params={"datastoreName": datastore_name, "entryKey": entry_key,
                    "scope": scope, "limit": limit},
            headers={"x-api-key": api_key},
        )
        r.raise_for_status()
        return r.json()

    # ── Ordered DataStores ─────────────────────────────────────────────

    def list_ordered_datastore(self, universe_id: int, datastore_name: str,
                                api_key: str, scope: str = "global",
                                max_page_size: int = 10,
                                order_by: str = "desc") -> dict:
        r = _req.get(
            f"{self.ODS}/universes/{universe_id}/orderedDataStores/{datastore_name}/scopes/{scope}/entries",
            params={"max_page_size": max_page_size, "order_by": order_by},
            headers={"x-api-key": api_key},
        )
        r.raise_for_status()
        return r.json()

    def set_ordered_datastore_entry(self, universe_id: int, datastore_name: str,
                                     entry_key: str, value: int, api_key: str,
                                     scope: str = "global",
                                     allow_missing: bool = True) -> dict:
        params = {}
        if allow_missing: params["allow_missing"] = "true"
        r = _req.patch(
            f"{self.ODS}/universes/{universe_id}/orderedDataStores/{datastore_name}/scopes/{scope}/entries/{entry_key}",
            params=params, json={"value": value},
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json()

    def increment_ordered_datastore(self, universe_id: int, datastore_name: str,
                                     entry_key: str, amount: int,
                                     api_key: str, scope: str = "global") -> dict:
        r = _req.post(
            f"{self.ODS}/universes/{universe_id}/orderedDataStores/{datastore_name}/scopes/{scope}/entries/{entry_key}:increment",
            json={"amount": amount},
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json()

    # ── MessagingService ───────────────────────────────────────────────

    def publish_message(self, universe_id: int, topic: str,
                        message: str, api_key: str) -> None:
        r = _req.post(
            f"{self.MSGR}/universes/{universe_id}/topics/{topic}",
            json={"message": message},
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        r.raise_for_status()

    def broadcast_shutdown(self, universe_id: int, api_key: str,
                            message: str = "Server shutting down.") -> None:
        self.publish_message(universe_id, "ServerShutdown", message, api_key)

    def announce(self, universe_id: int, api_key: str, text: str) -> None:
        self.publish_message(universe_id, "GlobalAnnouncement", text, api_key)

    # ── Bans (Open Cloud) ──────────────────────────────────────────────

    def ban_user(self, universe_id: int, user_id: int, api_key: str,
                 duration_seconds: Optional[int] = None,
                 display_reason: str = "You have been banned.",
                 private_reason: str = "",
                 exclude_alt_accounts: bool = False) -> dict:
        payload: dict = {
            "gameJoinRestriction": {
                "active": True,
                "displayReason": display_reason,
                "privateReason": private_reason,
                "excludeAltAccounts": exclude_alt_accounts,
            }
        }
        if duration_seconds is not None:
            payload["gameJoinRestriction"]["duration"] = f"{duration_seconds}s"
        r = _req.patch(
            f"{self.OCCLOUD}/universes/{universe_id}/user-restrictions/{user_id}",
            json=payload,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json()

    def unban_user(self, universe_id: int, user_id: int, api_key: str) -> dict:
        r = _req.patch(
            f"{self.OCCLOUD}/universes/{universe_id}/user-restrictions/{user_id}",
            json={"gameJoinRestriction": {"active": False}},
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json()

    def get_ban_status(self, universe_id: int, user_id: int, api_key: str) -> dict:
        r = _req.get(
            f"{self.OCCLOUD}/universes/{universe_id}/user-restrictions/{user_id}",
            headers={"x-api-key": api_key},
        )
        r.raise_for_status()
        return r.json()

    def list_bans(self, universe_id: int, api_key: str,
                  max_page_size: int = 100,
                  page_token: Optional[str] = None) -> dict:
        params = {"maxPageSize": max_page_size}
        if page_token: params["pageToken"] = page_token
        r = _req.get(
            f"{self.OCCLOUD}/universes/{universe_id}/user-restrictions",
            params=params, headers={"x-api-key": api_key},
        )
        r.raise_for_status()
        return r.json()

    # ── Subscriptions ─────────────────────────────────────────────────

    def get_subscriptions(self, universe_id: int, limit: int = 10,
                           cursor: Optional[str] = None) -> Page:
        self._c.require_auth("get_subscriptions")
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        return Page.from_dict(
            self._c._get(f"{self.OCCLOUD}/universes/{universe_id}/subscriptions",
                         params=params)
        )
