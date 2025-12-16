from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import questionary
from rich.console import Console

from tradingagents.auth import AuthClient, AuthenticationError

from cli.models import AnalystType


console = Console()

ANALYST_ORDER = [
    ("Market Analyst", AnalystType.MARKET),
    ("Social Media Analyst", AnalystType.SOCIAL),
    ("News Analyst", AnalystType.NEWS),
    ("Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


@dataclass
class ModelInfo:
    id: str
    display_name: str
    capabilities: set[str]


@dataclass
class ProviderInfo:
    id: str
    display_name: str
    base_url: Optional[str]
    models: List[ModelInfo]


def _normalize_capabilities(raw_caps) -> set[str]:
    if isinstance(raw_caps, str):
        return {raw_caps.lower()}
    if isinstance(raw_caps, (list, tuple, set)):
        return {str(cap).lower() for cap in raw_caps if cap}
    return set()


def _parse_providers(payload: dict) -> List[ProviderInfo]:
    providers: List[ProviderInfo] = []
    for provider in payload.get("providers", []):
        provider_id = provider.get("id") or provider.get("provider") or provider.get("name")
        if not provider_id:
            continue
        display_name = provider.get("display_name") or provider.get("name") or provider_id
        base_url = provider.get("base_url") or provider.get("url")
        models: List[ModelInfo] = []
        for model in provider.get("models", []):
            if isinstance(model, str):
                models.append(
                    ModelInfo(
                        id=model,
                        display_name=model,
                        capabilities={"quick", "deep"},
                    )
                )
                continue
            model_id = model.get("id") or model.get("model")
            if not model_id:
                continue
            display = model.get("display_name") or model.get("name") or model_id
            capabilities = _normalize_capabilities(
                model.get("capabilities") or model.get("tags") or []
            )
            capabilities = capabilities or {"quick", "deep"}
            models.append(
                ModelInfo(id=model_id, display_name=display, capabilities=capabilities)
            )

        providers.append(
            ProviderInfo(
                id=provider_id,
                display_name=display_name,
                base_url=base_url,
                models=models,
            )
        )
    return providers


def load_model_catalog(auth_client: Optional[AuthClient] = None) -> List[ProviderInfo]:
    """Fetch the model catalog from the auth service."""

    client = auth_client or AuthClient()
    try:
        payload = client.discover_models()
    except AuthenticationError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise AuthenticationError(f"Unexpected error while fetching models: {exc}")

    providers = _parse_providers(payload or {})
    if not providers:
        raise AuthenticationError("Model discovery returned no providers.")
    return providers


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "Enter the ticker symbol to analyze:",
        validate=lambda x: len(x.strip()) > 0 or "Please enter a valid ticker symbol.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]No ticker symbol provided. Exiting...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "Enter the analysis date (YYYY-MM-DD):",
        validate=lambda x: validate_date(x.strip())
        or "Please enter a valid date in YYYY-MM-DD format.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]No date provided. Exiting...[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        "Select Your [Analysts Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- Press Space to select/unselect analysts\n- Press 'a' to select/unselect all\n- Press Enter when done",
        validate=lambda x: len(x) > 0 or "You must select at least one analyst.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("Shallow - Quick research, few debate and strategy discussion rounds", 1),
        ("Medium - Middle ground, moderate debate rounds and strategy discussion", 3),
        ("Deep - Comprehensive research, in depth debate and strategy discussion", 5),
    ]

    choice = questionary.select(
        "Select Your [Research Depth]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No research depth selected. Exiting...[/red]")
        exit(1)

    return choice


def _filter_models_by_capability(provider: ProviderInfo, capability: str) -> List[ModelInfo]:
    filtered = [model for model in provider.models if capability in model.capabilities]
    return filtered or provider.models


def select_shallow_thinking_agent(provider: ProviderInfo) -> str:
    """Select shallow thinking llm engine using an interactive selection."""

    models = _filter_models_by_capability(provider, "quick")
    choice = questionary.select(
        "Select Your [Quick-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(model.display_name, value=model.id) for model in models
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No shallow thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice


def select_deep_thinking_agent(provider: ProviderInfo) -> str:
    """Select deep thinking llm engine using an interactive selection."""

    models = _filter_models_by_capability(provider, "deep")
    choice = questionary.select(
        "Select Your [Deep-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(model.display_name, value=model.id) for model in models
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice


def select_llm_provider(providers: List[ProviderInfo]) -> ProviderInfo:
    """Select the LLM provider using interactive selection from model discovery."""

    choice = questionary.select(
        "Select your LLM Provider:",
        choices=[
            questionary.Choice(provider.display_name, value=provider)
            for provider in providers
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]no LLM backend selected. Exiting...[/red]")
        exit(1)

    return choice
