"""
examples/marketplace_tools.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Marketplace and economy tools — RAP tracking, profit estimation,
underpriced limited detection.
"""

from roboat import RoboatClient
from roboat.marketplace import MarketplaceAPI

client = RoboatClient()
market = MarketplaceAPI(client)

# ── Get full limited data ───────────────────────────────────────────

print("=== Valkyrie Helm ===")
data = market.get_limited_data(1365767)
print(data)
print(f"Price trend: {data.price_trend}")
print()

# ── Estimate resale profit ──────────────────────────────────────────

print("=== Resale Profit Estimate ===")
profit = market.estimate_resale_profit(1365767, purchase_price=12000)
print(profit)
print()

# ── RAP Tracker — snapshot and diff ────────────────────────────────

print("=== RAP Tracker ===")
tracker = market.create_rap_tracker([1365767, 1028606, 19027209])

print("Taking snapshot 1...")
snap1 = tracker.snapshot()
for aid, rap in snap1.items():
    print(f"  Asset #{aid}: {rap:,}R$")

import time
print("Waiting 5 seconds...")
time.sleep(5)

print("Taking snapshot 2...")
tracker.snapshot()
print(tracker.summary())
print()

# ── Find underpriced limiteds ───────────────────────────────────────

print("=== Underpriced Limiteds (below 90% RAP) ===")
asset_ids = [1365767, 1028606, 19027209, 11884330, 1029025]
deals = market.find_underpriced_limiteds(asset_ids, threshold_pct=0.90)

if deals:
    for d in deals:
        ratio = (d.lowest_resale_price / d.recent_average_price * 100) if d.recent_average_price else 0
        print(f"  {d.name}: {d.lowest_resale_price:,}R$ ({ratio:.1f}% of RAP)")
else:
    print("  No underpriced limiteds found in this list.")
