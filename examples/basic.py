"""
examples/basic.py
~~~~~~~~~~~~~~~~~
Basic usage — no authentication required.
"""

from roboat import RoboatClient

client = RoboatClient()

# ── Users ──────────────────────────────────────────────────────────

user = client.users.get_user(156)
print(user)

users = client.users.get_users_by_ids([1, 156, 261])
for u in users:
    print(u.name, u.id)

page = client.users.search_users("builderman", limit=5)
for u in page:
    print(u)

# ── Games ──────────────────────────────────────────────────────────

game = client.games.get_game(2753915549)
print(game)
print(f"Visits: {game.visits:,}")

votes = client.games.get_votes([2753915549])
print(votes[0])

visits = client.games.get_visits([2753915549, 286090429])
print(visits)

# ── Friends ────────────────────────────────────────────────────────

friends = client.friends.get_friends(156)
print(f"{len(friends)} friends")
for f in friends[:5]:
    print(f)

count = client.friends.get_follower_count(156)
print(f"Followers: {count:,}")

# ── Thumbnails ─────────────────────────────────────────────────────

avatars = client.thumbnails.get_user_avatars([156], size="420x420")
print(avatars)

url = client.thumbnails.get_avatar_url(156)
print(f"Avatar URL: {url}")

# ── Catalog ────────────────────────────────────────────────────────

page = client.catalog.search(keyword="fedora", category="Accessories", limit=5)
for item in page:
    print(item)

# ── Presence ───────────────────────────────────────────────────────

presence = client.presence.get_presence(156)
print(f"Status: {presence.status}")
