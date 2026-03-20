"""
roboat.badges
~~~~~~~~~~~~~~~~
Badges API — badges.roblox.com
"""

from typing import List, Optional
from .models import Badge, Page


class BadgesAPI:
    BASE = "https://badges.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def get_badge(self, badge_id: int) -> Badge:
        """Get badge info by ID."""
        data = self._c._get(f"{self.BASE}/badges/{badge_id}")
        return Badge.from_dict(data)

    def get_universe_badges(self, universe_id: int, limit: int = 10,
                            cursor: Optional[str] = None) -> Page:
        """Get all badges for a universe/game."""
        params = {"limit": limit, "sortOrder": "Asc"}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/universes/{universe_id}/badges", params=params)
        return Page.from_dict(data, Badge)

    def get_user_badges(self, user_id: int, limit: int = 10,
                        cursor: Optional[str] = None) -> Page:
        """Get badges awarded to a user."""
        params = {"limit": limit, "sortOrder": "Asc"}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/users/{user_id}/badges", params=params)
        return Page.from_dict(data, Badge)

    def get_awarded_dates(self, user_id: int, badge_ids: List[int]) -> dict:
        """
        Check which badges a user has and when they were awarded.
        Returns {badge_id: awarded_date_str}.
        """
        data = self._c._get(
            f"{self.BASE}/users/{user_id}/badges/awarded-dates",
            params={"badgeIds": ",".join(str(i) for i in badge_ids)},
        )
        return {
            item["badgeId"]: item.get("awardedDate")
            for item in data.get("data", [])
        }
