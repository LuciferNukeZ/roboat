"""
tests/test_models.py
~~~~~~~~~~~~~~~~~~~~
Unit tests for all roboat models — zero network calls.
Run with: pytest tests/ -v
"""

import pytest
from roboat.models import (
    User, Game, GameVotes, GameServer, Friend,
    Group, GroupRole, Badge, CatalogItem,
    UserPresence, RobuxBalance, Page, ResaleData,
    Avatar, AvatarAsset, AvatarColors, Transaction,
)
from roboat.trades import Trade, TradeOffer, TradeAsset
from roboat.messages import Message, ChatConversation
from roboat.inventory import InventoryAsset
from roboat.develop import Universe, Place, PlaceVersion, TeamCreateMember, PluginInfo
from roboat.groups import GroupShout, GroupPayout, GroupJoinRequest, GroupRelationship
from roboat.marketplace import LimitedData, ResaleProfit, RAPTracker
from roboat.social import UserNode, PresenceSnapshot
from roboat.notifications import NotificationResult
from roboat.publish import UploadedAsset


# ── User ──────────────────────────────────────────────────────────────── #

class TestUser:
    def _sample(self, **kwargs):
        base = {"id": 156, "name": "builderman", "displayName": "Builderman",
                "description": "bio", "isBanned": False, "hasVerifiedBadge": True}
        base.update(kwargs)
        return User.from_dict(base)

    def test_basic_fields(self):
        u = self._sample()
        assert u.id == 156
        assert u.name == "builderman"
        assert u.display_name == "Builderman"
        assert u.has_verified_badge is True
        assert u.is_banned is False

    def test_defaults(self):
        u = User.from_dict({"id": 1, "name": "x", "displayName": "x"})
        assert u.description == ""
        assert u.is_banned is False
        assert u.has_verified_badge is False

    def test_str_verified(self):
        u = self._sample()
        s = str(u)
        assert "builderman" in s
        assert "✓" in s
        assert "156" in s

    def test_str_banned(self):
        u = self._sample(isBanned=True)
        assert "BANNED" in str(u)

    def test_str_no_verified(self):
        u = self._sample(hasVerifiedBadge=False)
        assert "✓" not in str(u)


# ── Game ──────────────────────────────────────────────────────────────── #

class TestGame:
    _RAW = {
        "id": 2753915549, "rootPlaceId": 6872265039,
        "name": "Adopt Me!", "description": "Pets!",
        "creator": {"name": "Uplift Games", "id": 100, "type": "Group"},
        "price": None, "playing": 50000, "visits": 30_000_000_000,
        "maxPlayers": 50, "created": "2017-07-14T00:00:00Z",
        "updated": "2024-01-01T00:00:00Z",
        "genre": "Town and City",
        "isFavoritedByUser": False, "favoritedCount": 10_000_000,
    }

    def test_fields(self):
        g = Game.from_dict(self._RAW)
        assert g.id == 2753915549
        assert g.name == "Adopt Me!"
        assert g.visits == 30_000_000_000
        assert g.playing == 50000
        assert g.creator_name == "Uplift Games"
        assert g.creator_type == "Group"
        assert g.max_players == 50
        assert g.genre == "Town and City"
        assert g.price is None

    def test_str_contains_name_and_visits(self):
        g = Game.from_dict(self._RAW)
        s = str(g)
        assert "Adopt Me!" in s
        assert "30,000,000,000" in s
        assert "Uplift Games" in s

    def test_free_game(self):
        g = Game.from_dict({**self._RAW, "price": None})
        assert g.price is None

    def test_paid_game(self):
        g = Game.from_dict({**self._RAW, "price": 100})
        assert g.price == 100


# ── GameVotes ─────────────────────────────────────────────────────────── #

class TestGameVotes:
    def test_ratio_100(self):
        v = GameVotes(universe_id=1, up_votes=100, down_votes=0)
        assert v.ratio == 100.0

    def test_ratio_50(self):
        v = GameVotes(universe_id=1, up_votes=50, down_votes=50)
        assert v.ratio == 50.0

    def test_ratio_zero_total(self):
        v = GameVotes(universe_id=1, up_votes=0, down_votes=0)
        assert v.ratio == 0.0

    def test_ratio_rounds(self):
        v = GameVotes(universe_id=1, up_votes=1, down_votes=3)
        assert v.ratio == 25.0

    def test_from_dict(self):
        v = GameVotes.from_dict({"id": 99, "upVotes": 900, "downVotes": 100})
        assert v.universe_id == 99
        assert v.up_votes == 900
        assert v.down_votes == 100

    def test_str(self):
        v = GameVotes(universe_id=1, up_votes=1000, down_votes=200)
        s = str(v)
        assert "1,000" in s
        assert "200" in s
        assert "%" in s


