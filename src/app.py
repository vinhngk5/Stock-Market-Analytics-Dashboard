from datetime import date, timedelta

import plotly.graph_objects as go
import streamlit as st

from database.repository import StockRepository
from service.analytics_service import AnalyticsService
from service.ingestion_service import IngestionService

st.set_page_config(
    page_title="Stock Market Analytics",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Stock Market Analytics Dashboard")
st.caption(
    "End-to-end portfolio project: Yahoo Finance → PostgreSQL → Analytics → Streamlit"
)

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"]
DEFAULT_START = date.today() - timedelta(days=365)


@st.cache_resource
def get_services():
    repository = StockRepository()
    return repository, IngestionService(repository=repository), AnalyticsService()


repository, ingestion_service, analytics = get_services()

st.sidebar.header("Filters")
ticker = st.sidebar.selectbox("Ticker", TICKERS)
start_date = st.sidebar.date_input("Start date", DEFAULT_START)
end_date = st.sidebar.date_input("End date", date.today())

if start_date >= end_date:
    st.error("Start date must be earlier than end date.")
    st.stop()

if st.sidebar.button("Load / refresh data", type="primary"):
    with st.spinner(f"Downloading {ticker} data and updating PostgreSQL..."):
        try:
            count = ingestion_service.ingest(
                ticker, start_date, end_date + timedelta(days=1)
            )
            st.sidebar.success(f"Loaded {count} rows for {ticker}.")
        except Exception as exc:
            st.sidebar.error(f"Data load failed: {exc}")

try:
    data = repository.get_prices(ticker, start_date, end_date)
except Exception as exc:
    st.error(f"Database query failed: {exc}")
    st.stop()

if data.empty:
    st.info("No data in PostgreSQL for this selection. Click 'Load / refresh data'.")
    st.stop()

data = analytics.add_indicators(data)
metrics = analytics.latest_metrics(data)

st.header("Overview")
col1, col2, col3 = st.columns(3)
col1.metric(
    "Current Price",
    f"${metrics['current_price']:,.2f}"
    if metrics["current_price"] is not None
    else "—",
)
col2.metric(
    "Daily Return",
    f"{metrics['daily_return']:.2f}%" if metrics["daily_return"] is not None else "—",
)
col3.metric(
    "Volume", f"{metrics['volume']:,}" if metrics["volume"] is not None else "—"
)

st.divider()

st.subheader("Price Trend")
fig_price = go.Figure()
fig_price.add_trace(
    go.Scatter(x=data.index, y=data["close"], name="Close", mode="lines")
)
fig_price.update_layout(xaxis_title="Date", yaxis_title="Price", hovermode="x unified")
st.plotly_chart(fig_price, use_container_width=True)

st.subheader("Trading Volume")
fig_volume = go.Figure()
fig_volume.add_trace(go.Bar(x=data.index, y=data["volume"], name="Volume"))
fig_volume.update_layout(xaxis_title="Date", yaxis_title="Volume")
st.plotly_chart(fig_volume, use_container_width=True)

st.subheader("Candlestick Chart")
fig_candle = go.Figure(
    data=[
        go.Candlestick(
            x=data.index,
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            name=ticker,
        )
    ]
)
fig_candle.update_layout(
    xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=False
)
st.plotly_chart(fig_candle, use_container_width=True)

st.subheader("Moving Average")
fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=data.index, y=data["close"], name="Close", mode="lines"))
fig_ma.add_trace(
    go.Scatter(x=data.index, y=data["moving_average"], name="20-day MA", mode="lines")
)
fig_ma.update_layout(xaxis_title="Date", yaxis_title="Price", hovermode="x unified")
st.plotly_chart(fig_ma, use_container_width=True)

with st.expander("Raw data"):
    st.dataframe(data.sort_index(ascending=False), use_container_width=True)
