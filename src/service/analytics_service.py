from __future__ import annotations

import pandas as pd


class AnalyticsService:
    """Calculations used by the dashboard."""

    @staticmethod
    def add_indicators(data: pd.DataFrame, moving_average_window: int = 20) -> pd.DataFrame:
        if data.empty:
            return data.copy()

        result = data.copy()
        result["daily_return"] = result["close"].pct_change()
        result["moving_average"] = result["close"].rolling(moving_average_window).mean()
        return result

    @staticmethod
    def latest_metrics(data: pd.DataFrame) -> dict[str, float | int | None]:
        if data.empty:
            return {
                "current_price": None,
                "daily_return": None,
                "volume": None,
            }

        latest = data.iloc[-1]
        return {
            "current_price": float(latest["close"]),
            "daily_return": float(latest["daily_return"] * 100)
            if pd.notna(latest["daily_return"])
            else None,
            "volume": int(latest["volume"]) if pd.notna(latest["volume"]) else None,
        }
