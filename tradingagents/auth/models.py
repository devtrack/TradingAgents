"""Data models for authentication tokens."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional


@dataclass
class DeviceCodeGrant:
    """Represents the parameters returned by a device-code initiation call."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: Optional[str]
    expires_at: datetime
    interval: int

    @classmethod
    def from_response(cls, payload: dict) -> "DeviceCodeGrant":
        expires_in = int(payload.get("expires_in", 600))
        interval = int(payload.get("interval", 5))
        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
        return cls(
            device_code=payload["device_code"],
            user_code=payload["user_code"],
            verification_uri=payload.get("verification_uri") or payload.get("verification_uri_complete", ""),
            verification_uri_complete=payload.get("verification_uri_complete"),
            expires_at=expires_at,
            interval=interval,
        )

    def is_expired(self) -> bool:
        return datetime.now(tz=timezone.utc) >= self.expires_at


@dataclass
class TokenSet:
    """Represents an OAuth access token bundle."""

    access_token: str
    token_type: str
    expires_at: datetime
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

    @classmethod
    def from_response(cls, payload: dict) -> "TokenSet":
        expires_in = int(payload.get("expires_in", 0))
        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
        return cls(
            access_token=payload["access_token"],
            token_type=payload.get("token_type", "bearer"),
            expires_at=expires_at,
            refresh_token=payload.get("refresh_token"),
            scope=payload.get("scope"),
        )

    def is_expired(self, skew_seconds: int = 30) -> bool:
        margin = timedelta(seconds=skew_seconds)
        return datetime.now(tz=timezone.utc) >= (self.expires_at - margin)

    def as_authorization_header(self) -> str:
        return f"{self.token_type.capitalize()} {self.access_token}"