# ── GameServer ────────────────────────────────────────────────────────── #

class TestGameServer:
    def test_fields(self):
        s = GameServer.from_dict({
            "id": "abc-123-def", "maxPlayers": 12,
            "playing": 8, "fps": 59.9, "ping": 45,
        })
        assert s.id == "abc-123-def"
        assert s.max_players == 12
        assert s.playing == 8
        assert s.fps == 59.9
        assert s.ping == 45

    def test_str_shows_fill(self):
        s = GameServer.from_dict({
            "id": "x" * 20, "maxPlayers": 12, "playing": 8, "fps": 60, "ping": 20,
        })
        assert "8/12" in str(s)

    def test_fps_rounded(self):
        s = GameServer.from_dict({
            "id": "a", "maxPlayers": 10, "playing": 5, "fps": 59.9999, "ping": 10,
        })
        assert s.fps == 60.0


# ── Friend ────────────────────────────────────────────────────────────── #

class TestFriend:
    def test_online(self):
        f = Friend.from_dict({"id": 1, "name": "x", "displayName": "x", "isOnline": True})
        assert f.is_online is True
        assert "🟢" in str(f)

    def test_offline(self):
        f = Friend.from_dict({"id": 1, "name": "x", "displayName": "x", "isOnline": False})
        assert f.is_online is False
        assert "⚫" in str(f)

    def test_verified(self):
        f = Friend.from_dict({"id": 1, "name": "x", "displayName": "x",
                               "hasVerifiedBadge": True})
        assert "✓" in str(f)

    def test_defaults(self):
        f = Friend.from_dict({"id": 5, "name": "y", "displayName": "Y"})
        assert f.is_online is False
        assert f.has_verified_badge is False


# ── Group ─────────────────────────────────────────────────────────────── #

class TestGroup:
    _RAW = {
        "id": 7, "name": "Roblox",
        "description": "Official Roblox group",
        "owner": {"userId": 1, "username": "Roblox"},
        "memberCount": 3_000_000,
        "publicEntryAllowed": True,
        "hasVerifiedBadge": True,
    }

    def test_fields(self):
        g = Group.from_dict(self._RAW)
        assert g.id == 7
        assert g.name == "Roblox"
        assert g.member_count == 3_000_000
        assert g.owner_name == "Roblox"
        assert g.owner_id == 1
        assert g.is_public is True
        assert g.has_verified_badge is True

    def test_str_verified(self):
        g = Group.from_dict(self._RAW)
        assert "✓" in str(g)
        assert "Roblox" in str(g)
        assert "3,000,000" in str(g)

    def test_no_owner(self):
        raw = {**self._RAW, "owner": None}
        g = Group.from_dict(raw)
        assert g.owner_id is None
        assert g.owner_name is None


# ── GroupRole ─────────────────────────────────────────────────────────── #

class TestGroupRole:
    def test_fields(self):
        r = GroupRole.from_dict({"id": 1, "name": "Member", "rank": 1, "memberCount": 500})
        assert r.id == 1
        assert r.name == "Member"
        assert r.rank == 1
        assert r.member_count == 500

    def test_str(self):
        r = GroupRole.from_dict({"id": 2, "name": "Admin", "rank": 200, "memberCount": 5})
        s = str(r)
        assert "200" in s
        assert "Admin" in s


# ── Badge ─────────────────────────────────────────────────────────────── #

class TestBadge:
    def test_enabled(self):
        b = Badge.from_dict({
            "id": 1, "name": "Welcome", "description": "First visit",
            "enabled": True,
            "statistics": {"awardedCount": 10000, "winRatePercentage": 95.0},
        })
        assert b.enabled is True
        assert b.awarded_count == 10000
        assert b.win_rate_percentage == 95.0
        assert "✅" in str(b)

    def test_disabled(self):
        b = Badge.from_dict({
            "id": 2, "name": "Old", "description": "", "enabled": False,
            "statistics": {},
        })
        assert b.enabled is False
        assert "❌" in str(b)

    def test_default_stats(self):
        b = Badge.from_dict({"id": 3, "name": "x", "description": "", "enabled": True})
        assert b.awarded_count == 0
        assert b.win_rate_percentage == 0.0


