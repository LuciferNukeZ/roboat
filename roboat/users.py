"""
roboat.users
~~~~~~~~~~~~~~~
Users API — users.roblox.com
"""

from typing import List, Optional
from .models import User, Page


class UsersAPI:
    BASE = "https://users.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def get_user(self, user_id: int) -> User:
        """Get a user by their ID."""
        data = self._c._get(f"{self.BASE}/users/{user_id}")
        return User.from_dict(data)

    def get_authenticated_user(self) -> dict:
        """Get the authenticated user's basic info. Requires auth."""
        self._c.require_auth("get_authenticated_user")
        return self._c._get(f"{self.BASE}/users/authenticated")

    def get_users_by_ids(self, user_ids: List[int], exclude_banned: bool = False) -> List[User]:
        """Bulk-fetch users by ID (up to 100)."""
        data = self._c._post(
            f"{self.BASE}/users",
            json={"userIds": user_ids, "excludeBannedUsers": exclude_banned},
        )
        return [User.from_dict(u) for u in data.get("data", [])]

    def get_users_by_usernames(self, usernames: List[str], exclude_banned: bool = False) -> List[User]:
        """Bulk-fetch users by username (up to 100)."""
        data = self._c._post(
            f"{self.BASE}/usernames/users",
            json={"usernames": usernames, "excludeBannedUsers": exclude_banned},
        )
        return [User.from_dict(u) for u in data.get("data", [])]

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a single user by username. Returns None if not found."""
        results = self.get_users_by_usernames([username])
        return results[0] if results else None

    def search_users(self, keyword: str, limit: int = 10) -> Page:
        """Search users by keyword. Returns a Page of User objects."""
        data = self._c._get(
            f"{self.BASE}/users/search",
            params={"keyword": keyword, "limit": limit},
        )
        return Page.from_dict(data, User)

    def get_username_history(self, user_id: int, limit: int = 10,
                             cursor: Optional[str] = None) -> Page:
        """Get previous usernames for a user."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE}/users/{user_id}/username-history",
            params=params,
        )
        return Page.from_dict(data)

    def validate_username(self, username: str) -> dict:
        """
        Check if a username is available.
        Returns dict with 'code' (0 = valid/available) and 'message'.
        """
        return self._c._get(
            "https://auth.roblox.com/v1/usernames/validate",
            params={"Username": username, "Birthday": "2000-01-01"},
        )
