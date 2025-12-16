import os

from tradingagents.auth.session_cache import load_session_config


_SESSION_OVERRIDES = load_session_config()

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": _SESSION_OVERRIDES.get("llm_provider", "openai"),
    "deep_think_llm": _SESSION_OVERRIDES.get("deep_think_llm", "o4-mini"),
    "quick_think_llm": _SESSION_OVERRIDES.get("quick_think_llm", "gpt-4o-mini"),
    "backend_url": _SESSION_OVERRIDES.get(
        "backend_url", "https://api.openai.com/v1"
    ),
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
    "financial_data_provider": "fmp",
}
