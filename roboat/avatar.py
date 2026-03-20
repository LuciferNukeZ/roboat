"""
roboat.avatar
~~~~~~~~~~~~~~~~
Avatar API — avatar.roblox.com
"""

from .models import Avatar, Page


class AvatarAPI:
    BASE = "https://avatar.roblox.com/v1"
    BASE2 = "https://avatar.roblox.com/v2"

    def __init__(self, client):
        self._c = client

    def get_user_avatar(self, user_id: int) -> Avatar:
        """Get the full avatar for a user."""
        data = self._c._get(f"{self.BASE}/users/{user_id}/avatar")
        return Avatar.from_dict(user_id, data)

    def get_authenticated_avatar(self) -> Avatar:
        """Get the authenticated user's avatar. Requires auth."""
        self._c.require_auth("get_authenticated_avatar")
        uid = self._c.users.get_authenticated_user()["id"]
        data = self._c._get(f"{self.BASE}/avatar")
        return Avatar.from_dict(uid, data)

    def get_avatar_rules(self) -> dict:
        """Get all avatar rules (allowed scales, asset types, etc.)."""
        return self._c._get(f"{self.BASE}/avatar-rules")

    def get_outfit(self, outfit_id: int) -> dict:
        """Get details for a saved outfit."""
        return self._c._get(f"{self.BASE}/outfits/{outfit_id}/details")

    def get_user_outfits(self, user_id: int, page: int = 1,
                         items_per_page: int = 25,
                         is_editable: bool = False) -> dict:
        """Get outfits for a user."""
        return self._c._get(
            f"{self.BASE}/users/{user_id}/outfits",
            params={"page": page, "itemsPerPage": items_per_page,
                    "isEditable": is_editable},
        )
