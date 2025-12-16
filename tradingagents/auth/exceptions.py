"""Custom exceptions for the authentication subsystem."""

from __future__ import annotations


class AuthenticationError(Exception):
    """Base error raised for authentication failures."""


class DeviceCodeError(AuthenticationError):
    """Raised when initiating or handling the device-code flow fails."""


class TokenRefreshError(AuthenticationError):
    """Raised when refreshing a token cannot be completed."""


class TokenStorageError(AuthenticationError):
    """Raised when reading from or writing to the token store fails."""


class TokenRevocationError(AuthenticationError):
    """Raised when attempting to revoke a token fails."""
