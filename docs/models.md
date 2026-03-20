# Model Reference

All typed dataclasses returned by roboat APIs.
Every model has a `from_dict(cls, d)` classmethod and a `__str__` method.

---

## User

```python
from roboat.models import User

user.id                  # int
user.name                # str — username (@handle)
user.display_name        # str — display name
user.description         # str — profile bio
user.created             # str — ISO 8601 creation date
user.is_banned           # bool
user.has_verified_badge  # bool
```

**Display:** `Builderman (@builderman) ✓ [ID: 156]`

---

## Game

```python
from roboat.models import Game

game.id              # int — universe ID
game.root_place_id   # int — main place ID
game.name            # str
game.description     # str
game.creator_name    # str
game.creator_id      # int
game.creator_type    # str — "User" or "Group"
game.price           # Optional[int] — None if free
game.playing         # int — current player count
game.visits          # int
game.max_players     # int
game.created         # str — ISO 8601
game.updated         # str — ISO 8601
game.genre           # str
game.is_favorited    # bool — by authenticated user
game.favorited_count # int
```

---

## GameVotes

```python
from roboat.models import GameVotes

v.universe_id  # int
v.up_votes     # int
v.down_votes   # int
v.ratio        # float — computed: upVotes / total * 100
```

**Display:** `👍 12,345  👎 678  (94.8% positive)`

---

## GameServer

```python
from roboat.models import GameServer

s.id          # str — server UUID
s.max_players # int
s.playing     # int — current players
s.fps         # float
s.ping        # int — milliseconds
```

**Display:** `[abc123...] Players: 8/12  FPS: 60.0  Ping: 45ms`

---

## Friend

```python
from roboat.models import Friend

f.id                  # int
f.name                # str
f.display_name        # str
f.is_online           # bool
f.has_verified_badge  # bool
```

**Display:** `🟢 Builderman (@builderman) ✓ [ID: 156]`

---

## Group

```python
from roboat.models import Group

g.id                  # int
g.name                # str
g.description         # str
g.owner_id            # Optional[int]
g.owner_name          # Optional[str]
g.member_count        # int
g.is_public           # bool
g.has_verified_badge  # bool
```

---

## GroupRole

```python
from roboat.models import GroupRole

r.id           # int
r.name         # str
r.rank         # int — 0 to 255
r.member_count # int
```

**Display:** `[Rank 255] Owner                          (1 members)`

---

## CatalogItem

```python
from roboat.models import CatalogItem

item.id              # int
item.item_type       # str — "Asset" or "Bundle"
item.name            # str
item.description     # str
item.creator_name    # str
item.creator_id      # int
item.creator_type    # str
item.price           # Optional[int]
item.lowest_price    # Optional[int]
item.purchase_count  # int
item.favorite_count  # int
item.asset_type      # Optional[str]
item.bundle_type     # Optional[str]
item.is_off_sale     # bool
```

---

## ResaleData

```python
from roboat.models import ResaleData

r.asset_id               # int
r.asset_stock            # Optional[int]
r.sales                  # int
r.number_remaining       # Optional[int]
r.recent_average_price   # int — RAP
r.original_price         # Optional[int]
```

---

## Badge

```python
from roboat.models import Badge

b.id                    # int
b.name                  # str
b.description           # str
b.enabled               # bool
b.awarded_count         # int
b.win_rate_percentage   # float
```

**Display:** `✅ Welcome [ID: 12345]  Awarded: 10,000  Win Rate: 95.00%`

---

## Avatar

```python
from roboat.models import Avatar, AvatarAsset, AvatarColors

av.user_id      # int
av.avatar_type  # str — "R6" or "R15"
av.scales       # dict — height, width, head, depth, proportion, bodyType
av.assets       # List[AvatarAsset]
av.colors       # Optional[AvatarColors]
```

### AvatarAsset

```python
asset.id               # int
asset.name             # str
asset.asset_type_id    # int
asset.asset_type_name  # str
```

### AvatarColors

```python
colors.head       # str — color ID
colors.torso      # str
colors.right_arm  # str
colors.left_arm   # str
colors.right_leg  # str
colors.left_leg   # str
```

---

## UserPresence

```python
from roboat.models import UserPresence

p.user_id              # int
p.last_online          # Optional[str]
p.last_location        # Optional[str] — game name
p.game_id              # Optional[int]
p.universe_id          # Optional[int]
p.user_presence_type   # int — 0=Offline 1=Online 2=InGame 3=InStudio
p.status               # str — computed friendly label
```

---

## RobuxBalance

```python
from roboat.models import RobuxBalance

b.robux  # int
```

**Display:** `💎 12,345 Robux`

---

## Page

```python
from roboat.models import Page

page.data             # list — typed model objects
page.next_cursor      # Optional[str]
page.previous_cursor  # Optional[str]

len(page)             # int
for item in page: ... # iterable

Page.from_dict(d, Model)  # construct from raw dict + model class
```

---

## Trade / TradeOffer / TradeAsset

