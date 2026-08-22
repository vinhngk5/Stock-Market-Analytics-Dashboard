from __future__ import annotations

from datetime import date

from database.repository import StockRepository
from provider.yfinance_loader import YfinanceLoader


class IngestionService:
    """Extract -> validate -> load market data into PostgreSQL."""

    def __init__(self, loader: YfinanceLoader | None = None, repository: StockRepository | None = None):
        self.loader = loader or YfinanceLoader()
        self.repository = repository or StockRepository()

    def ingest(self, symbol: str, start: date, end: date) -> int:
        symbol = symbol.upper().strip()
        if start >= end:
            raise ValueError("Start date must be earlier than end date")

        data = self.loader.download_history(symbol, start, end)
        metadata = self.loader.get_metadata(symbol)
        self.repository.upsert_stock(symbol, metadata)
        return self.repository.upsert_prices(symbol, data)
