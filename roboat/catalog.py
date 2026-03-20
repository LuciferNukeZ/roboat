"""
roboat.catalog
~~~~~~~~~~~~~~~~~
Catalog API — catalog.roblox.com
"""

from typing import List, Optional
from .models import CatalogItem, Page


class CatalogAPI:
    BASE  = "https://catalog.roblox.com/v1"
    BASE2 = "https://catalog.roblox.com/v2"

    def __init__(self, client):
        self._c = client

    def search(self, keyword: str = "", category: str = "All",
               subcategory: str = "All", sort_type: str = "Relevance",
               price_min: Optional[int] = None, price_max: Optional[int] = None,
               limit: int = 30, cursor: Optional[str] = None) -> Page:
        """Search the avatar catalog."""
        params = {
            "category": category, "subcategory": subcategory,
            "sortType": sort_type, "limit": limit,
        }
        if keyword:    params["keyword"] = keyword
        if price_min:  params["minPrice"] = price_min
        if price_max:  params["maxPrice"] = price_max
        if cursor:     params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/search/items", params=params)
        return Page.from_dict(data, CatalogItem)

    def get_item_details(self, items: List[dict]) -> List[CatalogItem]:
        """
        Get details for catalog items.
        items: list of {"itemType": "Asset"|"Bundle", "id": int}
        """
        data = self._c._post(
            f"{self.BASE}/catalog/items/details",
            json={"items": items},
        )
        return [CatalogItem.from_dict(i) for i in data.get("data", [])]

    def get_asset(self, asset_id: int) -> CatalogItem:
        """Get details for a single asset."""
        results = self.get_item_details([{"itemType": "Asset", "id": asset_id}])
        if not results:
            from .exceptions import ItemNotFoundError
            raise ItemNotFoundError(f"Asset {asset_id} not found")
        return results[0]

    def get_bundle(self, bundle_id: int) -> CatalogItem:
        """Get details for a single bundle."""
        results = self.get_item_details([{"itemType": "Bundle", "id": bundle_id}])
        if not results:
            from .exceptions import ItemNotFoundError
            raise ItemNotFoundError(f"Bundle {bundle_id} not found")
        return results[0]

    def get_resale_data(self, asset_id: int):
        """Get resale history for a limited item. Delegates to economy API."""
        return self._c.economy.get_asset_resale_data(asset_id)

    def get_resellers(self, asset_id: int, limit: int = 10,
                      cursor: Optional[str] = None) -> Page:
        """Get resellers for a limited item."""
        return self._c.economy.get_asset_resellers(asset_id, limit, cursor)

    def get_user_bundles(self, user_id: int, limit: int = 10,
                         cursor: Optional[str] = None) -> Page:
        """Get bundles owned by a user."""
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/users/{user_id}/bundles", params=params)
        return Page.from_dict(data)

    def get_asset_favorite_count(self, asset_id: int) -> int:
        """Get favorite count for an asset."""
        data = self._c._get(f"{self.BASE}/favorites/assets/{asset_id}/count")
        return data if isinstance(data, int) else 0
