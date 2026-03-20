"""
roboat.economy
~~~~~~~~~~~~~~~~~
Economy API — economy.roblox.com
"""

from typing import Optional, List
from .models import RobuxBalance, Transaction, ResaleData, Page


class EconomyAPI:
    BASE = "https://economy.roblox.com/v1"
    BASE2 = "https://economy.roblox.com/v2"

    def __init__(self, client):
        self._c = client

    def get_robux_balance(self, user_id: int) -> RobuxBalance:
        """Get Robux balance for a user (requires auth for own balance)."""
        self._c.require_auth("get_robux_balance")
        data = self._c._get(f"{self.BASE}/users/{user_id}/currency")
        return RobuxBalance(robux=data.get("robux", 0))

    def get_transactions(self, user_id: int,
                         transaction_type: str = "Sale",
                         limit: int = 25,
                         cursor: Optional[str] = None) -> Page:
        """
        Get transaction history. Requires auth.
        transaction_type: "Sale", "Purchase", "AffiliateSale", "DevEx",
                          "GroupPayout", "AdImpressionPayout"
        """
        self._c.require_auth("get_transactions")
        params = {"transactionType": transaction_type, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE2}/users/{user_id}/transaction-totals",
            params=params,
        )
        return Page.from_dict(data)

    def get_asset_resale_data(self, asset_id: int) -> ResaleData:
        """Get resale price history for a limited item."""
        data = self._c._get(f"{self.BASE}/assets/{asset_id}/resale-data")
        return ResaleData.from_dict(asset_id, data)

    def get_asset_resellers(self, asset_id: int, limit: int = 10,
                            cursor: Optional[str] = None) -> Page:
        """Get users currently reselling a limited item."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE}/assets/{asset_id}/resellers",
            params=params,
        )
        return Page.from_dict(data)

    def get_group_funds(self, group_id: int) -> RobuxBalance:
        """Get a group's Robux balance. Requires auth + group permission."""
        self._c.require_auth("get_group_funds")
        data = self._c._get(f"{self.BASE}/groups/{group_id}/currency")
        return RobuxBalance(robux=data.get("robux", 0))
