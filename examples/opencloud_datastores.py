"""
examples/opencloud_datastores.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Open Cloud DataStore operations — read, write, increment, delete,
ordered DataStores, and MessagingService.

Get your API key at: https://create.roblox.com/dashboard/credentials
"""

from roboat import RoboatClient

client    = RoboatClient()
API_KEY   = "roblox-KEY-xxxxxx"   # replace with your key
UNIVERSE  = 123456789              # replace with your universe ID

# ── Standard DataStores ────────────────────────────────────────────

print("=== Standard DataStores ===")

# List all stores in universe
stores = client.develop.list_datastores(UNIVERSE, API_KEY)
print(f"Found {len(stores)} datastores:")
for s in stores:
    print(f"  {s.name}")

# Write player data
client.develop.set_datastore_entry(
    UNIVERSE, "PlayerData", "player_156",
    value={"coins": 1000, "level": 25, "wins": 42},
    api_key=API_KEY,
    user_ids=[156],   # associate with Roblox user for GDPR
)
print("Wrote player_156 data")

# Read it back
data = client.develop.get_datastore_entry(
    UNIVERSE, "PlayerData", "player_156", API_KEY
)
print(f"Read back: {data}")

# Increment a counter
client.develop.increment_datastore_entry(
    UNIVERSE, "ServerStats", "total_deaths", delta=1, api_key=API_KEY
)

# List all keys in PlayerData
keys = client.develop.list_datastore_keys(
    UNIVERSE, "PlayerData", API_KEY, prefix="player_"
)
print(f"Keys: {[k['key'] for k in keys.get('keys', [])]}")

# Version history for a key
versions = client.develop.list_datastore_versions(
    UNIVERSE, "PlayerData", "player_156", API_KEY
)
print(f"Versions: {len(versions.get('versions', []))}")

# Delete a key
client.develop.delete_datastore_entry(
    UNIVERSE, "Sessions", "expired_session", API_KEY
)

# ── Ordered DataStores (leaderboards) ─────────────────────────────

print("\n=== Ordered DataStore (Leaderboard) ===")

# Update player score (upsert)
client.develop.set_ordered_datastore_entry(
    UNIVERSE, "GlobalLeaderboard", "player_156",
    value=9500, api_key=API_KEY, allow_missing=True,
)

# Increment score
client.develop.increment_ordered_datastore(
    UNIVERSE, "GlobalLeaderboard", "player_156",
    amount=100, api_key=API_KEY,
)

# Get top 10
top = client.develop.list_ordered_datastore(
    UNIVERSE, "GlobalLeaderboard", API_KEY,
    max_page_size=10, order_by="desc",
)
print("Top players:")
for i, entry in enumerate(top.get("entries", []), 1):
    print(f"  #{i} {entry['id']}: {entry['value']:,}")

# ── MessagingService ───────────────────────────────────────────────

print("\n=== MessagingService ===")

# Custom topic
client.develop.publish_message(
    UNIVERSE, "PlayerAnnouncements",
    "Double XP event starts now!", API_KEY
)
print("Published announcement")

# Shutdown warning
client.develop.announce(UNIVERSE, API_KEY, "Server restart in 2 minutes!")
print("Sent shutdown warning")
