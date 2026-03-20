"""
roboat.moderation
~~~~~~~~~~~~~~~~~
Moderation utilities — report abuse, check account standing,
and manage moderation actions across your experience.

Example::

    from roboat.moderation import ModerationAPI

    mod = ModerationAPI(client)

    # Check if a user is in good standing
    standing = mod.get_account_standing(user_id=1234)
    print(standing)

    # Report abusive content
    mod.report_asset(asset_id=11111, reason="Inappropriate content")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .models import Page


@dataclass
class AccountStanding:
    user_id: int
    can_view_restricted: bool
    account_age_days: int
    has_verified_email: bool
    is_over_13: bool

    @classmethod
    def from_dict(cls, user_id: int, d: dict) -> "AccountStanding":
        return cls(
            user_id=user_id,
            can_view_restricted=d.get("canViewRestrictedContent", False),
            account_age_days=d.get("accountAgeInDays", 0),
            has_verified_email=d.get("hasVerifiedEmail", False),
            is_over_13=d.get("isOver13", False),
        )

    def __str__(self) -> str:
        age_str = f"{self.account_age_days} days"
        over13  = "13+" if self.is_over_13 else "Under 13"
        email   = "✅ Verified" if self.has_verified_email else "❌ Unverified"
        return (
            f"👤 User {self.user_id} Standing\n"
            f"   Age      : {age_str}\n"
            f"   Over 13  : {over13}\n"
            f"   Email    : {email}"
        )


@dataclass
class AbuseReport:
    report_id: Optional[str]
    success: bool
    message: str

    def __str__(self) -> str:
        status = "✅ Reported" if self.success else "❌ Failed"
        return f"{status}: {self.message}"


class ModerationAPI:
    """
    Moderation utilities built on top of RoboatClient.

    Args:
        client: An authenticated RoboatClient instance.
    """

    BASE_AUTH   = "https://auth.roblox.com/v1"
    BASE_USERS  = "https://users.roblox.com/v1"
    BASE_ABUSE  = "https://abuse-reporting.roblox.com/v1"
    BASE_ACCT   = "https://accountinformation.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    # ── Account info ──────────────────────────────────────────────────

    def get_account_standing(self, user_id: int) -> AccountStanding:
        """
        Get moderation-relevant account info for a user.

        Returns:
            AccountStanding with age, email verification, and 13+ status.
        """
        data = self._c._get(
            f"https://apis.roblox.com/account-information/v1/users/{user_id}"
        )
        return AccountStanding.from_dict(user_id, data)

    def get_content_restrictions(self, user_id: int) -> dict:
        """
        Check what content restrictions are active for a user.
        Useful for enforcing age-appropriate content in your experience.

        Returns:
            dict with restriction flags.
        """
        return self._c._get(
            f"https://apis.roblox.com/content-restrictions/v1/users/{user_id}"
        )

    # ── Reporting ─────────────────────────────────────────────────────

    def report_user(self, user_id: int, reason: str,
                    comment: str = "") -> AbuseReport:
        """
        Submit an abuse report against a user. Requires auth.

        Args:
            user_id: The user to report.
            reason: Short reason string.
            comment: Additional context (optional).

        Returns:
            AbuseReport indicating success/failure.
        """
        self._c.require_auth("report_user")
        try:
            self._c._post(
                f"{self.BASE_ABUSE}/reports/user",
                json={
                    "userId": user_id,
                    "reason": reason,
                    "comment": comment,
                },
            )
            return AbuseReport(report_id=None, success=True,
                               message=f"User {user_id} reported.")
        except Exception as e:
            return AbuseReport(report_id=None, success=False, message=str(e))

    def report_asset(self, asset_id: int, reason: str,
                     comment: str = "") -> AbuseReport:
        """
        Submit an abuse report against a catalog asset. Requires auth.

        Returns:
            AbuseReport indicating success/failure.
        """
        self._c.require_auth("report_asset")
        try:
            self._c._post(
                f"{self.BASE_ABUSE}/reports/asset",
                json={
                    "assetId": asset_id,
                    "reason": reason,
                    "comment": comment,
                },
            )
            return AbuseReport(report_id=None, success=True,
                               message=f"Asset {asset_id} reported.")
        except Exception as e:
            return AbuseReport(report_id=None, success=False, message=str(e))

    def report_game(self, universe_id: int, reason: str,
                    comment: str = "") -> AbuseReport:
        """
        Submit an abuse report against a game. Requires auth.

        Returns:
            AbuseReport indicating success/failure.
        """
        self._c.require_auth("report_game")
        try:
            self._c._post(
                f"{self.BASE_ABUSE}/reports/game",
                json={
                    "universeId": universe_id,
                    "reason": reason,
                    "comment": comment,
                },
            )
            return AbuseReport(report_id=None, success=True,
                               message=f"Game {universe_id} reported.")
        except Exception as e:
            return AbuseReport(report_id=None, success=False, message=str(e))

    # ── Block / unblock ────────────────────────────────────────────────

    def get_blocked_users(self) -> List[int]:
        """
        Get list of user IDs the authenticated user has blocked. Requires auth.

        Returns:
            List of blocked user IDs.
        """
        self._c.require_auth("get_blocked_users")
        data = self._c._get(
            "https://accountsettings.roblox.com/v1/users/get-detailed-blocked-users"
        )
        return [u.get("userId") for u in data.get("blockedUsers", [])]

    def block_user(self, user_id: int) -> None:
        """Block a user. Requires auth."""
        self._c.require_auth("block_user")
        self._c._post(
            f"https://accountsettings.roblox.com/v1/users/{user_id}/block"
        )

    def unblock_user(self, user_id: int) -> None:
        """Unblock a user. Requires auth."""
        self._c.require_auth("unblock_user")
        self._c._post(
            f"https://accountsettings.roblox.com/v1/users/{user_id}/unblock"
        )

    # ── Chat safety ────────────────────────────────────────────────────

    def filter_text(self, text: str, user_id: int) -> dict:
        """
        Run text through Roblox's chat filter. Requires auth.
        Useful for pre-validating user-submitted text before storing it.

        Args:
            text: The text to check.
            user_id: The user context for the filter.

        Returns:
            dict with filtered text and whether it was modified.
        """
        self._c.require_auth("filter_text")
        return self._c._post(
            "https://develop.roblox.com/v1/gameUpdateNotifications/filter",
            json={"text": text, "userId": user_id},
        )
