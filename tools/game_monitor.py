"""
tools/game_monitor.py
~~~~~~~~~~~~~~~~~~~~~
CLI tool: continuously monitor game stats and alert on changes.

Usage:
  python tools/game_monitor.py --universe 2753915549 --interval 60
  python tools/game_monitor.py --universe 2753915549 --milestone 1000000
"""

import argparse
import time
import sys
from roboat import RoboatClient


def monitor(client: RoboatClient, universe_id: int,
            interval: int, milestone_step: int):
    print(f"\nMonitoring universe {universe_id}")
    print(f"Interval: {interval}s  |  Milestone step: {milestone_step:,}")
    print("Press Ctrl+C to stop.\n")

    last_visits  = None
    last_playing = None
    next_milestone = None

    try:
        while True:
            try:
                game  = client.games.get_game(universe_id)
                votes = client.games.get_votes([universe_id])
                ratio = votes[0].ratio if votes else 0.0

                ts = time.strftime("%H:%M:%S")

                if last_visits is None:
                    next_milestone = ((game.visits // milestone_step) + 1) * milestone_step
                    print(f"[{ts}] Starting: {game.name}")
                    print(f"         Visits : {game.visits:,}")
                    print(f"         Playing: {game.playing:,}")
                    print(f"         Votes  : {ratio}%")
                    print(f"         Next milestone: {next_milestone:,} visits\n")
                else:
                    visit_delta   = game.visits - last_visits
                    playing_delta = game.playing - last_playing
                    v_sign = "+" if visit_delta >= 0 else ""
                    p_sign = "+" if playing_delta >= 0 else ""

                    print(
                        f"[{ts}]  "
                        f"Visits: {game.visits:>15,}  ({v_sign}{visit_delta:,})  |  "
                        f"Playing: {game.playing:>6,}  ({p_sign}{playing_delta})  |  "
                        f"Votes: {ratio}%"
                    )

                    if next_milestone and game.visits >= next_milestone:
                        print(f"\n  🎉 MILESTONE: {game.name} hit {next_milestone:,} visits!\n")
                        next_milestone += milestone_step

                last_visits  = game.visits
                last_playing = game.playing

            except Exception as e:
                print(f"  ⚠️  Error: {e}", file=sys.stderr)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitor stopped.")


def main():
    parser = argparse.ArgumentParser(description="roboat game monitor")
    parser.add_argument("--universe",  type=int, required=True, help="Universe ID to monitor")
    parser.add_argument("--interval",  type=int, default=60,    help="Poll interval in seconds (default: 60)")
    parser.add_argument("--milestone", type=int, default=1_000_000, help="Visit milestone step (default: 1M)")
    args = parser.parse_args()

    client = RoboatClient()
    monitor(client, args.universe, args.interval, args.milestone)


if __name__ == "__main__":
    main()
