"""
tools/rap_snapshot.py
~~~~~~~~~~~~~~~~~~~~~
CLI tool: snapshot a user's limited item RAP and save to JSON.
Re-run to see what changed.

Usage:
  python tools/rap_snapshot.py --user 156
  python tools/rap_snapshot.py --user 156 --diff
  python tools/rap_snapshot.py --user 156 --output snap.json
"""

import argparse
import json
import os
import time
from roboat import RoboatClient
from roboat.utils import Paginator


def take_snapshot(client: RoboatClient, user_id: int) -> dict:
    print(f"Fetching collectibles for user {user_id}...")
    page_fn = lambda c: client.inventory.get_collectibles(user_id, limit=100, cursor=c)
    assets = Paginator(page_fn).collect()

    items = []
    total_rap = 0
    for a in assets:
        items.append({
            "asset_id":   a.asset_id,
            "name":       a.name,
            "serial":     a.serial_number,
            "rap":        a.recent_average_price,
            "tradable":   a.is_tradable,
        })
        total_rap += a.recent_average_price

    return {
        "user_id":    user_id,
        "timestamp":  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_rap":  total_rap,
        "item_count": len(items),
        "items":      items,
    }


def diff_snapshots(old: dict, new: dict):
    old_map = {i["asset_id"]: i for i in old.get("items", [])}
    new_map = {i["asset_id"]: i for i in new.get("items", [])}

    gained = [new_map[k] for k in new_map if k not in old_map]
    lost   = [old_map[k] for k in old_map if k not in new_map]
    rap_change = new["total_rap"] - old["total_rap"]

    print(f"\n── Snapshot Diff ──────────────────────────────")
    print(f"  Old: {old['timestamp']}  RAP: {old['total_rap']:,}R$  Items: {old['item_count']}")
    print(f"  New: {new['timestamp']}  RAP: {new['total_rap']:,}R$  Items: {new['item_count']}")
    print(f"  RAP change: {'+' if rap_change >= 0 else ''}{rap_change:,}R$")

    if gained:
        print(f"\n  ✅ Gained ({len(gained)}):")
        for item in gained:
            print(f"     • {item['name']} — {item['rap']:,}R$")
    if lost:
        print(f"\n  ❌ Lost ({len(lost)}):")
        for item in lost:
            print(f"     • {item['name']} — {item['rap']:,}R$")
    if not gained and not lost:
        print("\n  No changes detected.")


def main():
    parser = argparse.ArgumentParser(description="roboat RAP snapshot tool")
    parser.add_argument("--user",   type=int, required=True, help="Roblox user ID")
    parser.add_argument("--diff",   action="store_true",      help="Diff against saved snapshot")
    parser.add_argument("--output", type=str,                 help="Output file (default: snap_<userid>.json)")
    args = parser.parse_args()

    client   = RoboatClient()
    out_file = args.output or f"snap_{args.user}.json"

    old_snap = None
    if args.diff and os.path.exists(out_file):
        with open(out_file) as f:
            old_snap = json.load(f)

    new_snap = take_snapshot(client, args.user)

    with open(out_file, "w") as f:
        json.dump(new_snap, f, indent=2)

    print(f"\nTotal RAP : {new_snap['total_rap']:,}R$")
    print(f"Items     : {new_snap['item_count']}")
    print(f"Saved     : {out_file}")

    if old_snap:
        diff_snapshots(old_snap, new_snap)


if __name__ == "__main__":
    main()
