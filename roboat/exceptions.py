"""
roboat.exceptions
~~~~~~~~~~~~~~~~~~~~
All custom exceptions raised by roboat.
"""


class RobloxAPIError(Exception):
    """Base exception for all roboat errors."""
    pass


class NotAuthenticatedError(RobloxAPIError):
    """Raised when an endpoint requires authentication but no cookie is set."""
    def __init__(self, method: str = ""):
        msg = f"{method} requires authentication. Pass a .ROBLOSECURITY cookie to RoboatClient."
        super().__init__(msg)


class UserNotFoundError(RobloxAPIError):
    """Raised when a user ID or username cannot be found."""
    pass


class GameNotFoundError(RobloxAPIError):
    """Raised when a universe/place ID cannot be found."""
    pass


class ItemNotFoundError(RobloxAPIError):
    """Raised when a catalog item cannot be found."""
    pass


class GroupNotFoundError(RobloxAPIError):
    """Raised when a group cannot be found."""
    pass


class BadgeNotFoundError(RobloxAPIError):
    """Raised when a badge cannot be found."""
    pass


class RateLimitedError(RobloxAPIError):
    """Raised when Roblox returns a 429 Too Many Requests."""
    def __init__(self):
        super().__init__("Rate limited by Roblox API. Slow down requests.")


class InvalidCookieError(RobloxAPIError):
    """Raised when the provided .ROBLOSECURITY cookie is invalid or expired."""
    def __init__(self):
        super().__init__("Invalid or expired .ROBLOSECURITY cookie.")


class InsufficientFundsError(RobloxAPIError):
    """Raised when a purchase cannot be completed due to insufficient Robux."""
    pass


class DatabaseError(RobloxAPIError):
    """Raised for errors relating to the local session database."""
    pass
