"""Helpers for persisting session-derived configuration preferences."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


_CACHE_PATH = Path.home() / ".tradingagents" / "session_config.json"


def save_session_config(data: Dict[str, Any]) -> None:
    """Persist session configuration overrides next to the token cache."""

    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_session_config() -> Dict[str, Any]:
    """Load cached session configuration overrides if available."""

    if not _CACHE_PATH.exists():
        return {}
    try:
        raw = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(raw, dict):
        return {}
    return raw
