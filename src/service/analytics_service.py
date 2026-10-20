from __future__ import annotations

import numpy as np
import pandas as pd


class AnalyticsService:
    """Calculations used by the dashboard."""

    @staticmethod
    def add_indicators(
        data: pd.DataFrame, moving_average_window: int = 20
    ) -> pd.DataFrame:
        if data.empty:
            return data.copy()

        result = data.copy()
        result["daily_return"] = result["close"].pct_change()
        result["moving_average"] = result["close"].rolling(moving_average_window).mean()
        price_change = result["close"].diff()
        average_gain = price_change.clip(lower=0).rolling(14).mean()
        average_loss = -price_change.clip(upper=0).rolling(14).mean()
        relative_strength = average_gain / average_loss.replace(0, np.nan)
        result["rsi"] = 100 - (100 / (1 + relative_strength))
        result.loc[(average_loss == 0) & (average_gain > 0), "rsi"] = 100
        result.loc[(average_loss == 0) & (average_gain == 0), "rsi"] = 50
        result["macd"] = result["close"].ewm(span=12, adjust=False).mean() - result[
            "close"
        ].ewm(span=26, adjust=False).mean()
        result["macd_signal"] = result["macd"].ewm(span=9, adjust=False).mean()
        result["volatility_30d"] = (
            result["daily_return"].rolling(30).std() * np.sqrt(252) * 100
        )
        result["drawdown"] = (result["close"] / result["close"].cummax() - 1) * 100
        return result

    @staticmethod
    def latest_metrics(data: pd.DataFrame) -> dict[str, float | int | None]:
        if data.empty:
            return {
                "current_price": None,
                "daily_return": None,
                "volume": None,
                "period_return": None,
                "volatility_30d": None,
                "max_drawdown": None,
                "rsi": None,
                "period_high": None,
                "period_low": None,
            }

        latest = data.iloc[-1]
        closes = pd.to_numeric(data["close"], errors="coerce").dropna()
        return {
            "current_price": float(latest["close"]),
            "daily_return": float(latest["daily_return"] * 100)
            if pd.notna(latest["daily_return"])
            else None,
            "volume": int(latest["volume"]) if pd.notna(latest["volume"]) else None,
            "period_return": float((closes.iloc[-1] / closes.iloc[0] - 1) * 100)
            if len(closes) > 1
            else None,
            "volatility_30d": float(latest["volatility_30d"])
            if pd.notna(latest["volatility_30d"])
            else None,
            "max_drawdown": float(data["drawdown"].min())
            if data["drawdown"].notna().any()
            else None,
            "rsi": float(latest["rsi"]) if pd.notna(latest["rsi"]) else None,
            "period_high": float(closes.max()) if not closes.empty else None,
            "period_low": float(closes.min()) if not closes.empty else None,
        }

    @staticmethod
    def forecast_prices(
        data: pd.DataFrame, horizon: int = 5, lookback: int = 5
    ) -> dict[str, object]:
        prices = pd.to_numeric(data["close"], errors="coerce").dropna()
        prices = prices[prices > 0].to_numpy(dtype=float)
        empty_forecast = pd.DataFrame(columns=["forecast"])
        if horizon < 1 or lookback < 1:
            raise ValueError("Horizon and lookback must be positive")

        log_returns = np.diff(np.log(prices))
        features = np.array(
            [
                log_returns[index - lookback : index]
                for index in range(lookback, len(log_returns))
            ]
        )
        targets = log_returns[lookback:]
        if len(targets) < lookback + 10:
            return {
                "forecast": empty_forecast,
                "mae": None,
                "samples": len(targets),
                "model": "Autoregressive linear regression",
            }

        def fit_predict(
            train_x: np.ndarray, train_y: np.ndarray, sample_x: np.ndarray
        ) -> float:
            center = train_x.mean(axis=0)
            scale = train_x.std(axis=0)
            scale[scale == 0] = 1
            normalized = (train_x - center) / scale
            normalized_sample = (sample_x - center) / scale
            design = np.column_stack((np.ones(len(normalized)), normalized))
            regularizer = np.eye(design.shape[1]) * 1e-4
            regularizer[0, 0] = 0
            coefficients = np.linalg.solve(
                design.T @ design + regularizer, design.T @ train_y
            )
            return float(np.append(1.0, normalized_sample) @ coefficients)

        holdout_size = min(20, max(5, len(targets) // 5))
        first_holdout = len(targets) - holdout_size
        holdout_errors = []
        for sample_index in range(first_holdout, len(targets)):
            predicted_return = fit_predict(
                features[:sample_index], targets[:sample_index], features[sample_index]
            )
            price_index = sample_index + lookback + 1
            predicted_price = prices[price_index - 1] * np.exp(predicted_return)
            holdout_errors.append(abs(predicted_price - prices[price_index]))

        recent_returns = list(log_returns[-lookback:])
        predicted_prices = []
        latest_price = float(prices[-1])
        for _ in range(horizon):
            sample_x = np.asarray(recent_returns[-lookback:], dtype=float)
            predicted_return = fit_predict(features, targets, sample_x)
            latest_price *= float(np.exp(np.clip(predicted_return, -0.2, 0.2)))
            predicted_prices.append(latest_price)
            recent_returns.append(predicted_return)

        last_date = pd.Timestamp(data.index[-1])
        forecast_dates = pd.bdate_range(last_date + pd.offsets.BDay(1), periods=horizon)
        forecast = pd.DataFrame({"forecast": predicted_prices}, index=forecast_dates)
        return {
            "forecast": forecast,
            "mae": float(np.mean(holdout_errors)),
            "samples": len(targets),
            "model": "Autoregressive linear regression",
        }