# ── CatalogItem ───────────────────────────────────────────────────────── #

class TestCatalogItem:
    _RAW = {
        "id": 1028606, "itemType": "Asset", "name": "Friendly Rabbit Ears",
        "description": "cute", "creatorName": "Roblox",
        "creatorTargetId": 1, "creatorType": "User",
        "price": 80, "lowestPrice": 75,
        "purchaseCount": 50000, "favoriteCount": 12000,
        "itemStatus": [],
    }

    def test_fields(self):
        i = CatalogItem.from_dict(self._RAW)
        assert i.id == 1028606
        assert i.name == "Friendly Rabbit Ears"
        assert i.price == 80
        assert i.purchase_count == 50000
        assert i.is_off_sale is False

    def test_off_sale(self):
        i = CatalogItem.from_dict({**self._RAW, "itemStatus": ["OffSale"]})
        assert i.is_off_sale is True

    def test_free_item(self):
        i = CatalogItem.from_dict({**self._RAW, "price": None})
        assert i.price is None

    def test_str(self):
        i = CatalogItem.from_dict(self._RAW)
        s = str(i)
        assert "Friendly Rabbit Ears" in s
        assert "80" in s


# ── UserPresence ──────────────────────────────────────────────────────── #

class TestUserPresence:
    def test_offline(self):
        p = UserPresence(user_id=1, user_presence_type=0)
        assert p.status == "Offline"

    def test_online(self):
        p = UserPresence(user_id=1, user_presence_type=1)
        assert p.status == "Online"

    def test_in_game(self):
        p = UserPresence(user_id=1, user_presence_type=2)
        assert p.status == "In Game"

    def test_in_studio(self):
        p = UserPresence(user_id=1, user_presence_type=3)
        assert p.status == "In Studio"

    def test_from_dict(self):
        p = UserPresence.from_dict({
            "userId": 156, "userPresenceType": 2,
            "lastLocation": "Adopt Me!", "lastOnline": "2024-01-01"
        })
        assert p.user_id == 156
        assert p.last_location == "Adopt Me!"


# ── RobuxBalance ──────────────────────────────────────────────────────── #

class TestRobuxBalance:
    def test_str(self):
        b = RobuxBalance(robux=12345)
        s = str(b)
        assert "12,345" in s
        assert "Robux" in s

    def test_zero(self):
        b = RobuxBalance(robux=0)
        assert "0" in str(b)


# ── Page ──────────────────────────────────────────────────────────────── #

class TestPage:
    def test_iteration(self):
        p = Page(data=[1, 2, 3], next_cursor="abc")
        assert list(p) == [1, 2, 3]

    def test_len(self):
        p = Page(data=[1, 2, 3])
        assert len(p) == 3

    def test_cursors(self):
        p = Page(data=[], next_cursor="next", previous_cursor="prev")
        assert p.next_cursor == "next"
        assert p.previous_cursor == "prev"

    def test_from_dict_with_model(self):
        raw = {
            "data": [
                {"id": 1, "name": "A", "displayName": "A"},
                {"id": 2, "name": "B", "displayName": "B"},
            ],
            "nextPageCursor": "xyz",
            "previousPageCursor": None,
        }
        p = Page.from_dict(raw, User)
        assert len(p) == 2
        assert isinstance(p.data[0], User)
        assert p.next_cursor == "xyz"

    def test_from_dict_no_model(self):
        raw = {"data": [{"foo": "bar"}], "nextPageCursor": None}
        p = Page.from_dict(raw)
        assert p.data == [{"foo": "bar"}]

    def test_empty_page(self):
        p = Page(data=[])
        assert len(p) == 0
        assert list(p) == []


# ── Trades ────────────────────────────────────────────────────────────── #

class TestTradeAsset:
    def test_fields(self):
        a = TradeAsset.from_dict({
            "userAssetId": 1, "serialNumber": 42, "assetId": 1365767,
            "name": "Valkyrie Helm", "recentAveragePrice": 15000,
            "originalPrice": 1000, "assetStock": None,
        })
        assert a.asset_id == 1365767
        assert a.name == "Valkyrie Helm"
        assert a.recent_average_price == 15000
        assert a.serial_number == 42

    def test_str(self):
        a = TradeAsset(1, None, 100, "Item", 5000, None, None)
        assert "Item" in str(a)
        assert "5,000" in str(a)


