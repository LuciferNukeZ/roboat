"""
examples/async_parallel.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Async client — fetch multiple resources in parallel.
Requires: pip install roboat[async]
"""

import asyncio
from roboat import AsyncRoboatClient


async def parallel_game_data():
    """Fetch game details, votes, and thumbnails all at once."""
    async with AsyncRoboatClient() as client:
        universe_id = 2753915549

        game, votes, icons, servers = await asyncio.gather(
            client.games.get_game(universe_id),
            client.games.get_votes([universe_id]),
            client.thumbnails.get_game_icons([universe_id]),
            client.games.get_servers(4483381587, limit=5),
        )

        print(game)
        print(votes[0])
        print(f"Icon: {icons.get(universe_id)}")
        print(f"Servers: {len(servers.data)} active")


async def bulk_user_fetch():
    """Fetch 500 users in parallel — auto-chunked into batches of 100."""
    async with AsyncRoboatClient() as client:
        user_ids = list(range(1, 501))
        users = await client.users.get_users_by_ids(user_ids)
        print(f"Fetched {len(users)} users")

        # Sort by ID
        users.sort(key=lambda u: u.id)
        for u in users[:10]:
            print(f"  {u.id}: {u.name}")


async def friend_presence_monitor():
    """Check online status of friends in bulk."""
    async with AsyncRoboatClient() as client:
        friends = await client.friends.get_friends(156)
        friend_ids = [f.id for f in friends[:50]]

        if not friend_ids:
            print("No friends found (or private)")
            return

        presences = await client.presence.get_presences(friend_ids)
        online = [p for p in presences if p.user_presence_type > 0]

        print(f"{len(online)}/{len(friend_ids)} friends online")
        for p in online:
            print(f"  {p.user_id}: {p.status} — {p.last_location or 'Unknown'}")


async def main():
    print("=== Parallel Game Data ===")
    await parallel_game_data()

    print("\n=== Bulk User Fetch ===")
    await bulk_user_fetch()

    print("\n=== Friend Presence ===")
    await friend_presence_monitor()


if __name__ == "__main__":
    asyncio.run(main())
