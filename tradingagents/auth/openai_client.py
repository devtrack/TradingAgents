"""Factories for OpenAI-compatible clients using the cached session token."""

from __future__ import annotations

from typing import Any, Dict, Optional

from openai import OpenAI

from tradingagents.auth import get_session


def get_openai_kwargs(base_url: Optional[str] = None) -> Dict[str, Any]:
    """Build keyword arguments for OpenAI/ChatOpenAI using the current session."""

    session = get_session()
    headers = {"Authorization": session.as_authorization_header()}
    kwargs: Dict[str, Any] = {
        "api_key": session.access_token,
        "default_headers": headers,
    }
    if base_url:
        kwargs["base_url"] = base_url
    return kwargs


def create_openai_client(base_url: Optional[str] = None) -> OpenAI:
    """Instantiate an OpenAI client authenticated with the cached session."""

    return OpenAI(**get_openai_kwargs(base_url))
