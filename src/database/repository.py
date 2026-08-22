from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from database.connection import DatabaseConnection


class StockRepository:
    """Persistence layer for stock metadata and historical prices."""

    def __init__(self, db: DatabaseConnection | None = None):
        self.db = db or DatabaseConnection()

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
