"""
tests/test_exceptions.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Tests for the roboat exception hierarchy.
"""

import pytest
from roboat.exceptions import (
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


class TestExceptionHierarchy:
    def test_all_inherit_from_base(self):
        exceptions = [
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
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, RoboatAPIError), \
                f"{exc_class.__name__} should inherit from RoboatAPIError"

    def test_base_is_exception(self):
        assert issubclass(RoboatAPIError, Exception)

    def test_not_authenticated_message(self):
        e = NotAuthenticatedError("my_method")
        assert "my_method" in str(e)
        assert "authentication" in str(e).lower()

    def test_rate_limited_message(self):
        e = RateLimitedError()
        assert "rate" in str(e).lower() or "429" in str(e).lower() or "slow" in str(e).lower()

    def test_invalid_cookie_message(self):
        e = InvalidCookieError()
        assert len(str(e)) > 0

    def test_can_catch_as_base(self):
        with pytest.raises(RoboatAPIError):
            raise UserNotFoundError("user not found")

    def test_can_catch_specifically(self):
        with pytest.raises(UserNotFoundError):
            raise UserNotFoundError("specific")

    def test_not_authenticated_no_method(self):
        e = NotAuthenticatedError()
        assert "authentication" in str(e).lower() or "cookie" in str(e).lower()

    def test_custom_message(self):
        e = DatabaseError("DB file corrupt")
        assert "DB file corrupt" in str(e)

    def test_raise_and_catch_chain(self):
        """Test that multiple exception types can be caught correctly."""
        for exc_class, specific_class in [
            (UserNotFoundError, UserNotFoundError),
            (GameNotFoundError, GameNotFoundError),
            (RateLimitedError, RateLimitedError),
        ]:
            caught = False
            try:
                raise exc_class("test")
            except specific_class:
                caught = True
            assert caught, f"{exc_class.__name__} not caught as {specific_class.__name__}"
