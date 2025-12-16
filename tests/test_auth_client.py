from datetime import datetime, timedelta, timezone

import pytest

from tradingagents.auth.auth_client import AuthClient, DeviceCodeError
from tradingagents.auth.models import DeviceCodeGrant, TokenSet


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text or ""
        self.ok = 200 <= status_code < 400

    def json(self):
        if self._payload is None:
            raise ValueError("no json payload")
        return self._payload


class FakeSession:
    def __init__(self, *, posts=None, gets=None):
        self.posts = posts or []
        self.gets = gets or []
        self.calls = []

    def post(self, url, data=None, timeout=None):
        self.calls.append(("post", url, data))
        if not self.posts:
            raise AssertionError("Unexpected POST call")
        responder = self.posts.pop(0)
        return responder() if callable(responder) else responder

    def get(self, url, headers=None, timeout=None):
        self.calls.append(("get", url, headers))
        if not self.gets:
            raise AssertionError("Unexpected GET call")
        responder = self.gets.pop(0)
        return responder() if callable(responder) else responder


class MemoryTokenStore:
    def __init__(self, token: TokenSet | None = None):
        self.token = token
        self.saved = None
        self.cleared = False

    def save(self, token: TokenSet):
        self.saved = token
        self.token = token

    def load(self):
        return self.token

    def clear(self):
        self.cleared = True
        self.token = None


def make_grant(interval: int = 0) -> DeviceCodeGrant:
    return DeviceCodeGrant(
        device_code="device",
        user_code="user",
        verification_uri="https://verify",
        verification_uri_complete=None,
        expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=5),
        interval=interval,
    )


def make_token(expired: bool = False) -> TokenSet:
    expires_at = datetime.now(tz=timezone.utc)
    expires_at += timedelta(minutes=5) if not expired else timedelta(minutes=-5)
    return TokenSet(
        access_token="access", refresh_token="refresh", token_type="bearer", scope=None, expires_at=expires_at
    )


def test_login_saves_tokens(monkeypatch):
    grant_payload = {
        "device_code": "device",
        "user_code": "user",
        "verification_uri": "https://verify",
        "expires_in": 600,
        "interval": 0,
    }
    token_payload = {
        "access_token": "new", "refresh_token": "ref", "token_type": "bearer", "expires_in": 3600
    }

    session = FakeSession(posts=[FakeResponse(payload=grant_payload), FakeResponse(payload=token_payload)])
    store = MemoryTokenStore()
    client = AuthClient(token_store=store, session=session)

    monkeypatch.setattr(client, "_open_browser", lambda grant: None)
    token = client.login(open_browser=False)

    assert token.access_token == "new"
    assert store.saved == token
    assert session.calls[0][1].endswith("/device/code")


def test_poll_waits_for_authorization(monkeypatch):
    grant = make_grant(interval=0)
    session = FakeSession(
        posts=[
            FakeResponse(status_code=400, payload={"error": "authorization_pending"}),
            FakeResponse(payload={"access_token": "ok", "expires_in": 5}),
        ]
    )
    client = AuthClient(session=session)
    monkeypatch.setattr(client, "token_store", MemoryTokenStore())
    monkeypatch.setattr("tradingagents.auth.auth_client.time.sleep", lambda *_: None)

    token = client.poll_for_token(grant)
    assert token.access_token == "ok"


def test_refreshes_expired_session(monkeypatch):
    old_token = make_token(expired=True)
    new_token_payload = {"access_token": "fresh", "refresh_token": "r2", "expires_in": 10}
    session = FakeSession(posts=[FakeResponse(payload=new_token_payload)])
    store = MemoryTokenStore(token=old_token)
    client = AuthClient(token_store=store, session=session)

    refreshed = client.get_session()

    assert refreshed.access_token == "fresh"
    assert store.saved.access_token == "fresh"


def test_logout_revokes_and_clears(monkeypatch):
    token = make_token()
    session = FakeSession(posts=[FakeResponse(status_code=200)])
    store = MemoryTokenStore(token=token)
    client = AuthClient(token_store=store, session=session)

    client.logout()

    assert store.cleared is True
    assert session.calls[0][1].endswith("/revoke")


def test_discover_models_uses_authorization_header():
    token = make_token()
    payload = {"providers": []}
    session = FakeSession(gets=[FakeResponse(payload=payload)])
    store = MemoryTokenStore(token=token)
    client = AuthClient(token_store=store, session=session)

    result = client.discover_models()

    assert result == payload
    assert session.calls[0][2]["Authorization"] == token.as_authorization_header()


def test_poll_raises_on_expired_code(monkeypatch):
    grant = make_grant(interval=0)
    grant.expires_at = datetime.now(tz=timezone.utc) - timedelta(seconds=1)
    session = FakeSession(posts=[])
    client = AuthClient(session=session)
    monkeypatch.setattr("tradingagents.auth.auth_client.time.sleep", lambda *_: None)

    with pytest.raises(DeviceCodeError):
        client.poll_for_token(grant)