```python
from roboat.trades import Trade, TradeOffer, TradeAsset

# Trade
t.id         # int
t.user_id    # int
t.user_name  # str
t.status     # str — Open/Completed/Declined/Expired/Countered
t.created    # str
t.expiration # Optional[str]
t.offers     # List[TradeOffer]

# TradeOffer
o.user_id    # int
o.user_name  # str
o.robux      # int
o.assets     # List[TradeAsset]
o.total_rap  # int — computed sum of asset RAPs

# TradeAsset
a.user_asset_id          # int
a.serial_number          # Optional[int]
a.asset_id               # int
a.name                   # str
a.recent_average_price   # int
a.original_price         # Optional[int]
a.asset_stock            # Optional[int]
```

---

## Message / ChatConversation

```python
from roboat.messages import Message, ChatConversation

# Message
m.id                # int
m.sender_id         # int
m.sender_name       # str
m.recipient_id      # int
m.recipient_name    # str
m.subject           # str
m.body              # str
m.created           # str
m.updated           # str
m.is_read           # bool
m.is_system_message # bool

# ChatConversation
c.id                # int
c.title             # str
c.conversation_type # str
c.participants      # List[dict]
c.last_updated      # Optional[str]
c.unread_count      # int
```

---

## InventoryAsset

```python
from roboat.inventory import InventoryAsset

a.user_asset_id                 # int
a.asset_id                      # int
a.name                          # str
a.asset_type_id                 # int
a.created                       # str
a.updated                       # str
a.serial_number                 # Optional[int]
a.is_tradable                   # bool
a.is_recent_average_price_valid # bool
a.recent_average_price          # int
```

---

## Universe / Place / DataStore

```python
from roboat.develop import Universe, Place, DataStore, PlaceVersion, TeamCreateMember, PluginInfo

# Universe
u.id            # int
u.name          # str
u.description   # str
u.created       # str
u.updated       # str
u.root_place_id # int
u.is_archived   # bool
u.is_active     # bool
u.privacy_type  # str
u.creator_type  # str
u.creator_id    # int
u.creator_name  # str

# Place
p.id            # int
p.universe_id   # int
p.name          # str
p.description   # str
p.max_players   # int
p.server_fill   # str
p.is_root_place # bool

# DataStore
d.name    # str
d.created # str

# PlaceVersion
v.version_number # int
v.version_type   # str
v.created        # str
v.creator_id     # int
v.creator_type   # str

# TeamCreateMember
m.user_id      # int
m.username     # str
m.display_name # str

# PluginInfo
p.id               # int
p.name             # str
p.description      # str
p.comments_enabled # bool
p.version_id       # int
```

---

## Group Extended Models

```python
from roboat.groups import GroupShout, GroupPayout, GroupJoinRequest, GroupRelationship

# GroupShout
s.body        # str
s.poster_id   # int
s.poster_name # str
s.created     # str

# GroupPayout
p.recipient_id   # int
p.recipient_name # str
p.recipient_type # str
p.amount         # int
p.percentage     # int

# GroupJoinRequest
r.requester_id           # int
r.requester_name         # str
r.requester_display_name # str
r.created                # str

# GroupRelationship
r.group_id         # int
r.group_name       # str
r.relationship_type # str
r.member_count     # int
```

---

## Marketplace Models

```python
from roboat.marketplace import LimitedData, ResaleProfit

# LimitedData
d.asset_id               # int
d.name                   # str
d.asset_stock            # Optional[int]
d.sales                  # int
d.number_remaining       # Optional[int]
d.recent_average_price   # int — RAP
d.original_price         # Optional[int]
d.lowest_resale_price    # Optional[int]
d.price_data_points      # List[dict]
d.volume_data_points     # List[dict]
d.price_trend            # str — "rising" / "falling" / "stable" / "unknown" (computed)

# ResaleProfit
p.asset_id         # int
p.purchase_price   # int
p.rap              # int
p.lowest_resale    # Optional[int]
p.roblox_fee       # int — 30% of sale price
p.estimated_profit # int
p.roi_percent      # float
```

---

## Social Models

```python
from roboat.social import UserNode, PresenceSnapshot

# UserNode
n.user_id        # int
n.username       # str
n.friend_count   # int
n.follower_count # int

# PresenceSnapshot
s.timestamp    # float — unix timestamp
s.online       # List[int] — user IDs online (website)
s.in_game      # List[int] — user IDs in a game
s.in_studio    # List[int] — user IDs in Roblox Studio
s.offline      # List[int]
s.total_online # int — computed: online + in_game + in_studio
```

---

## Notification / Upload Models

```python
from roboat.notifications import NotificationResult
from roboat.publish import UploadedAsset
from roboat.moderation import AccountStanding, AbuseReport

# NotificationResult
r.user_id # int
r.success # bool
r.error   # Optional[str]

# UploadedAsset
a.operation_id # str
a.asset_id     # Optional[int]
a.name         # str
a.asset_type   # str
a.status       # str — "Pending" or "Complete"

# AccountStanding
s.user_id             # int
s.can_view_restricted # bool
s.account_age_days    # int
s.has_verified_email  # bool
s.is_over_13          # bool

# AbuseReport
r.report_id # Optional[str]
r.success   # bool
r.message   # str
```
