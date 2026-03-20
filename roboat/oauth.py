"""
roboat.oauth
~~~~~~~~~~~~
OAuth 2.0 authentication for the Roblox API.
Opens the Roblox authorization URL, waits up to 120 seconds for the user
to complete it, then exchanges the code for an access token.
"""

from __future__ import annotations
import threading
import time
import webbrowser
from typing import Optional, Callable

OAUTH_URL = (
    "https://authorize.roblox.com/?client_id=8759333275480296790"
    "&response_type=code"
    "&redirect_uri=https%3A%2F%2Froblox.com%2Fcallback"
    "&scope=openid+profile"
    "&state=g1hvseqhr6"
    "&step=landing"
)

TIMEOUT = 120  # seconds to wait for user to complete OAuth


class OAuthState:
    """
    Holds the result of an OAuth flow attempt.

    States:
        pending   — waiting for user to authorize
        success   — token received
        failed    — timed out or error
    """

    def __init__(self):
        self.state: str = "pending"
        self.access_token: Optional[str] = None
        self.error: Optional[str] = None
        self._event = threading.Event()

    def succeed(self, access_token: str) -> None:
        self.access_token = access_token
        self.state = "success"
        self._event.set()

    def fail(self, reason: str = "Authentication timed out.") -> None:
        self.error = reason
        self.state = "failed"
        self._event.set()

    def wait(self, timeout: float = TIMEOUT) -> bool:
        """Block until done or timeout. Returns True on success."""
        self._event.wait(timeout=timeout)
        return self.state == "success"

    @property
    def is_pending(self) -> bool:
        return self.state == "pending"

    @property
    def is_authenticated(self) -> bool:
        return self.state == "success"


class OAuthManager:
    """
    Manages the OAuth 2.0 flow for roboat.

    Usage::

        manager = OAuthManager()
        token = manager.authenticate()   # opens browser, waits 120s
        if token:
            client = RoboatClient(oauth_token=token)
        else:
            print("Authentication failed")
    """

    def __init__(
        self,
        on_success: Optional[Callable[[str], None]] = None,
        on_failure: Optional[Callable[[str], None]] = None,
        timeout: int = TIMEOUT,
    ):
        self._on_success = on_success
        self._on_failure = on_failure
        self._timeout = timeout
        self._state: Optional[OAuthState] = None

    def authenticate(self, open_browser: bool = True) -> Optional[str]:
        """
        Launch the OAuth flow.

        Opens the Roblox authorization URL in the user's browser,
        then waits up to ``timeout`` seconds for completion.

        Args:
            open_browser: If True, automatically open the URL.

        Returns:
            Access token string on success, None on failure/timeout.
        """
        self._state = OAuthState()

        if open_browser:
            webbrowser.open(OAUTH_URL)

        # Start timeout thread
        def _timeout_watcher():
            if not self._state.wait(self._timeout):
                if self._state.is_pending:
                    self._state.fail("Authentication timed out after 120 seconds.")
                    if self._on_failure:
                        self._on_failure(self._state.error)

        t = threading.Thread(target=_timeout_watcher, daemon=True)
        t.start()

        return self._state.access_token if self._state.is_authenticated else None

    def receive_token(self, access_token: str) -> None:
        """
        Call this when you receive the OAuth access token
        (e.g. from your callback handler).

        Args:
            access_token: The access token from the OAuth callback.
        """
        if self._state and self._state.is_pending:
            self._state.succeed(access_token)
            if self._on_success:
                self._on_success(access_token)

    def cancel(self) -> None:
        """Cancel the current auth flow."""
        if self._state and self._state.is_pending:
            self._state.fail("Authentication cancelled.")

    @property
    def is_pending(self) -> bool:
        return self._state is not None and self._state.is_pending

    @property
    def oauth_url(self) -> str:
        return OAUTH_URL


def get_oauth_url() -> str:
    """Return the Roblox OAuth authorization URL."""
    return OAUTH_URL
