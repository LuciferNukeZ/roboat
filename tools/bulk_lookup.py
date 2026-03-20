"""
tools/bulk_lookup.py
~~~~~~~~~~~~~~~~~~~~
CLI tool: bulk-fetch Roblox user data from a list of IDs or usernames.
Outputs to CSV or JSON.

Usage:
  python tools/bulk_lookup.py --ids 1 156 261 --format csv
  python tools/bulk_lookup.py --usernames Roblox builderman --format json
  python tools/bulk_lookup.py --ids 1 156 --output results.csv
"""

import argparse
import csv
import json
import sys
from roboat import RoboatClient
from roboat.exceptions import RoboatAPIError


def fetch_by_ids(client: RoboatClient, ids: list) -> list:
    users = client.users.get_users_by_ids(ids)
    return enrich(client, users)


def fetch_by_usernames(client: RoboatClient, usernames: list) -> list:
    users = client.users.get_users_by_usernames(usernames)
    return enrich(client, users)


def enrich(client: RoboatClient, users: list) -> list:
    rows = []
    for user in users:
        try:
            friends   = client.friends.get_friend_count(user.id)
            followers = client.friends.get_follower_count(user.id)
            presence  = client.presence.get_presence(user.id)
            rows.append({
                "id":           user.id,
                "username":     user.name,
                "display_name": user.display_name,
                "is_banned":    user.is_banned,
                "verified":     user.has_verified_badge,
                "friends":      friends,
                "followers":    followers,
                "status":       presence.status,
            })
        except RoboatAPIError as e:
            rows.append({"id": user.id, "username": user.name, "error": str(e)})
    return rows


def output_csv(rows: list, dest):
    if not rows:
        return
    writer = csv.DictWriter(dest, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)


def output_json(rows: list, dest):
    json.dump(rows, dest, indent=2)
    dest.write("\n")


def main():
    parser = argparse.ArgumentParser(description="roboat bulk user lookup")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ids",       type=int, nargs="+", help="User IDs")
    group.add_argument("--usernames", type=str, nargs="+", help="Usernames")
    parser.add_argument("--format",   choices=["csv", "json"], default="csv")
    parser.add_argument("--output",   type=str, help="Output file (default: stdout)")
    args = parser.parse_args()

    client = RoboatClient()

    print(f"Fetching data...", file=sys.stderr)
    if args.ids:
        rows = fetch_by_ids(client, args.ids)
    else:
        rows = fetch_by_usernames(client, args.usernames)

    print(f"Fetched {len(rows)} users.", file=sys.stderr)

    if args.output:
        with open(args.output, "w", newline="") as f:
            if args.format == "csv":
                output_csv(rows, f)
            else:
                output_json(rows, f)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        if args.format == "csv":
            output_csv(rows, sys.stdout)
        else:
            output_json(rows, sys.stdout)


if __name__ == "__main__":
    main()
