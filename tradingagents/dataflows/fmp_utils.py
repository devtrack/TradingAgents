"""Utility functions for fetching data from the Financial Modeling Prep (FMP) API."""

from __future__ import annotations

import os
from typing import Dict

import requests

API_BASE = "https://financialmodelingprep.com/api/v3"
FMP_API_KEY = os.getenv("FMP_API_KEY")


def _call_api(endpoint: str, params: Dict) -> Dict:
    """Call an FMP endpoint and return the parsed JSON response."""
    if FMP_API_KEY:
        params["apikey"] = FMP_API_KEY
    response = requests.get(f"{API_BASE}/{endpoint}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_data_in_range(
    ticker: str,
    start_date: str,
    end_date: str,
    data_type: str,
    data_dir: str,
    period: str | None = None,
) -> Dict:
    """Retrieve FMP data in a date range.

    Only ``news_data`` is currently implemented. Unsupported ``data_type`` values
    return an empty dictionary.
    """
    if data_type == "news_data":
        params = {"tickers": ticker, "from": start_date, "to": end_date}
        news = _call_api("stock_news", params)
        return {start_date: news}
    return {}
