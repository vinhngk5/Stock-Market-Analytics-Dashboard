from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from database.connection import DatabaseConnection


class StockRepository:
    """Persistence layer for stock metadata and historical prices."""

    def __init__(self, db: DatabaseConnection | None = None):
        self.db = db or DatabaseConnection()

    def ensure_realtime_schema(self) -> None:
        table_query = """
            CREATE TABLE IF NOT EXISTS stock_ticks (
                symbol VARCHAR(20) NOT NULL REFERENCES stocks(symbol),
                timestamp TIMESTAMPTZ NOT NULL,
                price NUMERIC(18, 4) NOT NULL,
                day_volume BIGINT,
                bid NUMERIC(18, 4),
                ask NUMERIC(18, 4),
                exchange VARCHAR(50),
                market_hours SMALLINT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, timestamp)
            )
        """
        index_query = """
            CREATE INDEX IF NOT EXISTS idx_stock_ticks_symbol_timestamp
            ON stock_ticks (symbol, timestamp DESC)
        """
        with self.db.connection.cursor() as cur:
            with self.db.connection.transaction():
                cur.execute(table_query)
                cur.execute(index_query)

    def upsert_tick(self, tick: dict[str, Any]) -> None:
        symbol = str(tick["symbol"]).upper()
        with self.db.connection.cursor() as cur:
            with self.db.connection.transaction():
                cur.execute(
                    "INSERT INTO stocks (symbol) VALUES (%s) ON CONFLICT (symbol) DO NOTHING",
                    (symbol,),
                )
                cur.execute(
                    """
                    INSERT INTO stock_ticks
                        (symbol, timestamp, price, day_volume, bid, ask, exchange, market_hours)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timestamp) DO UPDATE SET
                        price = EXCLUDED.price,
                        day_volume = EXCLUDED.day_volume,
                        bid = EXCLUDED.bid,
                        ask = EXCLUDED.ask,
                        exchange = EXCLUDED.exchange,
                        market_hours = EXCLUDED.market_hours
                    """,
                    (
                        symbol,
                        tick["timestamp"],
                        tick["price"],
                        tick.get("day_volume"),
                        tick.get("bid"),
                        tick.get("ask"),
                        tick.get("exchange"),
                        tick.get("market_hours"),
                    ),
                )

    def get_latest_tick(self, symbol: str) -> dict[str, Any] | None:
        with self.db.connection.cursor() as cur:
            row = cur.execute(
                """
                SELECT timestamp, price, day_volume, bid, ask, exchange, market_hours
                FROM stock_ticks
                WHERE symbol = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (symbol.upper(),),
            ).fetchone()
        if row is None:
            return None
        return dict(
            zip(
                (
                    "timestamp",
                    "price",
                    "day_volume",
                    "bid",
                    "ask",
                    "exchange",
                    "market_hours",
                ),
                row,
            )
        )

    def get_recent_ticks(
        self, symbol: str, since: datetime, limit: int = 500
    ) -> pd.DataFrame:
        with self.db.connection.cursor() as cur:
            rows = cur.execute(
                """
                SELECT timestamp, price, day_volume, bid, ask
                FROM stock_ticks
                WHERE symbol = %s AND timestamp >= %s
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (symbol.upper(), since, limit),
            ).fetchall()
        data = pd.DataFrame(
            rows, columns=["timestamp", "price", "day_volume", "bid", "ask"]
        )
        if not data.empty:
            data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
            data.set_index("timestamp", inplace=True)
            data.sort_index(inplace=True)
        return data

    def upsert_stock(self, symbol: str, metadata: dict[str, Any] | None = None) -> None:
        metadata = metadata or {}
        query = """
            INSERT INTO stocks (symbol, company_name, exchange, sector, industry)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                exchange = EXCLUDED.exchange,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry
        """
        values = (
            symbol.upper(),
            metadata.get("company_name"),
            metadata.get("exchange"),
            metadata.get("sector"),
            metadata.get("industry"),
        )

        with self.db.connection.cursor() as cur:
            with self.db.connection.transaction():
                cur.execute(query, values)

    def upsert_prices(self, symbol: str, data: pd.DataFrame) -> int:
        if data.empty:
            return 0

        rows = []
        for idx, row in data.iterrows():
            rows.append(
                (
                    symbol.upper(),
                    pd.Timestamp(idx).date(),
                    self._number(row.get("Open")),
                    self._number(row.get("High")),
                    self._number(row.get("Low")),
                    self._number(row.get("Close")),
                    self._number(row.get("Adj Close")),
                    self._integer(row.get("Volume")),
                )
            )

        query = """
            INSERT INTO stock_prices
                (symbol, date, open, high, low, close, adj_close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, date) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                adj_close = EXCLUDED.adj_close,
                volume = EXCLUDED.volume
        """

        with self.db.connection.cursor() as cur:
            with self.db.connection.transaction():
                cur.executemany(query, rows)

        return len(rows)

    def get_prices(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
    ) -> pd.DataFrame:
        query = """
            SELECT date, open, high, low, close, adj_close, volume
            FROM stock_prices
            WHERE symbol = %s
        """
        params: list[Any] = [symbol.upper()]

        if start is not None:
            query += " AND date >= %s"
            params.append(start)
        if end is not None:
            query += " AND date <= %s"
            params.append(end)

        query += " ORDER BY date"

        with self.db.connection.cursor() as cur:
            rows = cur.execute(query, params).fetchall()

        columns = ["date", "open", "high", "low", "close", "adj_close", "volume"]
        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
        return df

    @staticmethod
    def _number(value):
        if pd.isna(value):
            return None
        return float(value)

    @staticmethod
    def _integer(value):
        if pd.isna(value):
            return None
        return int(value)
