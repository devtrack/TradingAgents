import tradingagents.default_config as default_config
from typing import Dict, Optional

# Use default config but allow it to be overridden
_config: Optional[Dict] = None
DATA_DIR: Optional[str] = None
FINANCIAL_DATA_PROVIDER: Optional[str] = None


def initialize_config():
    """Initialize the configuration with default values."""
    global _config, DATA_DIR, FINANCIAL_DATA_PROVIDER
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
        DATA_DIR = _config["data_dir"]
        FINANCIAL_DATA_PROVIDER = _config.get("financial_data_provider", "finnhub")


def set_config(config: Dict):
    """Update the configuration with custom values."""
    global _config, DATA_DIR, FINANCIAL_DATA_PROVIDER
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
    _config.update(config)
    DATA_DIR = _config["data_dir"]
    FINANCIAL_DATA_PROVIDER = _config.get("financial_data_provider", "finnhub")


def get_config() -> Dict:
    """Get the current configuration."""
    if _config is None:
        initialize_config()
    return _config.copy()


def get_financial_data_provider() -> str:
    """Return the selected financial data provider."""
    if _config is None:
        initialize_config()
    return _config.get("financial_data_provider", "finnhub")


# Initialize with default config
initialize_config()
