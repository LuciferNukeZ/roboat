"""
examples/event_monitor.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Real-time event monitoring — friends coming online, new friend requests,
message alerts, and game visit milestones.
"""

import time
from roboat import RoboatClient, EventPoller, OAuthManager


def main():
    # Authenticate
    manager = OAuthManager(timeout=120)
    print("Opening browser for authentication...")
    token = manager.authenticate()

    if not token:
        print("Authentication failed.")
        return

    client = RoboatClient(oauth_token=token)
    poller = EventPoller(client, interval=30)

    # ── Friend events ──────────────────────────────────────────────

    @poller.on_friend_online
    def on_online(user):
        print(f"🟢 {user.display_name} (@{user.name}) just came online!")

    @poller.on_friend_offline
    def on_offline(user):
        print(f"⚫ {user.display_name} went offline.")

    @poller.on_new_friend
    def on_new_friend(user):
        print(f"🤝 New friend: {user.display_name} (@{user.name}) [ID: {user.id}]")

    @poller.on_friend_removed
    def on_removed(user_id):
        print(f"❌ Unfriended by user ID: {user_id}")

    @poller.on_friend_request
    def on_request(user):
        print(f"📨 Friend request from {user.display_name} (@{user.name})")

    # ── Message events ─────────────────────────────────────────────

    @poller.on_new_message
    def on_message(count):
        print(f"✉️  You have {count} unread message(s)!")

    # ── Visit milestones ───────────────────────────────────────────

    UNIVERSE_ID = 2753915549  # Replace with your universe
    poller.track_game(UNIVERSE_ID, milestone_step=1_000_000)

    @poller.on("visit_milestone")
    def on_milestone(game, count):
        print(f"🎉 {game.name} just hit {count:,} visits!")

    # ── Start ──────────────────────────────────────────────────────

    print("Event monitor started. Polling every 30 seconds.")
    print("Press Ctrl+C to stop.\n")
    poller.start(interval=30, daemon=False)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        poller.stop()
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
