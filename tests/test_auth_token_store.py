import json
from datetime import datetime, timedelta, timezone

from tradingagents.auth import token_store
from tradingagents.auth.models import TokenSet
from tradingagents.auth.token_store import TokenStore


class DummyKeyring:
    def __init__(self):
        self.storage = {}

        class _Errors:
            class PasswordDeleteError(Exception):
                pass

        self.errors = _Errors()

    def get_password(self, service_name, username):
        return self.storage.get((service_name, username))

    def set_password(self, service_name, username, password):
        self.storage[(service_name, username)] = password

    def delete_password(self, service_name, username):
        try:
            del self.storage[(service_name, username)]
        except KeyError:
            raise self.errors.PasswordDeleteError()


def _sample_token(expires_delta: timedelta = timedelta(minutes=5)) -> TokenSet:
    return TokenSet(
        access_token="access",
        refresh_token="refresh",
        token_type="bearer",
        scope="scope",
        expires_at=datetime.now(tz=timezone.utc) + expires_delta,
    )


def test_save_and_load_via_file(tmp_path, monkeypatch):
    monkeypatch.setattr(token_store, "keyring", None)
    store = TokenStore(file_path=tmp_path / "tokens.json")

    token = _sample_token()
    store.save(token)

    assert store.file_path.exists()
    loaded = store.load()
    assert loaded == token

    persisted = json.loads(store.file_path.read_text())
    assert persisted["access_token"] == "access"


def test_prefers_keyring_when_available(tmp_path, monkeypatch):
    dummy = DummyKeyring()
    monkeypatch.setattr(token_store, "keyring", dummy)
    store = TokenStore(file_path=tmp_path / "tokens.json", service_name="svc")

    token = _sample_token()
    store.save(token)

    assert not store.file_path.exists()
    assert dummy.storage[("svc", "tokens")]
    loaded = store.load()
    assert loaded == token


def test_clear_removes_keyring_and_file(tmp_path, monkeypatch):
    dummy = DummyKeyring()
    monkeypatch.setattr(token_store, "keyring", dummy)
    store = TokenStore(file_path=tmp_path / "tokens.json", service_name="svc")

    token = _sample_token()
    store.save(token)
    store.file_path.write_text("{}", encoding="utf-8")

    store.clear()

    assert dummy.storage == {}
    assert not store.file_path.exists()
