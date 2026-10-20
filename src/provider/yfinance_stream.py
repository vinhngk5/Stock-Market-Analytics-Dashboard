from __future__ import annotations

from collections.abc import Callable
from typing import Any


class YfinanceStream:
    """Small adapter for yfinance's synchronous live WebSocket client."""

    def listen(
        self, symbols: list[str], message_handler: Callable[[dict[str, Any]], None]
    ) -> None:
        from yfinance.live import WebSocket

        client = WebSocket(verbose=False)
        try:
            client.subscribe(symbols)
            client.listen(message_handler)
        finally:
            client.close()
