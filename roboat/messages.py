"""
roboat.messages
~~~~~~~~~~~~~~~~~~
Private Messages API — privatemessages.roblox.com
All endpoints require authentication.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .models import Page


@dataclass
class Message:
    id: int
    sender_id: int
    sender_name: str
    recipient_id: int
    recipient_name: str
    subject: str
    body: str
    created: str
    updated: str
    is_read: bool
    is_system_message: bool

    @classmethod
    def from_dict(cls, d: dict) -> "Message":
        sender = d.get("sender", {})
        recipient = d.get("recipient", {})
        return cls(
            id=d.get("id", 0),
            sender_id=sender.get("id", 0),
            sender_name=sender.get("name", ""),
            recipient_id=recipient.get("id", 0),
            recipient_name=recipient.get("name", ""),
            subject=d.get("subject", ""),
            body=d.get("body", ""),
            created=d.get("created", ""),
            updated=d.get("updated", ""),
            is_read=d.get("isRead", False),
            is_system_message=d.get("isSystemMessage", False),
        )

    def __str__(self) -> str:
        read = "📬" if not self.is_read else "📭"
        return f"{read} [{self.id}] From: {self.sender_name} | {self.subject}"


class MessagesAPI:
    BASE = "https://privatemessages.roblox.com/v1"

    def __init__(self, client):
        self._c = client

    def get_messages(self, message_type: str = "Inbox",
                     page_size: int = 25, page_number: int = 0) -> Page:
        """
        Get private messages. Requires auth.

        Args:
            message_type: "Inbox", "Sent", "Archive"
            page_size: 10, 20, 25
            page_number: Zero-indexed page number.

        Returns:
            Page of Message objects.
        """
        self._c.require_auth("get_messages")
        data = self._c._get(
            f"{self.BASE}/messages",
            params={
                "messageTab": message_type,
                "pageSize": page_size,
                "pageNumber": page_number,
            },
        )
        messages = [Message.from_dict(m) for m in data.get("collection", [])]
        return Page(data=messages)

    def get_message(self, message_id: int) -> Message:
        """Get a single message by ID. Requires auth."""
        self._c.require_auth("get_message")
        data = self._c._get(f"{self.BASE}/messages/{message_id}")
        return Message.from_dict(data)

    def send_message(self, recipient_id: int, subject: str, body: str) -> dict:
        """Send a private message. Requires auth."""
        self._c.require_auth("send_message")
        return self._c._post(
            f"{self.BASE}/messages/send",
            json={
                "recipientId": recipient_id,
                "subject": subject,
                "body": body,
            },
        )

    def get_unread_count(self) -> int:
        """Get count of unread messages. Requires auth."""
        self._c.require_auth("get_unread_count")
        data = self._c._get(f"{self.BASE}/messages/unread/count")
        return data.get("count", 0)

    def mark_read(self, message_ids: List[int]) -> None:
        """Mark messages as read. Requires auth."""
        self._c.require_auth("mark_read")
        self._c._post(
            f"{self.BASE}/messages/mark-read",
            json={"messageIds": message_ids},
        )

    def mark_unread(self, message_ids: List[int]) -> None:
        """Mark messages as unread. Requires auth."""
        self._c.require_auth("mark_unread")
        self._c._post(
            f"{self.BASE}/messages/mark-unread",
            json={"messageIds": message_ids},
        )

    def archive(self, message_ids: List[int]) -> None:
        """Archive messages. Requires auth."""
        self._c.require_auth("archive")
        self._c._post(
            f"{self.BASE}/messages/archive",
            json={"messageIds": message_ids},
        )


@dataclass
class ChatConversation:
    id: int
    title: str
    conversation_type: str
    participants: List[dict] = field(default_factory=list)
    last_updated: Optional[str] = None
    unread_count: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "ChatConversation":
        return cls(
            id=d.get("id", 0),
            title=d.get("title", ""),
            conversation_type=d.get("conversationType", ""),
            participants=d.get("participants", []),
            last_updated=d.get("lastUpdated"),
            unread_count=d.get("unreadMessageCount", 0),
        )

    def __str__(self) -> str:
        unread = f" [{self.unread_count} unread]" if self.unread_count else ""
        return f"💬 {self.title}{unread}"


class ChatAPI:
    BASE = "https://chat.roblox.com/v2"

    def __init__(self, client):
        self._c = client

    def get_conversations(self, page_size: int = 30,
                          page_number: int = 1) -> List[ChatConversation]:
        """Get chat conversations. Requires auth."""
        self._c.require_auth("get_conversations")
        data = self._c._get(
            f"{self.BASE}/get-user-conversations",
            params={"pageSize": page_size, "pageNumber": page_number},
        )
        return [ChatConversation.from_dict(c) for c in (data if isinstance(data, list) else [])]

    def get_unread_conversation_count(self) -> int:
        """Get count of conversations with unread messages. Requires auth."""
        self._c.require_auth("get_unread_conversation_count")
        data = self._c._get(f"{self.BASE}/get-unread-conversation-count")
        return data.get("count", 0)

    def get_messages(self, conversation_id: int,
                     page_size: int = 30) -> list:
        """Get messages in a conversation. Requires auth."""
        self._c.require_auth("get_messages")
        data = self._c._get(
            f"{self.BASE}/get-messages",
            params={"conversationId": conversation_id, "pageSize": page_size},
        )
        return data if isinstance(data, list) else []

    def send_message(self, conversation_id: int, message: str) -> dict:
        """Send a chat message. Requires auth."""
        self._c.require_auth("send_message")
        return self._c._post(
            f"{self.BASE}/send-message",
            json={"conversationId": conversation_id, "message": message},
        )
