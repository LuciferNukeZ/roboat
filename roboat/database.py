"""
roboat.database
~~~~~~~~~~~~~~~~~~
Local SQLite-backed session database.
Stores user data, game data, and session history locally.
"""

from __future__ import annotations
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Any
from .exceptions import DatabaseError


class SessionDatabase:
    """
    Lightweight local SQLite database for persisting roboat session data.

    Usage::

        db = SessionDatabase.create("mysession")   # new DB
        db = SessionDatabase.load("mysession")     # existing DB

    Tables:
        users    — cached user records
        games    — cached game records
        sessions — session metadata / notes
        log      — command history
    """

    _EXTENSION = ".robloxdb"

    def __init__(self, path: str):
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self._conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._init_schema()

    # ------------------------------------------------------------------ #
    #  Factory methods                                                     #
    # ------------------------------------------------------------------ #

    @classmethod
    def create(cls, name: str, directory: str = ".") -> "SessionDatabase":
        """Create a new database. Raises if it already exists."""
        path = cls._resolve_path(name, directory)
        if os.path.exists(path):
            raise DatabaseError(f"Database '{name}' already exists at {path}. Use load() instead.")
        return cls(path)

    @classmethod
    def load(cls, name: str, directory: str = ".") -> "SessionDatabase":
        """Load an existing database. Raises if not found."""
        path = cls._resolve_path(name, directory)
        if not os.path.exists(path):
            raise DatabaseError(f"Database '{name}' not found at {path}. Use create() instead.")
        return cls(path)

    @classmethod
    def load_or_create(cls, name: str, directory: str = ".") -> "SessionDatabase":
        """Load if exists, otherwise create."""
        path = cls._resolve_path(name, directory)
        return cls(path)

    @classmethod
    def _resolve_path(cls, name: str, directory: str) -> str:
        if not name.endswith(cls._EXTENSION):
            name = name + cls._EXTENSION
        return os.path.join(directory, name)

    @classmethod
    def list_databases(cls, directory: str = ".") -> list:
        """List all .robloxdb files in a directory."""
        try:
            return [
                f[:-len(cls._EXTENSION)]
                for f in os.listdir(directory)
                if f.endswith(cls._EXTENSION)
            ]
        except FileNotFoundError:
            return []

    # ------------------------------------------------------------------ #
    #  Connection                                                          #
    # ------------------------------------------------------------------ #

    def _connect(self):
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def _init_schema(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                display_name TEXT,
                description TEXT,
                is_banned   INTEGER DEFAULT 0,
                verified    INTEGER DEFAULT 0,
                cached_at   TEXT
            );

            CREATE TABLE IF NOT EXISTS games (
                universe_id  INTEGER PRIMARY KEY,
                place_id     INTEGER,
                name         TEXT,
                description  TEXT,
                creator_name TEXT,
                visits       INTEGER DEFAULT 0,
                playing      INTEGER DEFAULT 0,
                max_players  INTEGER DEFAULT 0,
                genre        TEXT,
                cached_at    TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                key         TEXT UNIQUE,
                value       TEXT,
                updated_at  TEXT
            );

            CREATE TABLE IF NOT EXISTS log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                command     TEXT,
                result      TEXT,
                ran_at      TEXT
            );
        """)
        self._conn.commit()

    # ------------------------------------------------------------------ #
    #  Users                                                               #
    # ------------------------------------------------------------------ #

    def save_user(self, user) -> None:
        """Cache a User model to the database."""
        self._conn.execute("""
            INSERT OR REPLACE INTO users
              (user_id, username, display_name, description, is_banned, verified, cached_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user.id, user.name, user.display_name, user.description,
            int(user.is_banned), int(user.has_verified_badge),
            datetime.utcnow().isoformat(),
        ))
        self._conn.commit()

    def get_user(self, user_id: int) -> Optional[dict]:
        """Retrieve a cached user by ID."""
        row = self._conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_users(self) -> list:
        rows = self._conn.execute("SELECT * FROM users ORDER BY cached_at DESC").fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    #  Games                                                               #
    # ------------------------------------------------------------------ #

    def save_game(self, game) -> None:
        """Cache a Game model to the database."""
        self._conn.execute("""
            INSERT OR REPLACE INTO games
              (universe_id, place_id, name, description, creator_name,
               visits, playing, max_players, genre, cached_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            game.id, game.root_place_id, game.name, game.description,
            game.creator_name, game.visits, game.playing, game.max_players,
            game.genre, datetime.utcnow().isoformat(),
        ))
        self._conn.commit()

    def get_game(self, universe_id: int) -> Optional[dict]:
        row = self._conn.execute(
            "SELECT * FROM games WHERE universe_id = ?", (universe_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_games(self) -> list:
        rows = self._conn.execute("SELECT * FROM games ORDER BY visits DESC").fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    #  Session key-value store                                            #
    # ------------------------------------------------------------------ #

    def set(self, key: str, value: Any) -> None:
        """Store any JSON-serialisable value under a key."""
        self._conn.execute("""
            INSERT OR REPLACE INTO sessions (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, json.dumps(value), datetime.utcnow().isoformat()))
        self._conn.commit()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a stored value by key."""
        row = self._conn.execute(
            "SELECT value FROM sessions WHERE key = ?", (key,)
        ).fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except Exception:
                return row["value"]
        return default

    def delete(self, key: str) -> None:
        self._conn.execute("DELETE FROM sessions WHERE key = ?", (key,))
        self._conn.commit()

    def keys(self) -> list:
        rows = self._conn.execute("SELECT key FROM sessions").fetchall()
        return [r["key"] for r in rows]

    # ------------------------------------------------------------------ #
    #  Log                                                                 #
    # ------------------------------------------------------------------ #

    def log_command(self, command: str, result: str = "") -> None:
        """Log a terminal command and its result."""
        self._conn.execute(
            "INSERT INTO log (command, result, ran_at) VALUES (?, ?, ?)",
            (command, result[:500], datetime.utcnow().isoformat()),
        )
        self._conn.commit()

    def get_log(self, limit: int = 50) -> list:
        rows = self._conn.execute(
            "SELECT * FROM log ORDER BY ran_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    #  Stats                                                               #
    # ------------------------------------------------------------------ #

    def stats(self) -> dict:
        users = self._conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        games = self._conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        logs  = self._conn.execute("SELECT COUNT(*) FROM log").fetchone()[0]
        keys  = self._conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        return {"users": users, "games": games, "session_keys": keys, "log_entries": logs}

    def __repr__(self) -> str:
        return f"<SessionDatabase '{self.name}' at {self.path}>"
