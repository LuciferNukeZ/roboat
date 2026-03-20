"""
roboat.trades
~~~~~~~~~~~~~~~~
Trades API — trades.roblox.com
Fetch, send, accept, decline trades. All require authentication.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .models import Page


@dataclass
class TradeAsset:
    user_asset_id: int
    serial_number: Optional[int]
    asset_id: int
    name: str
    recent_average_price: int
    original_price: Optional[int]
    asset_stock: Optional[int]
    member_count: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "TradeAsset":
        return cls(
            user_asset_id=d.get("userAssetId", 0),
            serial_number=d.get("serialNumber"),
            asset_id=d.get("assetId", 0),
            name=d.get("name", ""),
            recent_average_price=d.get("recentAveragePrice", 0),
            original_price=d.get("originalPrice"),
            asset_stock=d.get("assetStock"),
            member_count=d.get("memberCount", 0),
        )

    def __str__(self) -> str:
        return f"{self.name} [RAP: {self.recent_average_price:,}R$]"


@dataclass
class TradeOffer:
    user_id: int
    user_name: str
    robux: int
    assets: List[TradeAsset] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "TradeOffer":
        user = d.get("user", {})
        return cls(
            user_id=user.get("id", 0),
            user_name=user.get("name", ""),
            robux=d.get("robux", 0),
            assets=[TradeAsset.from_dict(a) for a in d.get("userAssets", [])],
        )

    @property
    def total_rap(self) -> int:
        return sum(a.recent_average_price for a in self.assets)

    def __str__(self) -> str:
        asset_str = ", ".join(str(a) for a in self.assets) or "(none)"
        robux_str = f" + {self.robux:,}R$" if self.robux else ""
        return f"{self.user_name}: {asset_str}{robux_str} [RAP: {self.total_rap:,}]"


@dataclass
class Trade:
    id: int
    user_id: int
    user_name: str
    status: str
    created: str
    expiration: Optional[str] = None
    offers: List[TradeOffer] = field(default_factory=list)

    STATUS_EMOJI = {
        "Open": "🟡",
        "Completed": "✅",
        "Declined": "❌",
        "Expired": "⏰",
        "Countered": "🔄",
    }

    @classmethod
    def from_dict(cls, d: dict) -> "Trade":
        user = d.get("user", {})
        return cls(
            id=d.get("id", 0),
            user_id=user.get("id", 0),
            user_name=user.get("name", ""),
            status=d.get("status", ""),
            created=d.get("created", ""),
            expiration=d.get("expiration"),
        )

    @classmethod
    def from_detail_dict(cls, d: dict) -> "Trade":
        t = cls(
            id=d.get("id", 0),
            user_id=0,
            user_name="",
            status=d.get("status", ""),
            created=d.get("created", ""),
            expiration=d.get("expiration"),
            offers=[TradeOffer.from_dict(o) for o in d.get("offers", [])],
        )
        return t

    def __str__(self) -> str:
        emoji = self.STATUS_EMOJI.get(self.status, "❓")
        return f"{emoji} Trade #{self.id} with {self.user_name} — {self.status}"


class TradesAPI:
    BASE = "https://trades.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def get_trades(self, trade_type: str = "Inbound",
                   limit: int = 25, cursor: Optional[str] = None) -> Page:
        """
        Fetch trade list. Requires auth.

        Args:
            trade_type: "Inbound", "Outbound", "Completed", "Inactive"
            limit: 10, 25, 50, 100

        Returns:
            Page of Trade objects.
        """
        self._c.require_auth("get_trades")
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/trades/{trade_type}", params=params)
        trades = [Trade.from_dict(t) for t in data.get("data", [])]
        return Page(
            data=trades,
            next_cursor=data.get("nextPageCursor"),
            previous_cursor=data.get("previousPageCursor"),
        )

    def get_trade_details(self, trade_id: int) -> Trade:
        """Get detailed info about a specific trade including offers. Requires auth."""
        self._c.require_auth("get_trade_details")
        data = self._c._get(f"{self.BASE}/trades/{trade_id}")
        return Trade.from_detail_dict(data)

    def get_trade_count(self, trade_type: str = "Inbound") -> int:
        """Get count of trades by type. Requires auth."""
        self._c.require_auth("get_trade_count")
        data = self._c._get(f"{self.BASE}/trades/{trade_type}/count")
        return data.get("count", 0)

    def accept_trade(self, trade_id: int) -> None:
        """Accept an inbound trade. Requires auth."""
        self._c.require_auth("accept_trade")
        self._c._post(f"{self.BASE}/trades/{trade_id}/accept")

    def decline_trade(self, trade_id: int) -> None:
        """Decline an inbound trade. Requires auth."""
        self._c.require_auth("decline_trade")
        self._c._post(f"{self.BASE}/trades/{trade_id}/decline")

    def send_trade(self,
                   target_user_id: int,
                   my_asset_ids: List[int],
                   their_asset_ids: List[int],
                   my_robux: int = 0,
                   their_robux: int = 0) -> dict:
        """
        Send a trade offer. Requires auth.

        Args:
            target_user_id: The user you are trading with.
            my_asset_ids: List of your userAssetIds to offer.
            their_asset_ids: List of their userAssetIds to request.
            my_robux: Robux you offer (0 if none).
            their_robux: Robux you request (0 if none).

        Returns:
            dict with trade ID on success.
        """
        self._c.require_auth("send_trade")
        payload = {
            "offers": [
                {
                    "userId": self._c.user_id(),
                    "userAssetIds": my_asset_ids,
                    "robux": my_robux,
                },
                {
                    "userId": target_user_id,
                    "userAssetIds": their_asset_ids,
                    "robux": their_robux,
                },
            ]
        }
        return self._c._post(f"{self.BASE}/trades/send", json=payload)

    def can_trade_with(self, user_id: int) -> dict:
        """
        Check if you can trade with a specific user. Requires auth.

        Returns:
            dict: {canTrade, status}
        """
        self._c.require_auth("can_trade_with")
        return self._c._get(f"{self.BASE}/users/{user_id}/can-trade-with")
