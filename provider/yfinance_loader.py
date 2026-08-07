import yfinance as yf


class YfinanceLoader():
    """Wrapper for downloading historical market data from Yahoo Finance."""

    def download_history(self, ticker, start, end):
        data = yf.download(ticker, start=start, end=end)

        if data.empty:
            raise ValueError(f"No data found for ticker '{ticker}'")

        return data