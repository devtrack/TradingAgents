from .finnhub_utils import get_data_in_range as get_data_in_range_finnhub
from .fmp_utils import get_data_in_range as get_data_in_range_fmp
from .config import get_financial_data_provider


def get_data_in_range(*args, **kwargs):
    if get_financial_data_provider() == "fmp":
        return get_data_in_range_fmp(*args, **kwargs)
    return get_data_in_range_finnhub(*args, **kwargs)
from .googlenews_utils import getNewsData
from .yfin_utils import YFinanceUtils
from .reddit_utils import fetch_top_from_category
from .stockstats_utils import StockstatsUtils

from .interface import (
    # News and sentiment functions
    get_finnhub_news,
    get_finnhub_company_insider_sentiment,
    get_finnhub_company_insider_transactions,
    get_google_news,
    get_reddit_global_news,
    get_reddit_company_news,
    # Financial statements functions
    get_simfin_balance_sheet,
    get_simfin_cashflow,
    get_simfin_income_statements,
    # Technical analysis functions
    get_stock_stats_indicators_window,
    get_stockstats_indicator,
    # Market data functions
    get_YFin_data_window,
    get_YFin_data,
)

__all__ = [
    # News and sentiment functions
    "get_finnhub_news",
    "get_finnhub_company_insider_sentiment",
    "get_finnhub_company_insider_transactions",
    "get_google_news",
    "get_reddit_global_news",
    "get_reddit_company_news",
    # Financial statements functions
    "get_simfin_balance_sheet",
    "get_simfin_cashflow",
    "get_simfin_income_statements",
    # Technical analysis functions
    "get_stock_stats_indicators_window",
    "get_stockstats_indicator",
    # Market data functions
    "get_YFin_data_window",
    "get_YFin_data",
]
