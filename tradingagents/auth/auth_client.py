"""Device-code OAuth client with persistent token handling."""

from __future__ import annotations

import os
import time
import webbrowser
from dataclasses import dataclass
from typing import Optional

import requests

from .exceptions import (
    AuthenticationError,
    DeviceCodeError,
    TokenRefreshError,
    TokenRevocationError,
)
from .models import DeviceCodeGrant, TokenSet
from .token_store import TokenStore

DEFAULT_AUTH_BASE_URL = os.environ.get("TRADINGAGENTS_AUTH_BASE_URL", "https://api.openai.com/v1/auth")
DEFAULT_CLIENT_ID = os.environ.get("TRADINGAGENTS_CLIENT_ID", "tradingagents-cli")
DEFAULT_SCOPE = os.environ.get("TRADINGAGENTS_SCOPE", "openid profile offline_access")


@dataclass
class _AuthEndpoints:
    device_code: str
    token: str
    revoke: str


class AuthClient:
    """Handle device-code authentication, refresh, and revocation."""

    def __init__(
        self,
        *,
        client_id: str = DEFAULT_CLIENT_ID,
        base_url: str = DEFAULT_AUTH_BASE_URL,
        scope: str = DEFAULT_SCOPE,
        token_store: Optional[TokenStore] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.client_id = client_id
        self.base_url = base_url.rstrip("/")
        self.scope = scope
        self.token_store = token_store or TokenStore()
        self.session = session or requests.Session()
        self.endpoints = _AuthEndpoints(
            device_code=f"{self.base_url}/device/code",
            token=f"{self.base_url}/token",
            revoke=f"{self.base_url}/revoke",
        )

    def start_device_code(self) -> DeviceCodeGrant:
        payload = {"client_id": self.client_id, "scope": self.scope}
        response = self.session.post(self.endpoints.device_code, data=payload, timeout=10)
        if not response.ok:
            raise DeviceCodeError(f"Device-code initiation failed: {response.text}")
        return DeviceCodeGrant.from_response(response.json())

    def poll_for_token(self, grant: DeviceCodeGrant) -> TokenSet:
        interval = grant.interval
        while not grant.is_expired():
            token_response = self.session.post(
                self.endpoints.token,
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": grant.device_code,
                    "client_id": self.client_id,
                },
                timeout=10,
            )
            if token_response.ok:
                return TokenSet.from_response(token_response.json())

            try:
                error = token_response.json().get("error")
            except ValueError:
                error = token_response.text

            if error == "authorization_pending":
                time.sleep(interval)
                continue
            if error == "slow_down":
                interval += 5
                time.sleep(interval)
                continue
            if error == "expired_token":
                raise DeviceCodeError("The device code has expired before authorization was completed.")

            raise AuthenticationError(f"Authentication failed: {error}")

        raise DeviceCodeError("Device code expired before polling completed.")

    def refresh(self, refresh_token: str) -> TokenSet:
        response = self.session.post(
            self.endpoints.token,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
            },
            timeout=10,
        )
        if not response.ok:
            raise TokenRefreshError(f"Failed to refresh token: {response.text}")
        return TokenSet.from_response(response.json())

    def revoke(self, token: str) -> None:
        response = self.session.post(
            self.endpoints.revoke,
            data={"token": token, "client_id": self.client_id},
            timeout=10,
        )
        if response.status_code not in (200, 204):
            raise TokenRevocationError(f"Failed to revoke token: {response.text}")

    def _open_browser(self, grant: DeviceCodeGrant) -> None:
        url = grant.verification_uri_complete or grant.verification_uri
        webbrowser.open(url, new=1, autoraise=True)

    def login(self, *, open_browser: bool = True) -> TokenSet:
        grant = self.start_device_code()
        if open_browser:
            self._open_browser(grant)
        token_set = self.poll_for_token(grant)
        self.token_store.save(token_set)
        return token_set

    def get_session(self) -> TokenSet:
        token_set = self.token_store.load()
        if token_set and not token_set.is_expired():
            return token_set

        if token_set and token_set.refresh_token:
            try:
                refreshed = self.refresh(token_set.refresh_token)
                self.token_store.save(refreshed)
                return refreshed
            except TokenRefreshError:
                pass

        return self.login()

    def logout(self) -> None:
        token_set = self.token_store.load()
        if token_set:
            try:
                self.revoke(token_set.access_token)
            except TokenRevocationError:
                # Best-effort: still clear the local cache even if remote revocation fails.
                pass
        self.token_store.clear()


def _default_client() -> AuthClient:
    return AuthClient()


def login(*, open_browser: bool = True) -> TokenSet:
    client = _default_client()
    return client.login(open_browser=open_browser)


def get_session() -> TokenSet:
    client = _default_client()
    return client.get_session()


def logout() -> None:
    client = _default_client()
    client.logout()
