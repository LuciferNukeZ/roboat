"""
Type stubs for roboat — enables full IDE autocomplete.
"""

from typing import Optional
from roboat.models import (
    User, Game, GameVotes, GameServer,
    Friend, Group, GroupRole, Badge,
    CatalogItem, ResaleData, Avatar,
    UserPresence, RobuxBalance, Page,
    Transaction,
)
from roboat.trades import Trade, TradeOffer, TradeAsset
from roboat.messages import Message, ChatConversation
from roboat.inventory import InventoryAsset
from roboat.develop import Universe, Place, DataStore
from roboat.marketplace import MarketplaceAPI, LimitedData, ResaleProfit, RAPTracker
from roboat.social import SocialGraph, UserNode, PresenceSnapshot
from roboat.notifications import NotificationsAPI, NotificationResult
from roboat.publish import PublishAPI, UploadedAsset
from roboat.moderation import ModerationAPI, AccountStanding, AbuseReport
from roboat.oauth import OAuthManager, OAUTH_URL
from roboat.database import SessionDatabase
from roboat.events import EventPoller
from roboat.analytics import Analytics
from roboat.client import RoboatClient, ClientBuilder
from roboat.async_client import AsyncRoboatClient
from roboat.opencloud import RoboatCloudClient
from roboat.session import RoboatSession

__version__: str
__author__: str
__license__: str

__all__ = [
    "RoboatClient", "ClientBuilder", "AsyncRoboatClient",
    "RoboatCloudClient", "RoboatSession", "SessionDatabase",
    "EventPoller", "Analytics", "OAuthManager", "OAUTH_URL",
    "MarketplaceAPI", "SocialGraph", "NotificationsAPI",
    "PublishAPI", "ModerationAPI",
    "User", "Game", "GameVotes", "GameServer", "Friend",
    "Group", "GroupRole", "Badge", "CatalogItem", "ResaleData",
    "Avatar", "UserPresence", "RobuxBalance", "Page",
    "Trade", "TradeOffer", "TradeAsset",
    "Message", "ChatConversation",
    "InventoryAsset", "Universe", "Place", "DataStore",
    "LimitedData", "ResaleProfit", "RAPTracker",
    "UserNode", "PresenceSnapshot",
    "NotificationResult", "UploadedAsset",
    "AccountStanding", "AbuseReport",
]
