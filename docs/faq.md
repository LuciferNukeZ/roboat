# Frequently Asked Questions

---

### Why OAuth instead of a cookie?

The `.ROBLOSECURITY` cookie approach is fragile — it breaks on password changes, requires manual browser extraction, and is effectively an undocumented private token not intended for external use. OAuth 2.0 is Roblox's official authentication mechanism for external applications and is more secure, more explicit about permissions, and more maintainable long-term.

---

### Does roboat work without authentication?

Yes. The vast majority of endpoints — user lookup, game info, catalog search, thumbnails, presence, badges, groups, friends — are fully public and work without any authentication. Authentication is only required for actions that involve your account (trades, messages, group payouts, etc.).

---

### What Python version do I need?

Python 3.8 or higher. roboat uses `from __future__ import annotations` and dataclasses, both available from 3.8. It is tested on 3.8 through 3.12.

---

### How do I use roboat in an async application?

```python
from roboat import AsyncRoboatClient
import asyncio

async def main():
    async with AsyncRoboatClient() as client:
        user = await client.users.get_user(156)
        print(user)

asyncio.run(main())
```

Install `aiohttp` first: `pip install "roboat[async]"`

---

### Why am I getting rate limited?

Roblox rate limits most endpoints. The built-in `TokenBucket` rate limiter helps by throttling requests before they go out, but if you are making very large numbers of requests you may still get 429s. Use `@retry` to handle them automatically:

```python
from roboat.utils import retry
from roboat import RateLimitedError

@retry(max_attempts=5, backoff=2.0, exceptions=(RateLimitedError,))
def fetch(uid):
    return client.users.get_user(uid)
```

---

### How do I fetch all followers of a user?

Use `Paginator`:

```python
from roboat.utils import Paginator

all_followers = Paginator(
    lambda c: client.friends.get_followers(156, limit=100, cursor=c)
).collect()
```

---

### Can I use a proxy?

Yes, via `ClientBuilder`:

```python
from roboat import ClientBuilder

client = (
    ClientBuilder()
    .set_proxy("http://your-proxy:8080")
    .build()
)
```

For async, aiohttp proxy support is handled per-request (not yet built into `AsyncRoboatClient` directly).

---

### How do I store an OAuth token securely?

Never hardcode it. Use environment variables:

```python
import os
from roboat import RoboatClient

client = RoboatClient(oauth_token=os.environ["ROBOAT_TOKEN"])
```

Or use a `.env` file with `python-dotenv`:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
client = RoboatClient(oauth_token=os.environ["ROBOAT_TOKEN"])
```

---

### What is the `.robloxdb` file?

It is roboat's local SQLite database created by `SessionDatabase`. It stores cached users, games, key-value session data, and terminal command logs. It is safe to delete — it just means you lose cached data. Add `*.robloxdb` to your `.gitignore`.

---

### Can I contribute?

Absolutely. See [CONTRIBUTING.md](../CONTRIBUTING.md) for full guidelines.

---

### An endpoint I need isn't covered. What do I do?

Open a **Feature Request** issue with the endpoint URL and a usage example. Or implement it yourself and open a PR — we review quickly.

---

### Does roboat work with group-owned games?

Yes. `get_universes_by_group`, `get_group_games`, group payout APIs, and all group management features support group-owned resources. Pass the group ID where applicable.

---

### Is roboat safe to use?

roboat only makes outbound requests to Roblox's official API endpoints. It does not execute any code from the network, does not modify local system files beyond its SQLite database, and does not have any telemetry. Audit the source — it's all here.
