# Architecture

This document explains how roboat is structured internally.

---

## Overview

```
Request
  │
  ▼
RoboatClient
  ├── TokenBucket (rate limiter)      ← throttles before sending
  ├── TTLCache (response cache)       ← short-circuits if cached
  ├── requests.Session (HTTP)         ← actual network call
  └── _handle_response()             ← maps status → typed exception
         │
         ▼
    Sub-API (e.g. UsersAPI)
         │
         ▼
    Typed Model (e.g. User)          ← returned to caller
```

---

## Client Layer (`client.py`)

`RoboatClient` is the central hub. It owns:

- A single `requests.Session` reused across all requests
- A `TokenBucket` that blocks any request that would exceed the configured rate
- A `TTLCache` checked before every GET request
- CSRF token management — captured on 403 and injected into the session headers automatically
- All sub-API instances attached as attributes (`self.users`, `self.games`, etc.)

`ClientBuilder` is a fluent builder that constructs `RoboatClient` with all optional configuration set before instantiation.

---

## Sub-API Layer

Each sub-API module (`users.py`, `games.py`, etc.) holds a reference to the client (`self._c`) and uses `self._c._get()` / `self._c._post()` for all HTTP calls. Sub-APIs never manage sessions, headers, or rate limiting — those concerns belong entirely to the client.

Responsibilities of a sub-API:
- Build URL and params for each endpoint
- Call `_get` / `_post` / `_patch` / `_delete`
- Wrap the response dict in typed model objects
- Require auth via `self._c.require_auth(method_name)` where needed

---

## Model Layer (`models.py`)

Every public API response is a `@dataclass` with:

- `from_dict(cls, d: dict)` — constructs the model from a raw response dict
- `__str__` — human-readable representation for terminal printing
- Computed properties where useful (e.g. `GameVotes.ratio`, `UserPresence.status`)

Models never make network calls. They are pure data containers.

---

## Utils Layer (`utils/`)

Three focused utilities:

**`TTLCache`** — thread-safe LRU cache with per-entry TTL. Uses `threading.Lock`. Evicts least recently used entries when `max_size` is reached.

**`TokenBucket`** — token bucket rate limiter. Tokens replenish at `rate` per second up to `capacity`. `consume()` blocks until a token is available. Thread-safe.

**`@retry`** — decorator with configurable max attempts, initial backoff, and backoff multiplier. Catches specified exception types and retries with exponential delay.

**`Paginator`** — lazy iterator that calls a user-supplied `fetch_fn(cursor)` repeatedly, yielding items from each `Page` until `next_cursor` is None. Supports `max_items` early termination.

---

## Async Layer (`async_client.py`)

`AsyncRoboatClient` is a parallel implementation using `aiohttp`. It mirrors the sync client's sub-API structure but every method is a coroutine. It does not share the sync client's session, cache, or rate limiter — it manages its own `aiohttp.ClientSession`.

Key difference: bulk user fetching (`get_users_by_ids`) automatically chunks large lists into batches of 100 and awaits them sequentially to avoid overloading the endpoint.

---

## OAuth Layer (`oauth.py`)

`OAuthManager` manages the OAuth 2.0 flow:

1. Opens the Roblox authorization URL in the system browser
2. Starts a background `threading.Thread` that waits `timeout` seconds
3. If `receive_token(token)` is called before timeout → calls `on_success`
4. If timeout expires with no token → calls `on_failure`

The `OAuthState` class holds state (`pending` / `success` / `failed`) and a `threading.Event` for synchronization.

---

## Database Layer (`database.py`)

`SessionDatabase` wraps Python's built-in `sqlite3`. Schema:

| Table | Purpose |
|---|---|
| `users` | Cached user records with timestamp |
| `games` | Cached game records with timestamp |
| `sessions` | Arbitrary key-value JSON store |
| `log` | Terminal command history |

All writes are committed immediately. Reads return `None` for missing keys rather than raising. The key-value store serialises values with `json.dumps` and deserialises with `json.loads`.

---

## Event System (`events.py`)

`EventPoller` runs a background daemon thread that calls `_poll()` on an interval. `_poll()` calls three sub-routines:

- `_poll_friends()` — fetches friends + presence, compares to previous state, fires callbacks
- `_poll_games()` — checks tracked universe visit counts against milestone thresholds
- `_poll_messages()` — checks unread message count delta

Callbacks are stored in a `dict[str, List[Callable]]`. `_fire(event, *args)` iterates handlers and calls each, ignoring exceptions so one bad handler doesn't break the loop.

---

## Session (REPL) Layer (`session.py`)

`RoboatSession` is a simple synchronous REPL:

1. Displays a banner and starts a `while` loop
2. Reads input with `input()`
3. Splits on whitespace to get `cmd` and `args`
4. Enforces session guard (blocks non-setup commands until `start <userid>` is called)
5. Looks up the handler in a dispatch dict
6. Calls the handler, catching `RoboatAPIError` and `NotAuthenticatedError`

The `auth` command runs a live countdown loop using `sys.stdout.write` with `\r` for in-place updating.
