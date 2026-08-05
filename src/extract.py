import datetime
import yfinance as yf


class YfinanceLoader():
    def get_historical(self, ticker):
        end = datetime.date.today()
        start = end - datetime.timedelta(days=365 * 2)
        
        data = yf.download(ticker, start=start, end=end)

        return data