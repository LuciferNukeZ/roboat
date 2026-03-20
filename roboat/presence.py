"""
roboat.presence
~~~~~~~~~~~~~~~~~~
Presence API — presence.roblox.com
"""

from typing import List
from .models import UserPresence


class PresenceAPI:
    BASE = "https://presence.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def get_presences(self, user_ids: List[int]) -> List[UserPresence]:
        """
        Get presence (online status + location) for multiple users.

        Presence types:
          0 = Offline
          1 = Online (website)
          2 = In Game
          3 = In Studio
        """
        data = self._c._post(
            f"{self.BASE}/presence/users",
            json={"userIds": user_ids},
        )
        return [UserPresence.from_dict(p) for p in data.get("userPresences", [])]

    def get_presence(self, user_id: int) -> UserPresence:
        """Get presence for a single user."""
        results = self.get_presences([user_id])
        return results[0] if results else UserPresence(user_id=user_id)

    def register_app_presence(self, universe_id: int, place_id: int,
                               game_id: str) -> None:
        """Register presence in a game (requires auth)."""
        self._c.require_auth("register_app_presence")
        self._c._post(
            f"{self.BASE}/presence/register-app-presence",
            json={
                "universeId": universe_id,
                "placeId": place_id,
                "gameId": game_id,
            },
        )
