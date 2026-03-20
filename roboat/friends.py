"""
roboat.friends
~~~~~~~~~~~~~~~~~
Friends API — friends.roblox.com
"""

from typing import Optional, List
from .models import Friend, Page


class FriendsAPI:
    BASE = "https://friends.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def get_friends(self, user_id: int) -> List[Friend]:
        """Get the full friends list for a user."""
        data = self._c._get(f"{self.BASE}/users/{user_id}/friends")
        return [Friend.from_dict(f) for f in data.get("data", [])]

    def get_friend_count(self, user_id: int) -> int:
        """Get the number of friends a user has."""
        data = self._c._get(f"{self.BASE}/users/{user_id}/friends/count")
        return data.get("count", 0)

    def get_followers(self, user_id: int, limit: int = 100,
                      cursor: Optional[str] = None) -> Page:
        """Get users who follow a given user."""
        params = {"limit": limit, "sortOrder": "Asc"}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/users/{user_id}/followers", params=params)
        return Page.from_dict(data, Friend)

    def get_follower_count(self, user_id: int) -> int:
        """Get the follower count for a user."""
        data = self._c._get(f"{self.BASE}/users/{user_id}/followers/count")
        return data.get("count", 0)

    def get_followings(self, user_id: int, limit: int = 100,
                       cursor: Optional[str] = None) -> Page:
        """Get users that a user is following."""
        params = {"limit": limit, "sortOrder": "Asc"}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/users/{user_id}/followings", params=params)
        return Page.from_dict(data, Friend)

    def get_following_count(self, user_id: int) -> int:
        """Get how many users a user is following."""
        data = self._c._get(f"{self.BASE}/users/{user_id}/followings/count")
        return data.get("count", 0)

    def get_friend_requests(self, limit: int = 20,
                            cursor: Optional[str] = None) -> Page:
        """Get pending friend requests. Requires auth."""
        self._c.require_auth("get_friend_requests")
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/my/friends/requests", params=params)
        return Page.from_dict(data, Friend)

    def send_friend_request(self, user_id: int) -> None:
        """Send a friend request. Requires auth."""
        self._c.require_auth("send_friend_request")
        self._c._post(f"{self.BASE}/users/{user_id}/request-friendship")

    def unfriend(self, user_id: int) -> None:
        """Unfriend a user. Requires auth."""
        self._c.require_auth("unfriend")
        self._c._post(f"{self.BASE}/users/{user_id}/unfriend")

    def accept_friend_request(self, user_id: int) -> None:
        """Accept a friend request. Requires auth."""
        self._c.require_auth("accept_friend_request")
        self._c._post(f"{self.BASE}/users/{user_id}/accept-friend-request")

    def decline_friend_request(self, user_id: int) -> None:
        """Decline a friend request. Requires auth."""
        self._c.require_auth("decline_friend_request")
        self._c._post(f"{self.BASE}/users/{user_id}/decline-friend-request")
