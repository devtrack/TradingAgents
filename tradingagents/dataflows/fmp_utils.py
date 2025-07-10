"""Utility functions for fetching data from the Financial Modeling Prep (FMP) API."""

from __future__ import annotations

import os
from typing import Dict

import requests

API_BASE = "https://financialmodelingprep.com/api"
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

    Parameters mirror ``finnhub_utils.get_data_in_range`` but data is fetched
    directly from FMP. Supported ``data_type`` values are ``news_data``,
    ``insider_senti``, ``insider_trans``, ``SEC_filings`` and ``fin_as_reported``.
    Unknown ``data_type`` values return an empty dictionary.
    """

    if data_type == "news_data":
        params = {"tickers": ticker, "from": start_date, "to": end_date}
        news = _call_api("v3/stock_news", params)
        return {start_date: news}

    if data_type == "insider_senti":
        params = {"symbol": ticker, "from": start_date, "to": end_date}
        data = _call_api("v4/insider-sentiments", params)
        return {start_date: data}

    if data_type == "insider_trans":
        params = {"symbol": ticker, "from": start_date, "to": end_date}
        data = _call_api("v4/insider-trading", params)
        return {start_date: data}

    if data_type == "SEC_filings":
        params = {"from": start_date, "to": end_date}
        data = _call_api(f"v3/sec_filings/{ticker}", params)
        return {start_date: data}

    if data_type == "fin_as_reported":
        params = {"from": start_date, "to": end_date}
        if period:
            params["period"] = period
        data = _call_api(f"v3/financial-statement-as-reported/{ticker}", params)
        return {start_date: data}

    return {}
