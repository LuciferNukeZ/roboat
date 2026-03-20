"""
roboat.session
~~~~~~~~~~~~~~
Interactive terminal session — OAuth-based, no cookie required.
"""

from __future__ import annotations
import sys
import os
import textwrap
import threading
import time
import webbrowser
from typing import Optional

from .client import RoboatClient
from .database import SessionDatabase
from .exceptions import RoboatAPIError, DatabaseError, NotAuthenticatedError
from .oauth import OAUTH_URL, TIMEOUT

# ── ANSI colours ──────────────────────────────────────────────────────────── #

class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

    @staticmethod
    def _supports_color() -> bool:
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(text: str, color: str) -> str:
    return f"{color}{text}{C.RESET}" if C._supports_color() else text


BANNER = r"""
  ____       _     _            _    ____ ___
 |  _ \ ___ | |__ | | _____  __/ \  |  _ \_ _|
 | |_) / _ \| '_ \| |/ _ \ \/ / _ \ | |_) | |
 |  _ < (_) | |_) | | (_) >  < ___ \|  __/| |
 |_| \_\___/|_.__/|_|\___/_/\_/_/  \_|_|  |___|
"""

VERSION = "2.0.0"


class RoboatSession:
    """
    Interactive terminal REPL for roboat.
    Uses OAuth for authentication — no cookie required.

    Usage:
        roboat
        python -m roboat
    """

    def __init__(self):
        self.client: RoboatClient = RoboatClient()
        self.db: Optional[SessionDatabase] = None
        self.session_user_id: Optional[int] = None
        self.session_username: Optional[str] = None
        self._running = False
        self._history: list = []
        self._auth_pending = False

    # ── I/O ───────────────────────────────────────────────────────────────── #

    def _print(self, text: str = ""):
        print(text)

    def _ok(self, text: str):
        print(_c(f"  ✔  {text}", C.GREEN))

    def _err(self, text: str):
        print(_c(f"  ✖  {text}", C.RED))

    def _info(self, text: str):
        print(_c(f"  ℹ  {text}", C.CYAN))

    def _warn(self, text: str):
        print(_c(f"  ⚠  {text}", C.YELLOW))

    def _section(self, title: str):
        w = 56
        line = "─" * w
        print()
        print(_c(f"┌{line}┐", C.BLUE))
        print(_c(f"│{f' {title} '.center(w)}│", C.BOLD + C.WHITE))
        print(_c(f"└{line}┘", C.BLUE))

    def _prompt(self) -> str:
        db_tag   = _c(f"[{self.db.name}] ", C.GRAY) if self.db else ""
        user_tag = _c(f"{self.session_username} ", C.CYAN) if self.session_username else ""
        arrow    = _c("» ", C.YELLOW)
        try:
            raw = input(f"\n{db_tag}{user_tag}{arrow}")
        except (EOFError, KeyboardInterrupt):
            print()
            return "exit"
        return raw.strip()

    def _require_session(self) -> bool:
        """Return False and print message if no session started."""
        if self.session_user_id is None:
            self._warn("Please run  start <userid>  first.")
            return False
        return True

    def _log(self, cmd: str, result: str = ""):
        self._history.append(cmd)
        if self.db:
            try:
                self.db.log_command(cmd, result)
            except Exception:
                pass

    # ── Entry point ───────────────────────────────────────────────────────── #

    def run(self):
        os.system("cls" if os.name == "nt" else "clear")
        print(_c(BANNER, C.CYAN + C.BOLD))
        print(_c(f"  roboat v{VERSION}  —  type 'help' to begin", C.GRAY))
        print()
        self._running = True
        while self._running:
            raw = self._prompt()
            if not raw:
                continue
            self._dispatch(raw)

    # ── Dispatch ──────────────────────────────────────────────────────────── #

    def _dispatch(self, raw: str):
        parts = raw.split(None, 2)
        cmd   = parts[0].lower()
        args  = parts[1:]
        self._log(raw)

        # Commands that don't need a session
        no_session_ok = {
            "help", "exit", "quit", "clear", "start",
            "auth", "newdb", "loaddb", "listdb", "history",
        }

        if cmd not in no_session_ok and self.session_user_id is None:
            self._warn("Please run  start <userid>  first.")
            return

        handlers = {
            "help":      self._cmd_help,
            "exit":      self._cmd_exit,
            "quit":      self._cmd_exit,
            "clear":     self._cmd_clear,
            "start":     self._cmd_start,
            "auth":      self._cmd_auth,
            "whoami":    self._cmd_whoami,
            "newdb":     self._cmd_newdb,
            "loaddb":    self._cmd_loaddb,
            "listdb":    self._cmd_listdb,
            "user":      self._cmd_user,
            "game":      self._cmd_game,
            "friends":   self._cmd_friends,
            "followers": self._cmd_followers,
            "likes":     self._cmd_likes,
            "search":    self._cmd_search,
            "presence":  self._cmd_presence,
            "avatar":    self._cmd_avatar,
            "servers":   self._cmd_servers,
            "badges":    self._cmd_badges,
            "catalog":   self._cmd_catalog,
            "trades":    self._cmd_trades,
            "inventory": self._cmd_inventory,
            "rap":       self._cmd_rap,
            "messages":  self._cmd_messages,
            "owns":      self._cmd_owns,
            "universe":  self._cmd_universe,
            "save":      self._cmd_save,
            "history":   self._cmd_history,
            "cache":     self._cmd_cache,
            "watch":     self._cmd_watch,
        }
        handler = handlers.get(cmd)
        if handler:
            try:
                handler(args)
            except NotAuthenticatedError:
                self._warn("This command requires authentication. Run  auth  first.")
            except RoboatAPIError as e:
                self._err(str(e))
            except Exception as e:
                self._err(f"Unexpected error: {e}")
        else:
            self._err(f"Unknown command '{cmd}'. Type 'help' for commands.")

    # ── Commands ──────────────────────────────────────────────────────────── #

    def _cmd_help(self, args):
        self._section("Commands")
        cmds = [
            ("start <userid>",      "Begin session as a Roblox user"),
            ("auth",                "Authenticate via Roblox OAuth (opens browser)"),
            ("whoami",              "Show current session user"),
            ("",                    ""),
            ("newdb <name>",        "Create a new local database"),
            ("loaddb <name>",       "Load an existing database"),
            ("listdb",              "List all local databases"),
            ("",                    ""),
            ("user <userid>",       "Fetch user profile"),
            ("game <universeid>",   "Fetch game + visit stats"),
            ("friends <userid>",    "Get friends list"),
            ("followers <userid>",  "Get follower count & list"),
            ("likes <universeid>",  "Get game vote stats"),
            ("search user <kw>",    "Search users by keyword"),
            ("search game <kw>",    "Search games by keyword"),
            ("presence <userid>",   "Get user online status"),
            ("avatar <userid>",     "Get user avatar details"),
            ("servers <placeid>",   "List active game servers"),
            ("badges <universeid>", "List badges in a game"),
            ("catalog <keyword>",   "Search the avatar catalog"),
            ("trades",              "View your trades (needs auth)"),
            ("inventory <userid>",  "View user limiteds + RAP"),
            ("rap <userid>",        "Calculate total RAP"),
            ("messages",            "View private messages (needs auth)"),
            ("owns <uid> <assetid>","Check if user owns an asset"),
            ("universe <id>",       "View universe/game developer info"),
            ("",                    ""),
            ("save user <id>",      "Save user to current DB"),
            ("save game <id>",      "Save game to current DB"),
            ("cache [clear]",       "Show or clear response cache"),
            ("watch <universeid>",  "Monitor game visit milestones"),
            ("history",             "Show command history"),
            ("clear",               "Clear the screen"),
            ("exit",                "Exit the session"),
        ]
        for cmd, desc in cmds:
            if not cmd:
                print()
                continue
            print(f"  {_c(cmd.ljust(24), C.YELLOW)}  {_c(desc, C.WHITE)}")
        print()

    def _cmd_exit(self, args):
        self._ok("Goodbye!")
        if self.db:
            self.db.close()
        self._running = False
        sys.exit(0)

    def _cmd_clear(self, args):
        os.system("cls" if os.name == "nt" else "clear")

    def _cmd_start(self, args):
        if not args:
            self._err("Usage: start <userid>")
            return
        try:
            uid = int(args[0])
        except ValueError:
            self._err("User ID must be an integer.")
            return
        self._info(f"Fetching user {uid}...")
        user = self.client.users.get_user(uid)
        self.session_user_id  = user.id
        self.session_username = user.name
        self._section("Session Started")
        print(f"  {user}")
        presence = self.client.presence.get_presence(uid)
        self._info(f"Status: {presence.status}")
        if self.db:
            self.db.save_user(user)
            self.db.set("session_user_id", uid)

    def _cmd_auth(self, args):
        """Authenticate via Roblox OAuth. Opens browser and waits up to 120s."""
        self._section("Roblox OAuth Authentication")
        self._info("Opening Roblox authorization page in your browser...")
        self._info("You have 120 seconds to complete the login.")
        print()
        print(_c(f"  URL: {OAUTH_URL}", C.GRAY))
        print()

        webbrowser.open(OAUTH_URL)
        self._auth_pending = True

        # Countdown display
        deadline = time.time() + TIMEOUT
        authenticated = False

        def _wait():
            nonlocal authenticated
            # In a real deployment you'd receive the token via a callback server.
            # Here we wait for the timeout and mark as failed unless receive_token() is called.
            time.sleep(TIMEOUT)

        t = threading.Thread(target=_wait, daemon=True)
        t.start()

        try:
            for remaining in range(TIMEOUT, 0, -1):
                if not self._auth_pending:
                    authenticated = True
                    break
                sys.stdout.write(
                    f"\r  {_c(f'Waiting... {remaining}s remaining', C.YELLOW)}  "
                )
                sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        print()
        self._auth_pending = False

        if authenticated:
            self._ok("Authentication successful!")
        else:
            self._err("Authentication failed — timed out after 120 seconds.")
            self._info("Visit the URL above in your browser and try again.")

    def _cmd_whoami(self, args):
        if not self.session_user_id:
            self._warn("No session started. Use: start <userid>")
            return
        self._info(f"@{self.session_username} (ID: {self.session_user_id})")
        auth = "Authenticated" if self.client.is_authenticated else "Not authenticated (run 'auth')"
        self._info(f"Auth: {auth}")

    def _cmd_newdb(self, args):
        if not args:
            self._err("Usage: newdb <name>")
            return
        try:
            self.db = SessionDatabase.create(args[0])
            self._ok(f"Created database '{args[0]}' → {self.db.path}")
        except DatabaseError as e:
            self._err(str(e))

    def _cmd_loaddb(self, args):
        if not args:
            self._err("Usage: loaddb <name>")
            return
        try:
            self.db = SessionDatabase.load(args[0])
            s = self.db.stats()
            self._ok(f"Loaded '{args[0]}' — {s['users']} users, {s['games']} games")
        except DatabaseError as e:
            self._err(str(e))

    def _cmd_listdb(self, args):
        dbs = SessionDatabase.list_databases(".")
        if not dbs:
            self._warn("No databases found in current directory.")
            return
        self._section("Local Databases")
        for name in dbs:
            active = _c(" ← active", C.GREEN) if (self.db and self.db.name == name) else ""
            print(f"  {_c('•', C.CYAN)} {name}{active}")

    def _cmd_user(self, args):
        if not args:
            self._err("Usage: user <userid>")
            return
        try:
            uid = int(args[0])
        except ValueError:
            self._err("User ID must be an integer."); return
        user = self.client.users.get_user(uid)
        self._section("User Profile")
        print(f"  {user}")
        if user.description:
            self._info(f"Bio: {textwrap.shorten(user.description, 60, placeholder='...')}")
        fc = self.client.friends.get_friend_count(uid)
        fl = self.client.friends.get_follower_count(uid)
        self._info(f"Friends: {fc:,}  |  Followers: {fl:,}")

    def _cmd_game(self, args):
        if not args:
            self._err("Usage: game <universeid>"); return
        try:
            uid = int(args[0])
        except ValueError:
            self._err("Universe ID must be an integer."); return
        game = self.client.games.get_game(uid)
        self._section("Game Info")
        print(f"  {game}")
        votes = self.client.games.get_votes([uid])
        if votes:
            self._info(f"Votes: {votes[0]}")
        if self.db:
            self.db.save_game(game)
            self._ok("Saved to database.")

    def _cmd_friends(self, args):
        uid = int(args[0]) if args else self.session_user_id
        friends = self.client.friends.get_friends(uid)
        self._section(f"Friends ({len(friends)})")
        for i, f in enumerate(friends[:20], 1):
            print(f"  {i:>3}. {f}")
        if len(friends) > 20:
            self._info(f"... and {len(friends)-20} more.")

    def _cmd_followers(self, args):
        if not args:
            self._err("Usage: followers <userid>"); return
        uid   = int(args[0])
        count = self.client.friends.get_follower_count(uid)
        fol   = self.client.friends.get_following_count(uid)
        page  = self.client.friends.get_followers(uid, limit=10)
        self._section(f"Followers ({count:,})")
        self._info(f"Following: {fol:,}")
        for f in page.data[:10]:
            print(f"  {f}")

    def _cmd_likes(self, args):
        if not args:
            self._err("Usage: likes <universeid>"); return
        uid   = int(args[0])
        votes = self.client.games.get_votes([uid])
        if not votes:
            self._warn("No vote data found."); return
        self._section("Game Votes")
        print(f"  {votes[0]}")
        fav = self.client.games.get_favorite_count(uid)
        self._info(f"Favourites: {fav:,}")

    def _cmd_search(self, args):
        if len(args) < 2:
            self._err("Usage: search user <kw>  |  search game <kw>"); return
        kind, keyword = args[0].lower(), args[1]
        if kind == "user":
            page = self.client.users.search_users(keyword, limit=10)
            self._section(f"User Search: '{keyword}'")
            for u in page.data:
                print(f"  {u}")
        elif kind == "game":
            page = self.client.games.search_games(keyword, limit=10)
            self._section(f"Game Search: '{keyword}'")
            for g in page.data:
                print(f"  {g.name} [ID: {g.id}] — {g.visits:,} visits")
        else:
            self._err("Type must be 'user' or 'game'.")

    def _cmd_presence(self, args):
        if not args:
            self._err("Usage: presence <userid>"); return
        uid = int(args[0])
        p   = self.client.presence.get_presence(uid)
        self._section("User Presence")
        self._info(f"User ID : {uid}")
        self._info(f"Status  : {p.status}")
        if p.last_location:
            self._info(f"Location: {p.last_location}")
        if p.last_online:
            self._info(f"Last Online: {p.last_online}")

    def _cmd_avatar(self, args):
        if not args:
            self._err("Usage: avatar <userid>"); return
        uid  = int(args[0])
        av   = self.client.avatar.get_user_avatar(uid)
        self._section("Avatar Info")
        self._info(f"Type  : {av.avatar_type}")
        self._info(f"Assets: {len(av.assets)} equipped items")
        self._info(f"Scales: {av.scales}")
        url = self.client.thumbnails.get_avatar_url(uid)
        if url:
            self._info(f"Thumbnail: {url}")

    def _cmd_servers(self, args):
        if not args:
            self._err("Usage: servers <placeid>"); return
        pid  = int(args[0])
        page = self.client.games.get_servers(pid, limit=10)
        self._section("Active Servers")
        if not page.data:
            self._warn("No active servers found."); return
        for s in page.data:
            print(f"  {s}")

    def _cmd_badges(self, args):
        if not args:
            self._err("Usage: badges <universeid>"); return
        uid  = int(args[0])
        page = self.client.badges.get_universe_badges(uid, limit=15)
        self._section("Game Badges")
        if not page.data:
            self._warn("No badges found."); return
        for b in page.data:
            print(f"  {b}")
            print()

    def _cmd_catalog(self, args):
        if not args:
            self._err("Usage: catalog <keyword>"); return
        keyword = " ".join(args)
        page    = self.client.catalog.search(keyword=keyword, limit=10)
        self._section(f"Catalog: '{keyword}'")
        if not page.data:
            self._warn("No items found."); return
        for item in page.data:
            price = f"{item.price}R$" if item.price else "Free/Off Sale"
            print(f"  [{item.id}] {item.name} — {price}")

    def _cmd_trades(self, args):
        trade_type = args[0].capitalize() if args else "Inbound"
        page = self.client.trades.get_trades(trade_type, limit=10)
        self._section(f"Trades — {trade_type} ({len(page.data)})")
        if not page.data:
            self._warn("No trades found."); return
        for t in page.data:
            print(f"  {t}")

    def _cmd_inventory(self, args):
        if not args:
            self._err("Usage: inventory <userid>"); return
        uid  = int(args[0])
        page = self.client.inventory.get_collectibles(uid, limit=25)
        self._section(f"Inventory (Limiteds) — User {uid}")
        if not page.data:
            self._warn("No collectibles found (or inventory is private)."); return
        total_rap = sum(a.recent_average_price for a in page.data)
        for asset in page.data:
            print(f"  {asset}")
        self._info(f"Shown RAP total: {total_rap:,}R$")

    def _cmd_rap(self, args):
        uid   = int(args[0]) if args else self.session_user_id
        self._info(f"Calculating RAP for user {uid}...")
        total = self.client.inventory.get_total_rap(uid)
        self._section("Total RAP")
        print(f"  {_c(f'📈 {total:,}R$ RAP', C.GREEN + C.BOLD)}")

    def _cmd_messages(self, args):
        unread = self.client.messages.get_unread_count()
        page   = self.client.messages.get_messages(page_size=10)
        self._section(f"Messages ({unread} unread)")
        if not page.data:
            self._warn("No messages."); return
        for m in page.data:
            print(f"  {m}")

    def _cmd_owns(self, args):
        if len(args) < 2:
            self._err("Usage: owns <userid> <assetid>"); return
        uid, aid = int(args[0]), int(args[1])
        result = self.client.inventory.owns_asset(uid, aid)
        if result:
            self._ok(f"User {uid} owns asset {aid}")
        else:
            self._warn(f"User {uid} does NOT own asset {aid}")

    def _cmd_universe(self, args):
        if not args:
            self._err("Usage: universe <universeid>"); return
        uid = int(args[0])
        u   = self.client.develop.get_universe(uid)
        self._section("Universe Info")
        print(f"  {u}")

    def _cmd_save(self, args):
        if not self.db:
            self._err("No database loaded. Use: newdb <n> or loaddb <n>"); return
        if len(args) < 2:
            self._err("Usage: save user <userid>  |  save game <universeid>"); return
        kind, obj_id = args[0].lower(), int(args[1])
        if kind == "user":
            user = self.client.users.get_user(obj_id)
            self.db.save_user(user)
            self._ok(f"Saved user {user.name} to '{self.db.name}'")
        elif kind == "game":
            game = self.client.games.get_game(obj_id)
            self.db.save_game(game)
            self._ok(f"Saved game '{game.name}' to '{self.db.name}'")
        else:
            self._err("Type must be 'user' or 'game'.")

    def _cmd_cache(self, args):
        stats = self.client.cache_stats()
        self._section("Cache Stats")
        self._info(f"Alive : {stats['alive']}")
        self._info(f"Total : {stats['total']}")
        self._info(f"Max   : {stats['max_size']}")
        if args and args[0] == "clear":
            self.client.invalidate_cache()
            self._ok("Cache cleared.")

    def _cmd_watch(self, args):
        if not args:
            self._err("Usage: watch <universeid>"); return
        uid = int(args[0])
        self.client.events.track_game(uid)

        @self.client.events.on("visit_milestone")
        def _on_milestone(game, count):
            self._warn(f"🎉 {game.name} hit {count:,} visits!")

        self.client.events.start(interval=60)
        self._ok(f"Watching universe {uid} for milestones every 60s.")

    def _cmd_history(self, args):
        self._section("Command History")
        if not self._history:
            self._warn("No commands yet."); return
        for i, cmd in enumerate(self._history[-20:], 1):
            print(f"  {_c(str(i).rjust(3), C.GRAY)}  {cmd}")


def _cli_entry():
    RoboatSession().run()
