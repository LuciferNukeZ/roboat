"""
examples/database_tracking.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Database layer — persist users, games, and inventory snapshots.
Detect changes between runs.
"""

from roboat import RoboatClient, SessionDatabase

client = RoboatClient()
db     = SessionDatabase.load_or_create("tracking")

# ── Save users and games ───────────────────────────────────────────

print("=== Saving Users & Games ===")

user = client.users.get_user(156)
db.save_user(user)
print(f"Saved: {user}")

game = client.games.get_game(2753915549)
db.save_game(game)
print(f"Saved: {game.name}")

# ── Retrieve cached data ───────────────────────────────────────────

print("\n=== Reading from DB ===")
cached_user = db.get_user(156)
print(f"Cached user: {cached_user['username']}")

all_users = db.get_all_users()
print(f"Total cached users: {len(all_users)}")

all_games = db.get_all_games()
print(f"Total cached games: {len(all_games)}")

# ── Key-value store ────────────────────────────────────────────────

print("\n=== Key-Value Store ===")

db.set("last_run", "2024-06-01T12:00:00")
db.set("tracked_users", [156, 261, 1234])
db.set("config", {"interval_seconds": 30, "alert_rap_threshold": 1000})

print(f"last_run: {db.get('last_run')}")
print(f"tracked_users: {db.get('tracked_users')}")
print(f"config: {db.get('config')}")
print(f"all keys: {db.keys()}")

# ── Inventory snapshot & diff ──────────────────────────────────────

print("\n=== Inventory Snapshot (User 156) ===")

USER_ID = 156
page = client.inventory.get_collectibles(USER_ID, limit=100)
current_ids = {a.asset_id for a in page.data}
current_rap  = sum(a.recent_average_price for a in page.data)

saved_ids = set(db.get(f"inventory:{USER_ID}") or [])
gained    = current_ids - saved_ids
lost      = saved_ids - current_ids

if not saved_ids:
    print("First run — no previous snapshot. Saving current state.")
else:
    if gained:
        print(f"Gained assets: {gained}")
    if lost:
        print(f"Lost assets: {lost}")
    if not gained and not lost:
        print("No inventory changes detected.")

print(f"Current collectibles: {len(current_ids)}")
print(f"Current RAP (shown): {current_rap:,}R$")

db.set(f"inventory:{USER_ID}", list(current_ids))
db.set(f"rap:{USER_ID}", current_rap)

# ── DB stats ───────────────────────────────────────────────────────

print("\n=== Database Stats ===")
stats = db.stats()
for k, v in stats.items():
    print(f"  {k}: {v}")

# ── List all DBs ───────────────────────────────────────────────────

print("\n=== All Local Databases ===")
dbs = SessionDatabase.list_databases()
for name in dbs:
    print(f"  {name}.robloxdb")

db.close()
print("\nDone.")
