from __future__ import annotations

import math
import threading
import time
from datetime import datetime, timezone
from typing import Any

from database.repository import StockRepository
from provider.yfinance_stream import YfinanceStream


class RealtimeService:
    """Maintains one process-wide yfinance stream and persists incoming quotes."""

    def __init__(
        self,
        repository: StockRepository,
        stream: YfinanceStream | None = None,
    ):
        self.repository = repository
        self.stream = stream or YfinanceStream()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._symbols: list[str] = []
        self._latest: dict[str, dict[str, Any]] = {}
        self._status = "idle"
        self._error: str | None = None

    def start(self, symbols: list[str]) -> None:
        normalized = sorted(
            {symbol.upper().strip() for symbol in symbols if symbol.strip()}
        )
        if not normalized:
            raise ValueError("At least one ticker is required")

        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self.repository.ensure_realtime_schema()
            self._symbols = normalized
            self._status = "connecting"
            self._thread = threading.Thread(
                target=self._run, name="yfinance-live-stream", daemon=True
            )
            self._thread.start()

    def status_for(self, symbol: str) -> dict[str, Any]:
        with self._lock:
            return {
                "status": self._status,
                "error": self._error,
                "tick": self._latest.get(symbol.upper()),
            }

    def _run(self) -> None:
        delay = 2
        while True:
            with self._lock:
                self._status = "connecting"
                symbols = list(self._symbols)
            try:
                self.stream.listen(symbols, self._handle_message)
                with self._lock:
                    self._status = "reconnecting"
                    self._error = "Stream disconnected; retrying"
                delay = 2
            except Exception as exc:
                with self._lock:
                    self._status = "reconnecting"
                    self._error = str(exc)
            time.sleep(delay)
            delay = min(delay * 2, 30)

    def _handle_message(self, message: dict[str, Any]) -> None:
        try:
            symbol = str(message["id"]).upper()
            price = float(message["price"])
            timestamp = datetime.fromtimestamp(
                int(message["time"]) / 1000, tz=timezone.utc
            )
            if not math.isfinite(price) or price <= 0 or symbol not in self._symbols:
                return
            tick = {
                "symbol": symbol,
                "timestamp": timestamp,
                "price": price,
                "day_volume": self._optional_int(message.get("day_volume")),
                "bid": self._optional_float(message.get("bid")),
                "ask": self._optional_float(message.get("ask")),
                "exchange": message.get("exchange"),
                "market_hours": self._optional_int(message.get("market_hours")),
            }
            self.repository.upsert_tick(tick)
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            with self._lock:
                self._error = f"Invalid stream message: {exc}"
            return
        except Exception as exc:
            with self._lock:
                self._error = f"Could not persist live quote: {exc}"
            return

        with self._lock:
            self._latest[symbol] = tick
            self._status = "live"
            self._error = None

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        return int(value) if value is not None else None

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        parsed = float(value) if value is not None else None
        return parsed if parsed is None or math.isfinite(parsed) else None
