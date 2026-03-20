"""
examples/group_manager.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Group management — roles, members, payouts, join requests, shouts.
Requires authentication.
"""

from roboat import RoboatClient, OAuthManager

# Auth
manager = OAuthManager(timeout=120)
token   = manager.authenticate()
client  = RoboatClient(oauth_token=token)

GROUP_ID = 7  # Replace with your group ID

# ── Group info ─────────────────────────────────────────────────────

group = client.groups.get_group(GROUP_ID)
print(group)

shout = client.groups.get_group_shout(GROUP_ID)
if shout:
    print(f"Current shout: {shout}")

# ── Roles ──────────────────────────────────────────────────────────

roles = client.groups.get_roles(GROUP_ID)
print(f"\nRoles ({len(roles)}):")
for role in roles:
    print(f"  {role}")

# Get a specific role by name
member_role = client.groups.get_role_by_name(GROUP_ID, "Member")
if member_role:
    print(f"\nMember role: {member_role}")

# ── Members ────────────────────────────────────────────────────────

members = client.groups.get_members(GROUP_ID, limit=10)
print(f"\nFirst 10 members:")
for m in members.data:
    print(f"  {m}")

# Check if a user is a member
is_in = client.groups.is_member(GROUP_ID, user_id=156)
print(f"\nUser 156 is member: {is_in}")

# ── Join requests ──────────────────────────────────────────────────

requests = client.groups.get_join_requests(GROUP_ID, limit=5)
print(f"\nPending join requests: {len(requests.data)}")
for req in requests.data:
    print(f"  {req}")

# Accept all pending requests
accepted = client.groups.accept_all_join_requests(GROUP_ID)
print(f"Accepted {accepted} join requests")

# ── Wall ───────────────────────────────────────────────────────────

wall = client.groups.get_wall(GROUP_ID, limit=5)
print(f"\nLast 5 wall posts:")
for post in wall.data:
    print(f"  {post}")

# Post to wall
# client.groups.post_to_wall(GROUP_ID, "New update deployed!")

# ── Shout ──────────────────────────────────────────────────────────

# client.groups.post_shout(GROUP_ID, "Welcome to the group!")

# ── Payouts ────────────────────────────────────────────────────────

payouts = client.groups.get_payouts(GROUP_ID)
print(f"\nCurrent payouts ({len(payouts)}):")
for p in payouts:
    print(f"  {p}")

# One-time payout
# client.groups.pay_out(GROUP_ID, user_id=1234, amount=100)

# ── Audit log ──────────────────────────────────────────────────────

log = client.groups.get_audit_log(GROUP_ID, limit=5)
print(f"\nAudit log entries: {len(log.data)}")

# ── Allies & enemies ───────────────────────────────────────────────

allies  = client.groups.get_allies(GROUP_ID)
enemies = client.groups.get_enemies(GROUP_ID)
print(f"\nAllies: {len(allies)}  Enemies: {len(enemies)}")
