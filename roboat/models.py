"""
roboat.models
~~~~~~~~~~~~~~~~
Typed dataclasses for every API response object.
Inspired by roboat's strong typing philosophy.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


# ─────────────────────────────────────────────
#  Users
# ─────────────────────────────────────────────

@dataclass
class User:
    id: int
    name: str
    display_name: str
    description: str = ""
    created: Optional[str] = None
    is_banned: bool = False
    has_verified_badge: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "User":
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            display_name=d.get("displayName", ""),
            description=d.get("description", ""),
            created=d.get("created"),
            is_banned=d.get("isBanned", False),
            has_verified_badge=d.get("hasVerifiedBadge", False),
        )

    def __str__(self) -> str:
        verified = " ✓" if self.has_verified_badge else ""
        banned = " [BANNED]" if self.is_banned else ""
        return f"{self.display_name} (@{self.name}){verified}{banned} [ID: {self.id}]"


@dataclass
class UserPresence:
    user_id: int
    last_online: Optional[str] = None
    last_location: Optional[str] = None
    game_id: Optional[int] = None
    universe_id: Optional[int] = None
    user_presence_type: int = 0  # 0=Offline, 1=Online, 2=InGame, 3=InStudio

    PRESENCE_LABELS = {0: "Offline", 1: "Online", 2: "In Game", 3: "In Studio"}

    @classmethod
    def from_dict(cls, d: dict) -> "UserPresence":
        return cls(
            user_id=d.get("userId", 0),
            last_online=d.get("lastOnline"),
            last_location=d.get("lastLocation"),
            game_id=d.get("gameId"),
            universe_id=d.get("universeId"),
            user_presence_type=d.get("userPresenceType", 0),
        )

    @property
    def status(self) -> str:
        return self.PRESENCE_LABELS.get(self.user_presence_type, "Unknown")


# ─────────────────────────────────────────────
#  Games
# ─────────────────────────────────────────────

@dataclass
class Game:
    id: int                 # universe ID
    root_place_id: int
    name: str
    description: str
    creator_name: str
    creator_id: int
    creator_type: str       # "User" or "Group"
    price: Optional[int]
    playing: int
    visits: int
    max_players: int
    created: Optional[str]
    updated: Optional[str]
    genre: str
    is_favorited: bool
    favorited_count: int
    up_votes: int = 0
    down_votes: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "Game":
        creator = d.get("creator", {})
        return cls(
            id=d.get("id", 0),
            root_place_id=d.get("rootPlaceId", 0),
            name=d.get("name", ""),
            description=d.get("description", ""),
            creator_name=creator.get("name", ""),
            creator_id=creator.get("id", 0),
            creator_type=creator.get("type", "User"),
            price=d.get("price"),
            playing=d.get("playing", 0),
            visits=d.get("visits", 0),
            max_players=d.get("maxPlayers", 0),
            created=d.get("created"),
            updated=d.get("updated"),
            genre=d.get("genre", ""),
            is_favorited=d.get("isFavoritedByUser", False),
            favorited_count=d.get("favoritedCount", 0),
        )

    def __str__(self) -> str:
        price_str = f"💰 {self.price}R$" if self.price else "Free"
        return (
            f"🎮 {self.name} [Universe: {self.id}]\n"
            f"   Creator : {self.creator_name} ({self.creator_type})\n"
            f"   Visits  : {self.visits:,}\n"
            f"   Playing : {self.playing:,}\n"
            f"   Max     : {self.max_players}\n"
            f"   Genre   : {self.genre}\n"
            f"   Price   : {price_str}\n"
            f"   Favs    : {self.favorited_count:,}"
        )


@dataclass
class GameVotes:
    universe_id: int
    up_votes: int
    down_votes: int

    @classmethod
    def from_dict(cls, d: dict) -> "GameVotes":
        return cls(
            universe_id=d.get("id", 0),
            up_votes=d.get("upVotes", 0),
            down_votes=d.get("downVotes", 0),
        )

    @property
    def ratio(self) -> float:
        total = self.up_votes + self.down_votes
        return round(self.up_votes / total * 100, 1) if total else 0.0

    def __str__(self) -> str:
        return f"👍 {self.up_votes:,}  👎 {self.down_votes:,}  ({self.ratio}% positive)"


@dataclass
class GameServer:
    id: str
    max_players: int
    playing: int
    fps: float
    ping: int

    @classmethod
    def from_dict(cls, d: dict) -> "GameServer":
        return cls(
            id=d.get("id", ""),
            max_players=d.get("maxPlayers", 0),
            playing=d.get("playing", 0),
            fps=round(d.get("fps", 0.0), 1),
            ping=d.get("ping", 0),
        )

    def __str__(self) -> str:
        fill = f"{self.playing}/{self.max_players}"
        return f"[{self.id[:8]}...] Players: {fill}  FPS: {self.fps}  Ping: {self.ping}ms"


# ─────────────────────────────────────────────
#  Catalog
# ─────────────────────────────────────────────

@dataclass
class CatalogItem:
    id: int
    item_type: str          # "Asset" or "Bundle"
    name: str
    description: str
    creator_name: str
    creator_id: int
    creator_type: str
    price: Optional[int]
    lowest_price: Optional[int]
    purchase_count: int
    favorite_count: int
    asset_type: Optional[str] = None
    bundle_type: Optional[str] = None
    is_off_sale: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "CatalogItem":
        return cls(
            id=d.get("id", 0),
            item_type=d.get("itemType", "Asset"),
            name=d.get("name", ""),
            description=d.get("description", ""),
            creator_name=d.get("creatorName", ""),
            creator_id=d.get("creatorTargetId", 0),
            creator_type=d.get("creatorType", "User"),
            price=d.get("price"),
            lowest_price=d.get("lowestPrice"),
            purchase_count=d.get("purchaseCount", 0),
            favorite_count=d.get("favoriteCount", 0),
            asset_type=d.get("assetType"),
            bundle_type=d.get("bundleType"),
            is_off_sale="OffSale" in d.get("itemStatus", []),
        )

    def __str__(self) -> str:
        price_str = f"{self.price}R$" if self.price else ("Off Sale" if self.is_off_sale else "Free")
        return (
            f"🛍  {self.name} [{self.item_type} #{self.id}]\n"
            f"   Creator  : {self.creator_name}\n"
            f"   Price    : {price_str}\n"
            f"   Sold     : {self.purchase_count:,}\n"
            f"   Favorites: {self.favorite_count:,}"
        )


@dataclass
class ResaleData:
    asset_id: int
    asset_stock: Optional[int]
    sales: int
    number_remaining: Optional[int]
    recent_average_price: Optional[int]
    original_price: Optional[int]

    @classmethod
    def from_dict(cls, asset_id: int, d: dict) -> "ResaleData":
        return cls(
            asset_id=asset_id,
            asset_stock=d.get("assetStock"),
            sales=d.get("sales", 0),
            number_remaining=d.get("numberRemaining"),
            recent_average_price=d.get("recentAveragePrice"),
            original_price=d.get("originalPrice"),
        )

    def __str__(self) -> str:
        return (
            f"📈 Asset #{self.asset_id} Resale Data\n"
            f"   RAP      : {self.recent_average_price:,}R$\n"
            f"   Sales    : {self.sales:,}\n"
            f"   Stock    : {self.asset_stock}\n"
            f"   Remaining: {self.number_remaining}"
        )


# ─────────────────────────────────────────────
#  Groups
# ─────────────────────────────────────────────

@dataclass
class Group:
    id: int
    name: str
    description: str
    owner_id: Optional[int]
    owner_name: Optional[str]
    member_count: int
    is_public: bool
    has_verified_badge: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Group":
        owner = d.get("owner") or {}
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            description=d.get("description", ""),
            owner_id=owner.get("userId"),
            owner_name=owner.get("username"),
            member_count=d.get("memberCount", 0),
            is_public=d.get("publicEntryAllowed", False),
            has_verified_badge=d.get("hasVerifiedBadge", False),
        )

    def __str__(self) -> str:
        verified = " ✓" if self.has_verified_badge else ""
        pub = "Public" if self.is_public else "Private"
        return (
            f"👥 {self.name}{verified} [ID: {self.id}]\n"
            f"   Owner  : {self.owner_name} (ID: {self.owner_id})\n"
            f"   Members: {self.member_count:,}\n"
            f"   Access : {pub}"
        )


@dataclass
class GroupRole:
    id: int
    name: str
    rank: int
    member_count: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "GroupRole":
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            rank=d.get("rank", 0),
            member_count=d.get("memberCount", 0),
        )

    def __str__(self) -> str:
        return f"[Rank {self.rank:>3}] {self.name:<30} ({self.member_count:,} members)"


# ─────────────────────────────────────────────
#  Friends / Followers
# ─────────────────────────────────────────────

@dataclass
class Friend:
    id: int
    name: str
    display_name: str
    is_online: bool = False
    has_verified_badge: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Friend":
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            display_name=d.get("displayName", ""),
            is_online=d.get("isOnline", False),
            has_verified_badge=d.get("hasVerifiedBadge", False),
        )

    def __str__(self) -> str:
        online = "🟢" if self.is_online else "⚫"
        verified = " ✓" if self.has_verified_badge else ""
        return f"{online} {self.display_name} (@{self.name}){verified} [ID: {self.id}]"


# ─────────────────────────────────────────────
#  Badges
# ─────────────────────────────────────────────

@dataclass
class Badge:
    id: int
    name: str
    description: str
    enabled: bool
    awarded_count: int = 0
    win_rate_percentage: float = 0.0

    @classmethod
    def from_dict(cls, d: dict) -> "Badge":
        stats = d.get("statistics", {})
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            description=d.get("description", ""),
            enabled=d.get("enabled", True),
            awarded_count=stats.get("awardedCount", 0),
            win_rate_percentage=stats.get("winRatePercentage", 0.0),
        )

    def __str__(self) -> str:
        status = "✅" if self.enabled else "❌"
        return (
            f"{status} {self.name} [ID: {self.id}]\n"
            f"   Awarded  : {self.awarded_count:,}\n"
            f"   Win Rate : {self.win_rate_percentage:.2f}%"
        )


# ─────────────────────────────────────────────
#  Economy
# ─────────────────────────────────────────────

@dataclass
class RobuxBalance:
    robux: int

    def __str__(self) -> str:
        return f"💎 {self.robux:,} Robux"


@dataclass
class Transaction:
    id: int
    created: str
    is_pending: bool
    agent_id: int
    agent_name: str
    agent_type: str
    details_type: str
    currency_type: str
    amount: int

    @classmethod
    def from_dict(cls, d: dict) -> "Transaction":
        agent = d.get("agent", {})
        details = d.get("details", {})
        currency = d.get("currency", {})
        return cls(
            id=d.get("id", 0),
            created=d.get("created", ""),
            is_pending=d.get("isPending", False),
            agent_id=agent.get("id", 0),
            agent_name=agent.get("name", ""),
            agent_type=agent.get("type", ""),
            details_type=details.get("type", ""),
            currency_type=currency.get("type", ""),
            amount=currency.get("amount", 0),
        )

    def __str__(self) -> str:
        sign = "+" if self.amount > 0 else ""
        pending = " (pending)" if self.is_pending else ""
        return f"{sign}{self.amount}R$ from {self.agent_name} [{self.details_type}]{pending}"


# ─────────────────────────────────────────────
#  Avatar
# ─────────────────────────────────────────────

@dataclass
class AvatarAsset:
    id: int
    name: str
    asset_type_id: int
    asset_type_name: str

    @classmethod
    def from_dict(cls, d: dict) -> "AvatarAsset":
        at = d.get("assetType", {})
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            asset_type_id=at.get("id", 0),
            asset_type_name=at.get("name", ""),
        )


@dataclass
class AvatarColors:
    head: str
    torso: str
    right_arm: str
    left_arm: str
    right_leg: str
    left_leg: str

    @classmethod
    def from_dict(cls, d: dict) -> "AvatarColors":
        return cls(
            head=d.get("headColorId", ""),
            torso=d.get("torsoColorId", ""),
            right_arm=d.get("rightArmColorId", ""),
            left_arm=d.get("leftArmColorId", ""),
            right_leg=d.get("rightLegColorId", ""),
            left_leg=d.get("leftLegColorId", ""),
        )


@dataclass
class Avatar:
    user_id: int
    avatar_type: str
    scales: dict
    assets: List[AvatarAsset] = field(default_factory=list)
    colors: Optional[AvatarColors] = None

    @classmethod
    def from_dict(cls, user_id: int, d: dict) -> "Avatar":
        assets = [AvatarAsset.from_dict(a) for a in d.get("assets", [])]
        colors = AvatarColors.from_dict(d.get("bodyColors", {}))
        return cls(
            user_id=user_id,
            avatar_type=d.get("playerAvatarType", ""),
            scales=d.get("scales", {}),
            assets=assets,
            colors=colors,
        )


# ─────────────────────────────────────────────
#  Presence
# ─────────────────────────────────────────────

@dataclass
class PresenceBatch:
    presences: List[UserPresence]

    @classmethod
    def from_dict(cls, d: dict) -> "PresenceBatch":
        return cls(
            presences=[UserPresence.from_dict(p) for p in d.get("userPresences", [])]
        )


# ─────────────────────────────────────────────
#  Pagination wrapper
# ─────────────────────────────────────────────

@dataclass
class Page:
    """Generic paginated result from any list endpoint."""
    data: list
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict, model=None) -> "Page":
        raw = d.get("data", [])
        items = [model.from_dict(i) for i in raw] if model else raw
        return cls(
            data=items,
            next_cursor=d.get("nextPageCursor"),
            previous_cursor=d.get("previousPageCursor"),
        )

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
