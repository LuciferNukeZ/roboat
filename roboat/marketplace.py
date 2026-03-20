"""
roboat.marketplace
~~~~~~~~~~~~~~~~~~
Marketplace tools — limited items, collectibles, UGC,
purchase history, and economy monitoring.

Example::

    from roboat.marketplace import MarketplaceAPI

    market = MarketplaceAPI(client)

    # Get resale data for a limited
    data = market.get_limited_data(1365767)
    print(data)

    # Check if a limited is profitable to resell
    profit = market.estimate_resale_profit(1365767, purchase_price=5000)
    print(profit)

    # Monitor RAP changes for a list of assets
    tracker = market.create_rap_tracker([1365767, 1028606])
    tracker.snapshot()
    # ... time passes ...
    changes = tracker.diff()
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import time


@dataclass
class LimitedData:
    asset_id: int
    name: str
    asset_stock: Optional[int]
    sales: int
    number_remaining: Optional[int]
    recent_average_price: int
    original_price: Optional[int]
    lowest_resale_price: Optional[int]
    price_data_points: List[dict] = field(default_factory=list)
    volume_data_points: List[dict] = field(default_factory=list)

    @classmethod
    def from_resale_dict(cls, asset_id: int, resale: dict,
                          details: Optional[dict] = None) -> "LimitedData":
        return cls(
            asset_id=asset_id,
            name=details.get("name", "") if details else "",
            asset_stock=resale.get("assetStock"),
            sales=resale.get("sales", 0),
            number_remaining=resale.get("numberRemaining"),
            recent_average_price=resale.get("recentAveragePrice", 0),
            original_price=resale.get("originalPrice"),
            lowest_resale_price=None,
            price_data_points=resale.get("priceDataPoints", []),
            volume_data_points=resale.get("volumeDataPoints", []),
        )

    @property
    def price_trend(self) -> str:
        """Returns 'rising', 'falling', or 'stable' based on price history."""
        points = [p["value"] for p in self.price_data_points[-5:] if "value" in p]
        if len(points) < 2:
            return "unknown"
        delta = points[-1] - points[0]
        if delta > points[0] * 0.05:
            return "rising"
        elif delta < -(points[0] * 0.05):
            return "falling"
        return "stable"

    def __str__(self) -> str:
        remaining = f"{self.number_remaining:,}" if self.number_remaining is not None else "N/A"
        low = f"{self.lowest_resale_price:,}R$" if self.lowest_resale_price else "N/A"
        trend_emoji = {"rising": "📈", "falling": "📉", "stable": "➡️", "unknown": "❓"}
        return (
            f"💎 {self.name} [#{self.asset_id}]\n"
            f"   RAP       : {self.recent_average_price:,}R$\n"
            f"   Lowest    : {low}\n"
            f"   Sales     : {self.sales:,}\n"
            f"   Remaining : {remaining}\n"
            f"   Trend     : {trend_emoji.get(self.price_trend, '❓')} {self.price_trend}"
        )


@dataclass
class ResaleProfit:
    asset_id: int
    purchase_price: int
    rap: int
    lowest_resale: Optional[int]
    roblox_fee: int
    estimated_profit: int
    roi_percent: float

    def __str__(self) -> str:
        sign = "+" if self.estimated_profit >= 0 else ""
        return (
            f"💰 Asset #{self.asset_id} Profit Estimate\n"
            f"   Bought at  : {self.purchase_price:,}R$\n"
            f"   RAP        : {self.rap:,}R$\n"
            f"   Roblox fee : -{self.roblox_fee:,}R$ (30%)\n"
            f"   Net profit : {sign}{self.estimated_profit:,}R$\n"
            f"   ROI        : {self.roi_percent:+.1f}%"
        )


class RAPTracker:
    """
    Tracks RAP changes for a set of limited assets over time.

    Usage::

        tracker = RAPTracker(client, asset_ids=[1365767, 1028606])
        tracker.snapshot()      # save current RAP
        # ... wait some time ...
        changes = tracker.diff() # get what changed
    """

    def __init__(self, client, asset_ids: List[int]):
        self._c = client
        self.asset_ids = asset_ids
        self._snapshots: List[Dict[int, int]] = []
        self._timestamps: List[float] = []

    def snapshot(self) -> Dict[int, int]:
        """Take a RAP snapshot. Returns {asset_id: rap}."""
        from .economy import EconomyAPI
        snap: Dict[int, int] = {}
        for aid in self.asset_ids:
            try:
                data = self._c._get(
                    f"https://economy.roblox.com/v1/assets/{aid}/resale-data"
                )
                snap[aid] = data.get("recentAveragePrice", 0)
            except Exception:
                snap[aid] = 0
        self._snapshots.append(snap)
        self._timestamps.append(time.time())
        return snap

    def diff(self) -> List[dict]:
        """
        Compare the last two snapshots.

        Returns:
            List of dicts: [{asset_id, old_rap, new_rap, change, change_pct}]
        """
        if len(self._snapshots) < 2:
            return []
        old = self._snapshots[-2]
        new = self._snapshots[-1]
        results = []
        for aid in self.asset_ids:
            o = old.get(aid, 0)
            n = new.get(aid, 0)
            delta = n - o
            pct = ((delta / o) * 100) if o > 0 else 0.0
            results.append({
                "asset_id": aid,
                "old_rap": o,
                "new_rap": n,
                "change": delta,
                "change_pct": round(pct, 2),
            })
        return sorted(results, key=lambda x: abs(x["change"]), reverse=True)

    def summary(self) -> str:
        """Return a formatted summary of the latest diff."""
        changes = self.diff()
        if not changes:
            return "No comparison data yet. Call snapshot() at least twice."
        lines = ["📊 RAP Tracker Summary", "─" * 50]
        for c in changes:
            sign  = "+" if c["change"] >= 0 else ""
            arrow = "↑" if c["change"] > 0 else ("↓" if c["change"] < 0 else "→")
            lines.append(
                f"  {arrow} Asset #{c['asset_id']:>12} "
                f"| {c['old_rap']:>8,} → {c['new_rap']:>8,}R$ "
                f"| {sign}{c['change']:,}R$ ({sign}{c['change_pct']}%)"
            )
        return "\n".join(lines)


class MarketplaceAPI:
    """
    Marketplace tools for limited items, economy, and UGC.

    Args:
        client: A RoboatClient instance.
    """

    ECON = "https://economy.roblox.com/v1"
    CAT  = "https://catalog.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def get_limited_data(self, asset_id: int) -> LimitedData:
        """
        Get full resale data for a limited item including price history.

        Args:
            asset_id: The asset ID of the limited.

        Returns:
            LimitedData with RAP, sales, remaining, price trend.
        """
        resale = self._c._get(f"{self.ECON}/assets/{asset_id}/resale-data")
        try:
            details_resp = self._c._post(
                f"{self.CAT}/catalog/items/details",
                json={"items": [{"itemType": "Asset", "id": asset_id}]},
            )
            details = details_resp.get("data", [{}])[0]
        except Exception:
            details = {}

        data = LimitedData.from_resale_dict(asset_id, resale, details)

        # Get lowest resale price from first reseller
        try:
            sellers = self._c._get(
                f"{self.ECON}/assets/{asset_id}/resellers",
                params={"limit": 1},
            )
            first = sellers.get("data", [{}])[0]
            data.lowest_resale_price = first.get("price")
        except Exception:
            pass

        return data

    def get_limited_data_bulk(self, asset_ids: List[int]) -> List[LimitedData]:
        """
        Get limited data for multiple assets.

        Returns:
            List of LimitedData objects.
        """
        return [self.get_limited_data(aid) for aid in asset_ids]

    def estimate_resale_profit(self, asset_id: int,
                                purchase_price: int) -> ResaleProfit:
        """
        Estimate profit from reselling a limited item.
        Roblox takes a 30% fee on all sales.

        Args:
            asset_id: The limited asset ID.
            purchase_price: What you paid for it.

        Returns:
            ResaleProfit with fee breakdown and ROI.
        """
        data = self.get_limited_data(asset_id)
        sell_at   = data.lowest_resale_price or data.recent_average_price
        fee       = int(sell_at * 0.30)
        net       = sell_at - fee
        profit    = net - purchase_price
        roi       = ((profit / purchase_price) * 100) if purchase_price > 0 else 0.0
        return ResaleProfit(
            asset_id=asset_id,
            purchase_price=purchase_price,
            rap=data.recent_average_price,
            lowest_resale=data.lowest_resale_price,
            roblox_fee=fee,
            estimated_profit=profit,
            roi_percent=round(roi, 2),
        )

    def get_economy_metrics(self, universe_id: int) -> dict:
        """
        Get transaction volume and economy metrics for a game.

        Returns:
            dict with aggregate economy data.
        """
        return self._c._get(
            f"https://economy.roblox.com/v1/universes/{universe_id}/economy-analytics"
        )

    def get_user_purchase_history(self, user_id: int,
                                   transaction_type: str = "Purchase",
                                   limit: int = 25,
                                   cursor: Optional[str] = None) -> dict:
        """
        Get purchase history for a user. Requires auth.

        transaction_type: "Purchase", "Sale", "AffiliateSale",
                          "GroupPayout", "DevEx"

        Returns:
            dict with transaction list.
        """
        self._c.require_auth("get_user_purchase_history")
        params = {"transactionType": transaction_type, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._c._get(
            f"https://economy.roblox.com/v2/users/{user_id}/transactions",
            params=params,
        )

    def create_rap_tracker(self, asset_ids: List[int]) -> RAPTracker:
        """
        Create a RAP tracker for a list of limited asset IDs.

        Returns:
            RAPTracker instance ready for snapshotting.
        """
        return RAPTracker(self._c, asset_ids)

    def find_underpriced_limiteds(self, asset_ids: List[int],
                                   threshold_pct: float = 0.85) -> List[LimitedData]:
        """
        Find limited items currently selling below their RAP.

        Args:
            asset_ids: List of limited asset IDs to check.
            threshold_pct: Items priced below this fraction of RAP are returned.
                           Default 0.85 means "selling for less than 85% of RAP".

        Returns:
            List of LimitedData for underpriced items, sorted by discount depth.
        """
        underpriced = []
        for aid in asset_ids:
            try:
                data = self.get_limited_data(aid)
                if data.lowest_resale_price and data.recent_average_price:
                    ratio = data.lowest_resale_price / data.recent_average_price
                    if ratio < threshold_pct:
                        underpriced.append(data)
            except Exception:
                continue
        return sorted(
            underpriced,
            key=lambda d: (d.lowest_resale_price or 0) / max(d.recent_average_price, 1),
        )
