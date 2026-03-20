"""
roboat v2.1.0 — Python interface for the Roblox ecosystem.
OAuth-authenticated. No cookie required.
"""

from .client       import RoboatClient, ClientBuilder
from .async_client import AsyncRoboatClient
from .opencloud    import RoboatCloudClient
from .session      import RoboatSession
from .database     import SessionDatabase
from .events       import EventPoller
from .analytics    import Analytics
from .oauth        import OAuthManager, get_oauth_url, OAUTH_URL
from .utils        import TokenBucket, TTLCache, Paginator, retry, cached

from .models import (
    User, UserPresence,
    Game, GameVotes, GameServer,
    CatalogItem, ResaleData,
    Group, GroupRole,
    Friend,
    Badge,
    Avatar, AvatarAsset, AvatarColors,
    RobuxBalance, Transaction,
    Page,
)
from .trades      import Trade, TradeOffer, TradeAsset
from .messages    import Message, ChatConversation
from .inventory   import InventoryAsset
from .develop     import Universe, Place, DataStore, PlaceVersion, TeamCreateMember, PluginInfo
from .groups      import GroupShout, GroupPayout, GroupJoinRequest, GroupRelationship
from .marketplace import MarketplaceAPI, LimitedData, ResaleProfit, RAPTracker
from .social      import SocialGraph, UserNode, PresenceSnapshot
from .notifications import NotificationsAPI, NotificationResult
from .publish     import PublishAPI, UploadedAsset
from .moderation  import ModerationAPI, AccountStanding, AbuseReport

from .exceptions import (
    RoboatAPIError,
    NotAuthenticatedError,
    UserNotFoundError,
    GameNotFoundError,
    ItemNotFoundError,
    GroupNotFoundError,
    BadgeNotFoundError,
    RateLimitedError,
    InvalidCookieError,
    InsufficientFundsError,
    DatabaseError,
)

__version__ = "2.1.0"
__author__  = "roboat contributors"
__license__ = "MIT"
