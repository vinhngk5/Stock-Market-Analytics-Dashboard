from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import yfinance as yf


class YfinanceLoader:
    """Wrapper around Yahoo Finance market-data access."""

    def download_history(self, ticker: str, start: date, end: date) -> pd.DataFrame:
        ticker = ticker.upper().strip()
        data = yf.download(
            ticker,
            start=start,
            end=end,
            auto_adjust=False,
            progress=False,
            actions=False,
        )

        if data.empty:
            raise ValueError(f"No historical data found for ticker '{ticker}'")

        # Recent yfinance versions may return MultiIndex columns even for one ticker.
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        required = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        missing = [column for column in required if column not in data.columns]
        if missing:
            raise ValueError(f"Missing columns from Yahoo Finance: {missing}")

        data = data[required].copy()
        data.index = pd.to_datetime(data.index).tz_localize(None)
        data = data[~data.index.duplicated(keep="last")].sort_index()
        data.dropna(subset=["Open", "High", "Low", "Close"], inplace=True)
        return data

    def get_metadata(self, ticker: str) -> dict[str, Any]:
        info = yf.Ticker(ticker.upper().strip()).info
        return {
            "company_name": info.get("longName") or info.get("shortName"),
            "exchange": info.get("exchange"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
        }