class TestTradeOffer:
    def test_total_rap(self):
        offer = TradeOffer(user_id=1, user_name="x", robux=0, assets=[
            TradeAsset(1, None, 100, "A", 5000, None, None),
            TradeAsset(2, None, 101, "B", 3000, None, None),
            TradeAsset(3, None, 102, "C", 2000, None, None),
        ])
        assert offer.total_rap == 10000

    def test_empty_assets(self):
        offer = TradeOffer(user_id=1, user_name="x", robux=0, assets=[])
        assert offer.total_rap == 0


class TestTrade:
    def test_status_emojis(self):
        statuses = [
            ("Open",      "🟡"),
            ("Completed", "✅"),
            ("Declined",  "❌"),
            ("Expired",   "⏰"),
        ]
        for status, emoji in statuses:
            t = Trade(id=1, user_id=2, user_name="x", status=status, created="2024-01-01")
            assert emoji in str(t)

    def test_from_dict(self):
        t = Trade.from_dict({
            "id": 999, "user": {"id": 1, "name": "bob"},
            "status": "Open", "created": "2024-01-01",
        })
        assert t.id == 999
        assert t.user_name == "bob"


# ── InventoryAsset ────────────────────────────────────────────────────── #

class TestInventoryAsset:
    _RAW = {
        "userAssetId": 1, "assetId": 1365767, "name": "Dominus Aureus",
        "assetTypeId": 8, "created": "2012-01-01", "updated": "2012-01-01",
        "serialNumber": 5, "isTradable": True,
        "isRecentAveragePriceValid": True, "recentAveragePrice": 100000,
    }

    def test_fields(self):
        a = InventoryAsset.from_dict(self._RAW)
        assert a.asset_id == 1365767
        assert a.serial_number == 5
        assert a.is_tradable is True
        assert a.recent_average_price == 100000

    def test_str_serial(self):
        a = InventoryAsset.from_dict(self._RAW)
        assert "#5" in str(a)

    def test_str_tradable(self):
        a = InventoryAsset.from_dict(self._RAW)
        assert "Tradable" in str(a)

    def test_not_tradable(self):
        a = InventoryAsset.from_dict({**self._RAW, "isTradable": False})
        assert a.is_tradable is False


# ── Develop models ────────────────────────────────────────────────────── #

class TestUniverse:
    _RAW = {
        "id": 2753915549, "name": "Adopt Me!", "description": "Pets",
        "created": "2017-07-14", "updated": "2024-01-01",
        "rootPlaceId": 6872265039,
        "isArchived": False, "isActive": True,
        "privacyType": "Public",
        "creator": {"type": "Group", "id": 100, "name": "Uplift Games"},
    }

    def test_fields(self):
        u = Universe.from_dict(self._RAW)
        assert u.id == 2753915549
        assert u.name == "Adopt Me!"
        assert u.is_active is True
        assert u.creator_name == "Uplift Games"

    def test_archived(self):
        u = Universe.from_dict({**self._RAW, "isArchived": True})
        assert u.is_archived is True
        assert "Archived" in str(u)


class TestPluginInfo:
    def test_fields(self):
        p = PluginInfo.from_dict({
            "id": 12345, "name": "My Plugin",
            "description": "A plugin", "commentsEnabled": True, "versionId": 3,
        })
        assert p.id == 12345
        assert p.comments_enabled is True


# ── Marketplace models ────────────────────────────────────────────────── #

class TestLimitedData:
    def test_price_trend_rising(self):
        data = LimitedData(
            asset_id=1, name="x", asset_stock=None, sales=100,
            number_remaining=50, recent_average_price=10000,
            original_price=1000, lowest_resale_price=9500,
            price_data_points=[
                {"value": 9000}, {"value": 9200}, {"value": 9400},
                {"value": 9700}, {"value": 10100},
            ],
        )
        assert data.price_trend == "rising"

    def test_price_trend_falling(self):
        data = LimitedData(
            asset_id=1, name="x", asset_stock=None, sales=100,
            number_remaining=50, recent_average_price=10000,
            original_price=1000, lowest_resale_price=8000,
            price_data_points=[
                {"value": 10000}, {"value": 9800}, {"value": 9400},
                {"value": 9000}, {"value": 8500},
            ],
        )
        assert data.price_trend == "falling"

    def test_price_trend_stable(self):
        data = LimitedData(
            asset_id=1, name="x", asset_stock=None, sales=100,
            number_remaining=50, recent_average_price=10000,
            original_price=1000, lowest_resale_price=10000,
            price_data_points=[
                {"value": 10000}, {"value": 10010}, {"value": 9990},
                {"value": 10005}, {"value": 10000},
            ],
        )
        assert data.price_trend == "stable"

    def test_price_trend_unknown(self):
        data = LimitedData(
            asset_id=1, name="x", asset_stock=None, sales=0,
            number_remaining=None, recent_average_price=0,
            original_price=None, lowest_resale_price=None,
        )
        assert data.price_trend == "unknown"


