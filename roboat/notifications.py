"""
roboat.notifications
~~~~~~~~~~~~~~~~~~~~
Experience Notifications API — send push notifications to players
even when they are not in your game.

Requires Open Cloud API key with experience notifications permission.
https://create.roblox.com/dashboard/credentials

Example::

    from roboat.notifications import NotificationsAPI

    notif = NotificationsAPI(api_key="roblox-KEY-xxxx")

    notif.send(
        universe_id=123456,
        user_id=1234,
        payload_type="StringAttribute",
        message_id="your-message-id",
        attributes={"username": "Builderman", "score": "9000"},
        join_experience={"launchData": "rejoin_prompt"},
    )
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import requests


@dataclass
class NotificationResult:
    user_id: int
    success: bool
    error: Optional[str] = None

    def __str__(self) -> str:
        status = "✅ Sent" if self.success else f"❌ Failed: {self.error}"
        return f"User {self.user_id}: {status}"


class NotificationsAPI:
    """
    Experience Notifications via Open Cloud.

    Args:
        api_key: Open Cloud API key with notifications permission.
    """

    BASE = "https://apis.roblox.com/cloud/v2"

    def __init__(self, api_key: str, timeout: int = 10):
        self._key = api_key
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json",
        })

    def send(
        self,
        universe_id: int,
        user_id: int,
        message_id: str,
        attributes: Optional[Dict[str, str]] = None,
        join_experience: Optional[dict] = None,
        analytics_data: Optional[dict] = None,
    ) -> NotificationResult:
        """
        Send an experience notification to a single user.

        Args:
            universe_id: Your game's universe ID.
            user_id: The target player's user ID.
            message_id: The notification message ID from Creator Dashboard.
            attributes: Key-value pairs for message template substitution.
            join_experience: Optional launch data dict e.g. {"launchData": "..."}.
            analytics_data: Optional analytics category dict.

        Returns:
            NotificationResult with success/failure info.
        """
        payload: Dict[str, Any] = {
            "source": {"universe": f"universes/{universe_id}"},
            "destination": {"user": f"users/{user_id}"},
            "payload": {
                "messageId": message_id,
                "type": "MOMENT",
            },
        }
        if attributes:
            payload["payload"]["stringBindings"] = [
                {"key": k, "value": v} for k, v in attributes.items()
            ]
        if join_experience:
            payload["payload"]["joinExperience"] = join_experience
        if analytics_data:
            payload["payload"]["analyticsData"] = analytics_data

        try:
            r = self._session.post(
                f"{self.BASE}/users/{user_id}/notifications",
                json=payload,
                timeout=self._timeout,
            )
            r.raise_for_status()
            return NotificationResult(user_id=user_id, success=True)
        except Exception as e:
            return NotificationResult(user_id=user_id, success=False, error=str(e))

    def send_bulk(
        self,
        universe_id: int,
        user_ids: List[int],
        message_id: str,
        attributes: Optional[Dict[str, str]] = None,
        join_experience: Optional[dict] = None,
    ) -> List[NotificationResult]:
        """
        Send the same notification to multiple users.

        Returns:
            List of NotificationResult objects.
        """
        return [
            self.send(
                universe_id=universe_id,
                user_id=uid,
                message_id=message_id,
                attributes=attributes,
                join_experience=join_experience,
            )
            for uid in user_ids
        ]

    def get_quota(self, universe_id: int) -> dict:
        """
        Get the notification quota for a universe.

        Returns:
            dict with quota info (remaining sends, reset time, etc.)
        """
        r = self._session.get(
            f"{self.BASE}/universes/{universe_id}/notificationQuota",
            timeout=self._timeout,
        )
        r.raise_for_status()
        return r.json()
