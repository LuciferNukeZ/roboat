"""
roboat.thumbnails
~~~~~~~~~~~~~~~~~~~~
Thumbnails API — thumbnails.roblox.com
"""

from typing import List, Optional


class ThumbnailsAPI:
    BASE = "https://thumbnails.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def _thumb_urls(self, data: dict) -> dict:
        """Convert response data list to {target_id: url} mapping."""
        return {
            item["targetId"]: item.get("imageUrl", "")
            for item in data.get("data", [])
            if item.get("state") == "Completed"
        }

    def get_user_avatars(self, user_ids: List[int],
                         size: str = "420x420", format: str = "Png",
                         is_circular: bool = False) -> dict:
        """Get avatar thumbnail URLs. Returns {user_id: url} dict."""
        data = self._c._get(
            f"{self.BASE}/users/avatar",
            params={"userIds": ",".join(str(i) for i in user_ids),
                    "size": size, "format": format, "isCircular": is_circular},
        )
        return self._thumb_urls(data)

    def get_user_headshots(self, user_ids: List[int],
                           size: str = "420x420", format: str = "Png") -> dict:
        """Get headshot (head-only) thumbnail URLs. Returns {user_id: url}."""
        data = self._c._get(
            f"{self.BASE}/users/avatar-headshot",
            params={"userIds": ",".join(str(i) for i in user_ids),
                    "size": size, "format": format},
        )
        return self._thumb_urls(data)

    def get_game_icons(self, universe_ids: List[int],
                       size: str = "512x512", format: str = "Png") -> dict:
        """Get game icon URLs. Returns {universe_id: url}."""
        data = self._c._get(
            f"{self.BASE}/games/icons",
            params={"universeIds": ",".join(str(i) for i in universe_ids),
                    "size": size, "format": format},
        )
        return self._thumb_urls(data)

    def get_game_thumbnails(self, universe_ids: List[int],
                            size: str = "768x432", count: int = 5) -> dict:
        """Get game screenshots. Returns {universe_id: [url, ...]}."""
        data = self._c._get(
            f"{self.BASE}/games/multiget/thumbnails",
            params={"universeIds": ",".join(str(i) for i in universe_ids),
                    "size": size, "countPerUniverse": count},
        )
        result = {}
        for entry in data.get("data", []):
            uid = entry.get("universeId")
            urls = [t["imageUrl"] for t in entry.get("thumbnails", [])
                    if t.get("state") == "Completed"]
            result[uid] = urls
        return result

    def get_asset_thumbnails(self, asset_ids: List[int],
                             size: str = "420x420", format: str = "Png") -> dict:
        """Get asset thumbnail URLs. Returns {asset_id: url}."""
        data = self._c._get(
            f"{self.BASE}/assets",
            params={"assetIds": ",".join(str(i) for i in asset_ids),
                    "size": size, "format": format},
        )
        return self._thumb_urls(data)

    def get_group_icons(self, group_ids: List[int],
                        size: str = "420x420", format: str = "Png") -> dict:
        """Get group icon URLs. Returns {group_id: url}."""
        data = self._c._get(
            f"{self.BASE}/groups/icons",
            params={"groupIds": ",".join(str(i) for i in group_ids),
                    "size": size, "format": format},
        )
        return self._thumb_urls(data)

    def get_avatar_url(self, user_id: int, size: str = "420x420") -> Optional[str]:
        """Convenience — get a single user's avatar URL or None."""
        result = self.get_user_avatars([user_id], size=size)
        return result.get(user_id)
