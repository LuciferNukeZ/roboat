"""
roboat.groups
~~~~~~~~~~~~~~~~
Groups API — groups.roblox.com
Full group management: roles, members, wall, shouts, payouts, join requests, relations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .models import Group, GroupRole, Page


@dataclass
class GroupShout:
    body: str
    poster_id: int
    poster_name: str
    created: str

    @classmethod
    def from_dict(cls, d: dict) -> "GroupShout":
        poster = d.get("poster", {})
        return cls(
            body=d.get("body", ""),
            poster_id=poster.get("userId", 0),
            poster_name=poster.get("username", ""),
            created=d.get("created", ""),
        )

    def __str__(self) -> str:
        return f"📣 {self.poster_name}: {self.body}"


@dataclass
class GroupPayout:
    recipient_id: int
    recipient_name: str
    recipient_type: str
    amount: int
    percentage: int

    @classmethod
    def from_dict(cls, d: dict) -> "GroupPayout":
        return cls(
            recipient_id=d.get("user", {}).get("userId", 0),
            recipient_name=d.get("user", {}).get("username", ""),
            recipient_type=d.get("recipientType", "User"),
            amount=d.get("amount", 0),
            percentage=d.get("percentage", 0),
        )

    def __str__(self) -> str:
        return f"💸 {self.recipient_name}: {self.amount}R$ ({self.percentage}%)"


@dataclass
class GroupJoinRequest:
    requester_id: int
    requester_name: str
    requester_display_name: str
    created: str

    @classmethod
    def from_dict(cls, d: dict) -> "GroupJoinRequest":
        requester = d.get("requester", {})
        return cls(
            requester_id=requester.get("userId", 0),
            requester_name=requester.get("username", ""),
            requester_display_name=requester.get("displayName", ""),
            created=d.get("created", ""),
        )

    def __str__(self) -> str:
        return f"👤 {self.requester_display_name} (@{self.requester_name}) [ID: {self.requester_id}]"


@dataclass
class GroupRelationship:
    group_id: int
    group_name: str
    relationship_type: str
    member_count: int

    @classmethod
    def from_dict(cls, d: dict) -> "GroupRelationship":
        return cls(
            group_id=d.get("id", 0),
            group_name=d.get("name", ""),
            relationship_type=d.get("relationshipType", ""),
            member_count=d.get("memberCount", 0),
        )


class GroupsAPI:
    BASE  = "https://groups.roblox.com/v1"
    BASE2 = "https://groups.roblox.com/v2"

    def __init__(self, client):
        self._c = client

    # ── Info ──────────────────────────────────────────────────────────

    def get_group(self, group_id: int) -> Group:
        data = self._c._get(f"{self.BASE}/groups/{group_id}")
        return Group.from_dict(data)

    def get_groups_by_ids(self, group_ids: List[int]) -> List[Group]:
        data = self._c._get(
            f"{self.BASE}/groups",
            params={"groupIds": ",".join(str(i) for i in group_ids)},
        )
        return [Group.from_dict(g.get("group", g)) for g in data.get("data", [])]

    def get_group_shout(self, group_id: int) -> Optional[GroupShout]:
        data = self._c._get(f"{self.BASE}/groups/{group_id}")
        shout_data = data.get("shout")
        return GroupShout.from_dict(shout_data) if shout_data else None

    def post_shout(self, group_id: int, message: str) -> dict:
        self._c.require_auth("post_shout")
        return self._c._patch(
            f"{self.BASE}/groups/{group_id}/status",
            json={"message": message},
        )

    # ── Roles & members ───────────────────────────────────────────────

    def get_roles(self, group_id: int) -> List[GroupRole]:
        data = self._c._get(f"{self.BASE}/groups/{group_id}/roles")
        roles = [GroupRole.from_dict(r) for r in data.get("roles", [])]
        return sorted(roles, key=lambda r: r.rank, reverse=True)

    def get_role_by_name(self, group_id: int, name: str) -> Optional[GroupRole]:
        for role in self.get_roles(group_id):
            if role.name.lower() == name.lower():
                return role
        return None

    def get_members(self, group_id: int, role_id: Optional[int] = None,
                    limit: int = 100, cursor: Optional[str] = None,
                    sort_order: str = "Asc") -> Page:
        params = {"limit": limit, "sortOrder": sort_order}
        if cursor: params["cursor"] = cursor
        if role_id:
            url = f"{self.BASE}/groups/{group_id}/roles/{role_id}/users"
        else:
            url = f"{self.BASE}/groups/{group_id}/users"
        return Page.from_dict(self._c._get(url, params=params))

    def get_member_role(self, group_id: int, user_id: int) -> Optional[dict]:
        try:
            data = self._c._get(f"{self.BASE2}/users/{user_id}/groups/roles")
            for entry in data.get("data", []):
                if entry.get("group", {}).get("id") == group_id:
                    return entry.get("role")
        except Exception:
            pass
        return None

    def set_member_role(self, group_id: int, user_id: int, role_id: int) -> None:
        self._c.require_auth("set_member_role")
        self._c._patch(
            f"{self.BASE}/groups/{group_id}/users/{user_id}",
            json={"roleId": role_id},
        )

    def kick_member(self, group_id: int, user_id: int) -> None:
        self._c.require_auth("kick_member")
        self._c._delete(f"{self.BASE}/groups/{group_id}/users/{user_id}")

    def get_member_count(self, group_id: int) -> int:
        return self._c._get(f"{self.BASE}/groups/{group_id}").get("memberCount", 0)

    def is_member(self, group_id: int, user_id: int) -> bool:
        return self.get_member_role(group_id, user_id) is not None

    # ── User groups ───────────────────────────────────────────────────

    def get_user_groups(self, user_id: int) -> list:
        data = self._c._get(f"{self.BASE2}/users/{user_id}/groups/roles")
        return data.get("data", [])

    def join_group(self, group_id: int) -> None:
        self._c.require_auth("join_group")
        self._c._post(f"{self.BASE}/groups/{group_id}/users")

    def leave_group(self, group_id: int) -> None:
        self._c.require_auth("leave_group")
        uid = self._c.user_id()
        self._c._delete(f"{self.BASE}/groups/{group_id}/users/{uid}")

    # ── Join requests ─────────────────────────────────────────────────

    def get_join_requests(self, group_id: int, limit: int = 100,
                          cursor: Optional[str] = None) -> Page:
        self._c.require_auth("get_join_requests")
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE}/groups/{group_id}/join-requests", params=params
        )
        requests = [GroupJoinRequest.from_dict(r) for r in data.get("data", [])]
        return Page(data=requests, next_cursor=data.get("nextPageCursor"))

    def accept_join_request(self, group_id: int, user_id: int) -> None:
        self._c.require_auth("accept_join_request")
        self._c._post(
            f"{self.BASE}/groups/{group_id}/join-requests/users/{user_id}"
        )

    def decline_join_request(self, group_id: int, user_id: int) -> None:
        self._c.require_auth("decline_join_request")
        self._c._delete(
            f"{self.BASE}/groups/{group_id}/join-requests/users/{user_id}"
        )

    def accept_all_join_requests(self, group_id: int) -> int:
        """Accept ALL pending join requests. Returns count accepted."""
        count = 0
        cursor = None
        while True:
            page = self.get_join_requests(group_id, limit=100, cursor=cursor)
            for req in page.data:
                try:
                    self.accept_join_request(group_id, req.requester_id)
                    count += 1
                except Exception:
                    pass
            cursor = page.next_cursor
            if not cursor:
                break
        return count

    # ── Wall ──────────────────────────────────────────────────────────

    def get_wall(self, group_id: int, limit: int = 100,
                 cursor: Optional[str] = None, sort_order: str = "Desc") -> Page:
        params = {"limit": limit, "sortOrder": sort_order}
        if cursor: params["cursor"] = cursor
        return Page.from_dict(
            self._c._get(f"{self.BASE}/groups/{group_id}/wall/posts", params=params)
        )

    def post_to_wall(self, group_id: int, message: str) -> dict:
        self._c.require_auth("post_to_wall")
        return self._c._post(
            f"{self.BASE}/groups/{group_id}/wall/posts", json={"body": message}
        )

    def delete_wall_post(self, group_id: int, post_id: int) -> None:
        self._c.require_auth("delete_wall_post")
        self._c._delete(
            f"{self.BASE}/groups/{group_id}/wall/posts/{post_id}"
        )

    # ── Payouts ───────────────────────────────────────────────────────

    def get_payouts(self, group_id: int) -> List[GroupPayout]:
        self._c.require_auth("get_payouts")
        data = self._c._get(f"{self.BASE}/groups/{group_id}/payouts")
        return [GroupPayout.from_dict(p) for p in data.get("data", [])]

    def pay_out(self, group_id: int, user_id: int, amount: int) -> None:
        """One-time Robux payout to a user from group funds."""
        self._c.require_auth("pay_out")
        self._c._post(
            f"{self.BASE}/groups/{group_id}/payouts",
            json={
                "PayoutType": "FixedAmount",
                "Recipients": [
                    {"recipientId": user_id, "recipientType": "User", "amount": amount}
                ],
            },
        )

    def set_recurring_payouts(self, group_id: int, recipients: List[dict]) -> None:
        """Set recurring percentage payouts. percentages must sum ≤ 100."""
        self._c.require_auth("set_recurring_payouts")
        self._c._post(
            f"{self.BASE}/groups/{group_id}/payouts/recurring",
            json={
                "PayoutType": "Percentage",
                "Recipients": [
                    {"recipientId": r["recipientId"], "recipientType": "User",
                     "amount": r["percentage"]}
                    for r in recipients
                ],
            },
        )

    # ── Relationships ─────────────────────────────────────────────────

    def get_allies(self, group_id: int, limit: int = 10) -> List[GroupRelationship]:
        data = self._c._get(
            f"{self.BASE}/groups/{group_id}/relationships/allies",
            params={"limit": limit},
        )
        return [GroupRelationship.from_dict(g) for g in data.get("relatedGroups", [])]

    def get_enemies(self, group_id: int, limit: int = 10) -> List[GroupRelationship]:
        data = self._c._get(
            f"{self.BASE}/groups/{group_id}/relationships/enemies",
            params={"limit": limit},
        )
        return [GroupRelationship.from_dict(g) for g in data.get("relatedGroups", [])]

    # ── Search ────────────────────────────────────────────────────────

    def search(self, keyword: str, limit: int = 10,
               cursor: Optional[str] = None) -> Page:
        params = {"keyword": keyword, "limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/groups/search", params=params)
        return Page(
            data=[Group.from_dict(g) for g in data.get("data", [])],
            next_cursor=data.get("nextPageCursor"),
        )

    def search_lookup(self, group_name: str) -> List[Group]:
        data = self._c._get(
            f"{self.BASE}/groups/search/lookup",
            params={"groupName": group_name},
        )
        return [Group.from_dict(g) for g in data.get("data", [])]

    # ── Audit & settings ──────────────────────────────────────────────

    def get_audit_log(self, group_id: int, action_type: str = "",
                      user_id: Optional[int] = None,
                      limit: int = 25, cursor: Optional[str] = None) -> Page:
        self._c.require_auth("get_audit_log")
        params = {"limit": limit}
        if action_type: params["actionType"] = action_type
        if user_id:     params["userId"] = user_id
        if cursor:      params["cursor"] = cursor
        return Page.from_dict(
            self._c._get(f"{self.BASE}/groups/{group_id}/audit-log", params=params)
        )

    def get_settings(self, group_id: int) -> dict:
        self._c.require_auth("get_settings")
        return self._c._get(f"{self.BASE}/groups/{group_id}/settings")

    def update_settings(self, group_id: int, **settings) -> dict:
        self._c.require_auth("update_settings")
        return self._c._patch(
            f"{self.BASE}/groups/{group_id}/settings", json=settings
        )

    def get_revenue_summary(self, group_id: int,
                             frequency: str = "Monthly") -> dict:
        self._c.require_auth("get_revenue_summary")
        return self._c._get(
            f"https://economy.roblox.com/v1/groups/{group_id}/revenue/summary/{frequency}"
        )
