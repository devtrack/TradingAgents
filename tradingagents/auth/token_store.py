"""Utilities for securely persisting authentication tokens."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

try:
    import keyring  # type: ignore
except Exception:  # pragma: no cover - keyring may not be installed
    keyring = None

from .exceptions import TokenStorageError
from .models import TokenSet


class TokenStore:
    """Persists token data using the system keyring or a local file."""

    def __init__(self, *, service_name: str = "tradingagents-auth", file_path: Optional[Path] = None) -> None:
        self.service_name = service_name
        self.file_path = file_path or Path.home() / ".tradingagents" / "auth_tokens.json"

    def _load_from_keyring(self) -> Optional[TokenSet]:
        if keyring is None:
            return None
        serialized = keyring.get_password(self.service_name, "tokens")
        if not serialized:
            return None
        return self._deserialize(serialized)

    def _save_to_keyring(self, token_set: TokenSet) -> bool:
        if keyring is None:
            return False
        serialized = self._serialize(token_set)
        keyring.set_password(self.service_name, "tokens", serialized)
        return True

    def _serialize(self, token_set: TokenSet) -> str:
        payload = {
            "access_token": token_set.access_token,
            "refresh_token": token_set.refresh_token,
            "token_type": token_set.token_type,
            "scope": token_set.scope,
            "expires_at": token_set.expires_at.isoformat(),
        }
        return json.dumps(payload)

    def _deserialize(self, serialized: str) -> TokenSet:
        data = json.loads(serialized)
        from datetime import datetime

        expires_at = datetime.fromisoformat(data["expires_at"])
        return TokenSet(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type", "bearer"),
            scope=data.get("scope"),
            expires_at=expires_at,
        )

    def load(self) -> Optional[TokenSet]:
        """Load tokens from the most secure available backend."""

        try:
            token_set = self._load_from_keyring()
            if token_set:
                return token_set

            if self.file_path.exists():
                serialized = self.file_path.read_text(encoding="utf-8")
                return self._deserialize(serialized)
        except Exception as exc:  # pragma: no cover - safeguard
            raise TokenStorageError("Unable to load authentication tokens") from exc
        return None

    def save(self, token_set: TokenSet) -> None:
        """Persist the provided token set."""

        try:
            if self._save_to_keyring(token_set):
                return

            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            serialized = self._serialize(token_set)
            self.file_path.write_text(serialized, encoding="utf-8")
            os.chmod(self.file_path, 0o600)
        except Exception as exc:  # pragma: no cover - safeguard
            raise TokenStorageError("Unable to persist authentication tokens") from exc

    def clear(self) -> None:
        """Remove any cached tokens."""

        try:
            if keyring is not None:
                try:
                    keyring.delete_password(self.service_name, "tokens")
                except keyring.errors.PasswordDeleteError:
                    pass

            if self.file_path.exists():
                self.file_path.unlink()
        except Exception as exc:  # pragma: no cover - safeguard
            raise TokenStorageError("Unable to clear persisted authentication tokens") from exc
