<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2563EB,100:1E3A8A&height=220&section=header&text=robase&fontSize=90&fontColor=ffffff&animation=fadeIn&fontAlignY=40&desc=The%20Most%20Powerful%20Python%20SDK%20for%20the%20Roblox%20API&descAlignY=62&descAlign=50&descColor=ffffff" width="100%"/>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&pause=800&color=2563EB&center=true&vCenter=true&width=700&lines=robase+%E2%80%94+Built+for+Roblox+Developers;OAuth+2.0+%E2%80%94+No+Cookie+Required;Typed+Models+for+Every+API+Response;Async+%2B+Sync+Clients+Built+In;SQLite+Database+Layer+Included;Open+Cloud+%2B+DataStore+Support;Real-time+Event+System;Marketplace+%26+RAP+Tracking+Tools;Interactive+Terminal+REPL;Production+Ready+%F0%9F%9A%80" alt="Typing SVG" />

<br/><br/>

[![Python](https://img.shields.io/badge/Python-3.8%2B-2563EB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-1E3A8A?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1.0-2563EB?style=for-the-badge)](https://github.com/Addi9000/robase)
[![Website](https://img.shields.io/badge/Website-robase.pro-1E3A8A?style=for-the-badge&logo=google-chrome&logoColor=white)](https://robase.pro)
[![Stars](https://img.shields.io/github/stars/Addi9000/robase?style=for-the-badge&color=2563EB&logo=github)](https://github.com/Addi9000/robase/stargazers)

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=14&pause=2000&color=60A5FA&center=true&vCenter=true&width=700&lines=pip+install+robase-utilities" alt="Install SVG" />

</div>

---

<div align="center">

## ⚡ Install

</div>

```bash
pip install robase-utilities
pip install "robase-utilities[async]"   # async support via aiohttp
pip install "robase-utilities[all]"     # everything + test tools
```

---

<div align="center">

## 🚀 Quick Start

</div>

```python
from robase import RobaseClient

client = RobaseClient()

# User lookup
user = client.users.get_user(156)
print(user)
# Builderman (@builderman) ✓ [ID: 156]

# Game stats
game = client.games.get_game(2753915549)
print(f"{game.name} — {game.visits:,} visits  |  {game.playing:,} playing")

# Catalog search
items = client.catalog.search(keyword="fedora", category="Accessories", sort_type="Sales")
for item in items:
    print(f"{item.name} — {item.price}R$")
```

---

<div align="center">

## 🖥️ Interactive Terminal

</div>

```bash
robase
# or: python -m robase
```

```
  ____       _                    
 |  _ \ ___ | |__   __ _ ___  ___ 
 | |_) / _ \| '_ \ / _` / __|/ _ \
 |  _ < (_) | |_) | (_| \__ \  __/
 |_| \_\___/|_.__/ \__,_|___/\___|

  robase v2.1.0  —  robase.pro  —  type 'help' to begin

» start 156
» auth
» game 2753915549
» inventory 156
» rap 156
» likes 2753915549
» friends 156
```

---

<div align="center">

## 🔐 OAuth Authentication

</div>

robase uses **Roblox OAuth 2.0** — no cookie extraction, no browser DevTools.

```python
from robase import OAuthManager, RobaseClient

manager = OAuthManager(
    on_success=lambda token: print("✅ Authenticated!"),
    on_failure=lambda err:   print(f"❌ Failed: {err}"),
    timeout=120,
)

token = manager.authenticate()   # opens browser, 120s countdown

if token:
    client = RobaseClient(oauth_token=token)
    print(f"Logged in as {client.username()}")
```

In the terminal, type `auth`. A browser window opens, you log in, and you're done. A **live 120-second countdown** is shown while waiting.

---

<div align="center">

## 📦 Repository Structure

</div>

```
robase/
├── robase/              Source package (35 modules)
│   ├── utils/           Cache, rate limiter, paginator
│   └── *.py             All API modules
├── examples/            8 ready-to-run example scripts
├── tests/               Unit tests — no network required
├── benchmarks/          Performance benchmarks
├── docs/                Architecture, endpoints, models, FAQ
├── tools/               CLI utilities (bulk lookup, RAP snapshot, game monitor)
├── integrations/        Discord bot, Flask REST API
├── typestubs/           .pyi type stubs for IDE autocomplete
├── scripts/             Dev scripts (env check, stub generator)
└── .github/             CI/CD workflows, issue templates
```

---

<div align="center">

## 🧠 Clients

</div>

### Sync — `RobaseClient`

```python
from robase import RobaseClient, ClientBuilder

# Simple
client = RobaseClient()

# Builder — full control
client = (
    ClientBuilder()
    .set_oauth_token("TOKEN")
    .set_timeout(15)
    .set_cache_ttl(60)       # cache responses for 60 seconds
    .set_rate_limit(10)      # max 10 requests/second
    .set_proxy("http://proxy:8080")
    .build()
)
```

### Async — `AsyncRobaseClient`

```python
import asyncio
from robase import AsyncRobaseClient

async def main():
    async with AsyncRobaseClient() as client:

        # Parallel fetch — all at once
        game, votes, icons = await asyncio.gather(
            client.games.get_game(2753915549),
            client.games.get_votes([2753915549]),
            client.thumbnails.get_game_icons([2753915549]),
        )

        # Bulk fetch 500 users — auto-chunked into batches of 100
        users = await client.users.get_users_by_ids(list(range(1, 501)))
        print(f"Fetched {len(users)} users")

asyncio.run(main())
```

### Open Cloud — `RobaseCloudClient`

```python
from robase import RobaseCloudClient

cloud = RobaseCloudClient(api_key="roblox-KEY-xxxxx")
cloud.datastores.set(universe_id, "PlayerData", "player_1", {"coins": 500})
```

---

<div align="center">

## 📡 API Coverage

</div>

<div align="center">

| API | Endpoint | Methods |
|:---|:---|:---:|
| Users | `users.roblox.com` | 7 |
| Games | `games.roblox.com` | 15 |
| Catalog | `catalog.roblox.com` | 8 |
| Groups | `groups.roblox.com` | 22 |
| Friends | `friends.roblox.com` | 11 |
| Thumbnails | `thumbnails.roblox.com` | 7 |
| Badges | `badges.roblox.com` | 4 |
| Economy | `economy.roblox.com` | 5 |
| Presence | `presence.roblox.com` | 3 |
| Avatar | `avatar.roblox.com` | 5 |
| Trades | `trades.roblox.com` | 7 |
| Messages | `privatemessages.roblox.com` | 7 |
| Inventory | `inventory.roblox.com` | 8 |
| Develop | `develop.roblox.com` | 14 |
| DataStores | `apis.roblox.com/datastores` | 7 |
| Ordered DS | `apis.roblox.com/ordered-data-stores` | 5 |
| Messaging | `apis.roblox.com/messaging-service` | 3 |
| Bans | `apis.roblox.com/cloud/v2` | 4 |
| Notifications | `apis.roblox.com/cloud/v2` | 3 |
| Asset Upload | `apis.roblox.com/assets` | 5 |

</div>

---

<div align="center">

## 👤 Users

</div>

```python
user  = client.users.get_user(156)
users = client.users.get_users_by_ids([1, 156, 261])          # up to 100 at once
users = client.users.get_users_by_usernames(["Roblox", "builderman"])
page  = client.users.search_users("builderman", limit=10)
page  = client.users.get_username_history(156)
ok    = client.users.validate_username("mycoolname")
```

---

<div align="center">

## 🎮 Games

</div>

```python
game    = client.games.get_game(2753915549)
game    = client.games.get_game_from_place(6872265039)
visits  = client.games.get_visits([2753915549, 286090429])    # {id: count}
votes   = client.games.get_votes([2753915549])
servers = client.games.get_servers(6872265039, limit=10)
page    = client.games.search_games("obby", limit=20)
page    = client.games.get_user_games(156)
page    = client.games.get_group_games(2868472)
count   = client.games.get_favorite_count(2753915549)
```

---

<div align="center">

## 👥 Groups

</div>

```python
group   = client.groups.get_group(7)
roles   = client.groups.get_roles(7)
role    = client.groups.get_role_by_name(7, "Member")
members = client.groups.get_members(7, limit=100)
is_in   = client.groups.is_member(7, user_id=156)

# Management (auth required)
client.groups.set_member_role(7, user_id=1234, role_id=role.id)
client.groups.kick_member(7, user_id=1234)
client.groups.post_shout(7, "Welcome everyone!")
client.groups.accept_all_join_requests(7)   # accepts ALL pending
client.groups.pay_out(7, user_id=1234, amount=500)
```

---

<div align="center">

## 💰 Marketplace & Economy

</div>

```python
from robase.marketplace import MarketplaceAPI

market = MarketplaceAPI(client)

# Full limited data — RAP, trend, remaining supply
data   = market.get_limited_data(1365767)
print(f"{data.name}  RAP: {data.recent_average_price:,}R$  Trend: {data.price_trend}")

# Profit estimator — includes Roblox 30% fee
profit = market.estimate_resale_profit(1365767, purchase_price=12000)
print(f"Net profit: {profit.estimated_profit:,}R$  ROI: {profit.roi_percent}%")

# Find underpriced limiteds (below 85% of RAP)
deals = market.find_underpriced_limiteds([1365767, 1028606, 19027209])

# RAP tracker — snapshot and diff over time
tracker = market.create_rap_tracker([1365767, 1028606])
tracker.snapshot()
# ... wait some time ...
tracker.snapshot()
print(tracker.summary())
```

---

<div align="center">

## 🤝 Social Graph

</div>

```python
from robase.social import SocialGraph

sg = SocialGraph(client)

mutuals      = sg.mutual_friends(156, 261)
is_following = sg.does_follow(follower_id=156, target_id=261)
snap         = sg.presence_snapshot([156, 261, 1234])
online_ids   = sg.who_is_online([156, 261, 1234])
nodes        = sg.most_followed_in_group([156, 261, 1234])   # parallel fetch
suggestions  = sg.follow_suggestions(156, limit=10)
```

---

<div align="center">

## 🔧 Open Cloud — Developer Tools

</div>

```python
API_KEY  = "roblox-KEY-xxxxx"
UNIVERSE = 123456789

# DataStores
client.develop.set_datastore_entry(UNIVERSE, "PlayerData", "player_1", {"coins": 500}, API_KEY)
client.develop.get_datastore_entry(UNIVERSE, "PlayerData", "player_1", API_KEY)
client.develop.increment_datastore_entry(UNIVERSE, "Stats", "deaths", 1, API_KEY)
client.develop.list_datastore_keys(UNIVERSE, "PlayerData", API_KEY)

# Ordered DataStores (leaderboards)
client.develop.list_ordered_datastore(UNIVERSE, "Leaderboard", API_KEY, max_page_size=10)
client.develop.set_ordered_datastore_entry(UNIVERSE, "Leaderboard", "player_1", 9500, API_KEY)

# MessagingService — reaches all live servers instantly
client.develop.announce(UNIVERSE, API_KEY, "Double XP starts now!")
client.develop.broadcast_shutdown(UNIVERSE, API_KEY)

# Bans
client.develop.ban_user(UNIVERSE, 1234, API_KEY, duration_seconds=86400,
                         display_reason="Temporarily banned.")
client.develop.unban_user(UNIVERSE, 1234, API_KEY)
```

---

<div align="center">

## 🗄️ Database Layer

</div>

```python
from robase import SessionDatabase

db = SessionDatabase.load_or_create("myproject")

db.save_user(client.users.get_user(156))
db.save_game(client.games.get_game(2753915549))

db.set("tracked_ids", [156, 261, 1234])
val = db.get("tracked_ids")

print(db.stats())
# {'users': 10, 'games': 5, 'session_keys': 3, 'log_entries': 42}
db.close()
```

---

<div align="center">

## ⚡ Events

</div>

```python
from robase import EventPoller

poller = EventPoller(client, interval=30)

@poller.on_friend_online
def on_online(user):
    print(f"🟢 {user.display_name} came online!")

@poller.on_new_friend
def on_friend(user):
    print(f"🤝 New friend: {user.display_name}")

poller.track_game(2753915549, milestone_step=1_000_000)

@poller.on("visit_milestone")
def on_milestone(game, count):
    print(f"🎉 {game.name} hit {count:,} visits!")

poller.start(interval=30)   # background thread
```

---

<div align="center">

## 🛠️ CLI Tools

</div>

```bash
# Bulk user lookup → CSV or JSON
python tools/bulk_lookup.py --ids 1 156 261 --format csv
python tools/bulk_lookup.py --usernames Roblox builderman --format json

# RAP snapshot and diff
python tools/rap_snapshot.py --user 156
python tools/rap_snapshot.py --user 156 --diff    # compare to last run

# Live game monitor with milestone alerts
python tools/game_monitor.py --universe 2753915549 --interval 60

# Environment health check
python scripts/check_env.py

# Generate .pyi type stubs
python scripts/generate_stub.py
```

---

<div align="center">

## 🔗 Integrations

</div>

| Integration | File | Description |
|:---|:---|:---|
| Discord Bot | `integrations/discord_bot.py` | Slash commands: `/user`, `/game`, `/status` |
| Flask REST API | `integrations/flask_api.py` | REST endpoints for all major resources |

---

<div align="center">

## 🚨 Error Handling

</div>

```python
from robase import (
    UserNotFoundError, GameNotFoundError,
    RateLimitedError, NotAuthenticatedError, RobaseAPIError,
)
from robase.utils import retry

@retry(max_attempts=3, backoff=2.0)
def safe_get(user_id):
    return client.users.get_user(user_id)

try:
    user = safe_get(99999999999)
except UserNotFoundError:
    print("User not found")
except RateLimitedError:
    print("Rate limited")
except NotAuthenticatedError:
    print("Need OAuth token")
except RobaseAPIError as e:
    print(f"API error: {e}")
```

---

<div align="center">

## 📊 Pagination

</div>

```python
from robase.utils import Paginator

# Lazily iterate ALL followers — auto-fetches every page
for follower in Paginator(
    lambda cursor: client.friends.get_followers(156, limit=100, cursor=cursor)
):
    print(follower)

# Collect first 500
top_500 = Paginator(
    lambda c: client.friends.get_followers(156, limit=100, cursor=c),
    max_items=500,
).collect()
```

---

<div align="center">

## 📋 Terminal Commands

</div>

<div align="center">

| Command | Description |
|:---|:---|
| `start <userid>` | Begin session (required first) |
| `auth` | OAuth login — browser opens, 120s |
| `whoami` | Current session info |
| `newdb / loaddb / listdb` | Database management |
| `user <id>` | User profile |
| `game <id>` | Game stats + votes |
| `friends / followers <id>` | Social counts |
| `likes <id>` | Vote breakdown |
| `search user/game <kw>` | Search |
| `presence / avatar <id>` | Status + avatar |
| `servers <placeid>` | Active servers |
| `badges <id>` | Game badges |
| `catalog <keyword>` | Shop search |
| `trades` | Trade list |
| `inventory / rap <id>` | Limiteds + RAP |
| `messages` | Private messages |
| `owns <uid> <assetid>` | Ownership check |
| `universe <id>` | Developer universe info |
| `save user/game <id>` | Save to DB |
| `cache [clear]` | Cache stats |
| `watch <id>` | Visit milestone alerts |
| `history / clear / exit` | Utility |

</div>

---

<div align="center">

## ⚖️ License

</div>

```
MIT License

Copyright (c) 2024 robase contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

Full license: [LICENSE](LICENSE)

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1E3A8A,100:2563EB&height=140&section=footer" width="100%"/>

**[robase.pro](https://robase.pro)** &nbsp;·&nbsp; **[GitHub](https://github.com/Addi9000/robase)** &nbsp;·&nbsp; **[Issues](https://github.com/Addi9000/robase/issues)**

*Built with ❤️ for the Roblox developer community*

</div>
