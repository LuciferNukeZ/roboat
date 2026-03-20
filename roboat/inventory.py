"""
roboat.inventory
~~~~~~~~~~~~~~~~~~~
Inventory API — inventory.roblox.com + economy.roblox.com
Check asset ownership, list user inventory, asset details.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from .models import Page


@dataclass
class InventoryAsset:
    user_asset_id: int
    asset_id: int
    name: str
    asset_type_id: int
    created: str
    updated: str
    serial_number: Optional[int] = None
    is_tradable: bool = False
    is_recent_average_price_valid: bool = False
    recent_average_price: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "InventoryAsset":
        return cls(
            user_asset_id=d.get("userAssetId", 0),
            asset_id=d.get("assetId", 0),
            name=d.get("name", ""),
            asset_type_id=d.get("assetTypeId", 0),
            created=d.get("created", ""),
            updated=d.get("updated", ""),
            serial_number=d.get("serialNumber"),
            is_tradable=d.get("isTradable", False),
            is_recent_average_price_valid=d.get("isRecentAveragePriceValid", False),
            recent_average_price=d.get("recentAveragePrice", 0),
        )

    def __str__(self) -> str:
        serial = f" #{self.serial_number}" if self.serial_number else ""
        tradable = " [Tradable]" if self.is_tradable else ""
        rap = f" RAP: {self.recent_average_price:,}R$" if self.recent_average_price else ""
        return f"{self.name}{serial}{tradable}{rap}"


class InventoryAPI:
    BASE  = "https://inventory.roblox.com/v1"
    BASE2 = "https://inventory.roblox.com/v2"
    ECON  = "https://economy.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def get_user_inventory(self, user_id: int, asset_type_ids: List[int],
                           limit: int = 100,
                           cursor: Optional[str] = None) -> Page:
        """
        Get a user's inventory filtered by asset type.

        Common asset_type_ids:
            2  = T-Shirt       11 = Shirt       12 = Pants
            8  = Hat           17 = Head        18 = Face
            19 = Gear          25 = Body Parts   27 = Torso
            28 = Right Arm     29 = Left Arm    30 = Right Leg
            31 = Left Leg      41 = Hair        42 = Emote
            43 = Shoulder      44 = Front       45 = Back
            46 = Waist         47 = Climb       48 = Fall
            49 = Jump          50 = Run         51 = Swim
            52 = Walk          53 = Idle        54 = Animation
            61 = Bundle        62 = AnimationBundle

        Returns:
            Page of InventoryAsset objects.
        """
        params = {
            "assetTypeIds": ",".join(str(i) for i in asset_type_ids),
            "limit": limit,
            "sortOrder": "Asc",
        }
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE}/users/{user_id}/assets/collectibles",
            params=params,
        )
        assets = [InventoryAsset.from_dict(a) for a in data.get("data", [])]
        return Page(
            data=assets,
            next_cursor=data.get("nextPageCursor"),
            previous_cursor=data.get("previousPageCursor"),
        )

    def get_collectibles(self, user_id: int, limit: int = 100,
                         cursor: Optional[str] = None) -> Page:
        """
        Get all tradable/collectible (limited) items owned by a user.

        Returns:
            Page of InventoryAsset objects with RAP data.
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE}/users/{user_id}/assets/collectibles",
            params=params,
        )
        assets = [InventoryAsset.from_dict(a) for a in data.get("data", [])]
        return Page(
            data=assets,
            next_cursor=data.get("nextPageCursor"),
        )

    def owns_asset(self, user_id: int, asset_id: int) -> bool:
        """Check if a user owns a specific asset. Returns True/False."""
        try:
            data = self._c._get(
                f"{self.BASE}/users/{user_id}/items/1/{asset_id}/is-owned"
            )
            return bool(data)
        except Exception:
            return False

    def owns_badge(self, user_id: int, badge_id: int) -> bool:
        """Check if a user has earned a specific badge."""
        try:
            data = self._c._get(
                f"https://badges.roblox.com/v1/users/{user_id}/badges/awarded-dates",
                params={"badgeIds": badge_id},
            )
            return len(data.get("data", [])) > 0
        except Exception:
            return False

    def owns_game_pass(self, user_id: int, game_pass_id: int) -> bool:
        """Check if a user owns a game pass."""
        try:
            data = self._c._get(
                f"https://inventory.roblox.com/v1/users/{user_id}/items/GamePass/{game_pass_id}/is-owned"
            )
            return bool(data)
        except Exception:
            return False

    def get_user_item_types(self, user_id: int) -> List[dict]:
        """Get all item type categories available in a user's inventory."""
        data = self._c._get(
            f"{self.BASE2}/users/{user_id}/inventory",
            params={"limit": 100},
        )
        return data.get("data", [])

    def get_user_hats(self, user_id: int, limit: int = 100) -> Page:
        """Shortcut: Get all hats owned by a user."""
        return self.get_user_inventory(user_id, [8], limit=limit)

    def get_user_faces(self, user_id: int, limit: int = 100) -> Page:
        """Shortcut: Get all faces owned by a user."""
        return self.get_user_inventory(user_id, [18], limit=limit)

    def get_user_gear(self, user_id: int, limit: int = 100) -> Page:
        """Shortcut: Get all gear owned by a user."""
        return self.get_user_inventory(user_id, [19], limit=limit)

    def get_user_clothes(self, user_id: int, limit: int = 100) -> Page:
        """Shortcut: Get all clothing (shirt, pants, t-shirt) owned by a user."""
        return self.get_user_inventory(user_id, [2, 11, 12], limit=limit)

    def get_total_rap(self, user_id: int) -> int:
        """
        Calculate the total Recent Average Price (RAP) of a user's limiteds.
        Iterates through all pages of collectibles.

        Returns:
            int: Total RAP in Robux.
        """
        total = 0
        cursor = None
        while True:
            page = self.get_collectibles(user_id, limit=100, cursor=cursor)
            for asset in page.data:
                total += asset.recent_average_price
            cursor = page.next_cursor
            if not cursor:
                break
        return total