class TestResaleProfit:
    def test_profit(self):
        p = ResaleProfit(
            asset_id=1, purchase_price=10000, rap=15000,
            lowest_resale=15000, roblox_fee=4500,
            estimated_profit=500, roi_percent=5.0,
        )
        assert p.estimated_profit == 500
        assert p.roi_percent == 5.0
        assert "500" in str(p)

    def test_loss(self):
        p = ResaleProfit(
            asset_id=1, purchase_price=20000, rap=15000,
            lowest_resale=15000, roblox_fee=4500,
            estimated_profit=-9500, roi_percent=-47.5,
        )
        assert p.estimated_profit < 0
        assert "-9,500" in str(p)


# ── Social models ─────────────────────────────────────────────────────── #

class TestPresenceSnapshot:
    def test_total_online(self):
        snap = PresenceSnapshot(
            timestamp=0.0,
            online=[1, 2],
            in_game=[3, 4, 5],
            in_studio=[6],
            offline=[7, 8],
        )
        assert snap.total_online == 6

    def test_str(self):
        snap = PresenceSnapshot(
            timestamp=0.0,
            online=[1], in_game=[2, 3], in_studio=[], offline=[4],
        )
        s = str(snap)
        assert "Online" in s
        assert "In Game" in s


# ── Notifications / Publish ───────────────────────────────────────────── #

class TestNotificationResult:
    def test_success(self):
        r = NotificationResult(user_id=1, success=True)
        assert "✅" in str(r)

    def test_failure(self):
        r = NotificationResult(user_id=1, success=False, error="Quota exceeded")
        assert "❌" in str(r)
        assert "Quota exceeded" in str(r)


# ── Groups extended models ────────────────────────────────────────────── #

class TestGroupShout:
    def test_fields(self):
        s = GroupShout.from_dict({
            "body": "Welcome everyone!",
            "poster": {"userId": 1, "username": "admin"},
            "created": "2024-01-01",
        })
        assert s.body == "Welcome everyone!"
        assert s.poster_name == "admin"
        assert "📣" in str(s)


class TestGroupPayout:
    def test_str(self):
        p = GroupPayout.from_dict({
            "user": {"userId": 1, "username": "dev"},
            "recipientType": "User", "amount": 1000, "percentage": 50,
        })
        assert "dev" in str(p)
        assert "1,000" in str(p)
        assert "50%" in str(p)


class TestGroupJoinRequest:
    def test_fields(self):
        r = GroupJoinRequest.from_dict({
            "requester": {
                "userId": 1234, "username": "newuser",
                "displayName": "New User",
            },
            "created": "2024-01-01",
        })
        assert r.requester_id == 1234
        assert r.requester_name == "newuser"
        assert "newuser" in str(r)


# ── Message ───────────────────────────────────────────────────────────── #

class TestMessage:
    def test_fields(self):
        m = Message.from_dict({
            "id": 1,
            "sender": {"id": 156, "name": "builderman"},
            "recipient": {"id": 261, "name": "other"},
            "subject": "Hello",
            "body": "Hey there",
            "created": "2024-01-01",
            "updated": "2024-01-01",
            "isRead": False,
            "isSystemMessage": False,
        })
        assert m.sender_name == "builderman"
        assert m.subject == "Hello"
        assert m.is_read is False
        assert "📬" in str(m)

    def test_read_message(self):
        m = Message.from_dict({
            "id": 2, "sender": {"id": 1, "name": "x"},
            "recipient": {"id": 2, "name": "y"},
            "subject": "s", "body": "b",
            "created": "2024-01-01", "updated": "2024-01-01",
            "isRead": True, "isSystemMessage": False,
        })
        assert "📭" in str(m)


# ── ResaleData ────────────────────────────────────────────────────────── #

class TestResaleData:
    def test_fields(self):
        r = ResaleData.from_dict(1365767, {
            "assetStock": 1000, "sales": 5000, "numberRemaining": 800,
            "recentAveragePrice": 15000, "originalPrice": 1000,
        })
        assert r.asset_id == 1365767
        assert r.recent_average_price == 15000
        assert r.number_remaining == 800


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
