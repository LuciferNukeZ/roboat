"""
examples/social_analysis.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Social graph analysis — mutual friends, follow checking,
presence snapshots, and friend suggestions.
"""

from roboat import RoboatClient
from roboat.social import SocialGraph

client = RoboatClient()
sg     = SocialGraph(client)

# ── Mutual friends ─────────────────────────────────────────────────

print("=== Mutual Friends ===")
mutuals = sg.mutual_friends(user_a=156, user_b=261)
print(f"Users 156 and 261 share {len(mutuals)} mutual friends")
for m in mutuals[:5]:
    print(f"  {m}")

count = sg.mutual_friends_count(156, 261)
print(f"Count only: {count}")

# ── Relationship checks ────────────────────────────────────────────

print("\n=== Relationship Checks ===")
friends = sg.are_friends(156, 261)
print(f"156 and 261 are friends: {friends}")

# Note: does_follow scans following list — may take a moment
# follows = sg.does_follow(follower_id=156, target_id=261)
# print(f"156 follows 261: {follows}")

# ── Presence snapshot ──────────────────────────────────────────────

print("\n=== Presence Snapshot ===")
user_ids = [156, 261, 1, 2, 3]
snap = sg.presence_snapshot(user_ids)
print(snap)
print(f"  Online IDs: {snap.online}")
print(f"  In Game IDs: {snap.in_game}")
print(f"  Offline IDs: {snap.offline}")

online_now = sg.who_is_online(user_ids)
print(f"  Currently active: {online_now}")

# ── Rank by followers ──────────────────────────────────────────────

print("\n=== Most Followed in Group ===")
nodes = sg.most_followed_in_group([156, 261, 1234])
for i, node in enumerate(nodes, 1):
    print(f"  #{i} {node}")

# ── Friend suggestions ─────────────────────────────────────────────

print("\n=== Friend Suggestions for User 156 ===")
suggestions = sg.follow_suggestions(user_id=156, limit=5)
for u in suggestions:
    print(f"  {u}")

# ── Friend overlap matrix ──────────────────────────────────────────

print("\n=== Friend Overlap Matrix ===")
ids = [156, 261, 1234]
matrix = sg.friend_overlap_matrix(ids)
for (a, b), count in matrix.items():
    if a < b:  # print each pair once
        print(f"  Users {a} & {b}: {count} mutual friends")
