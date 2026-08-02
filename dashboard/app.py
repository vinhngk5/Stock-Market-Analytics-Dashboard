import streamlit as st

st.set_page_config(
    page_title="Stock Market Analytics",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Stock Market Analytics Dashboard")
st.caption("Portfolio Project")

st.divider()

st.sidebar.header("Filters")

ticker = st.sidebar.selectbox(
    "Ticker",
    ["AAPL", "MSFT", "GOOGL"]
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=()
)

st.header("Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Current Price", "--")
col2.metric("Daily Return", "--")
col3.metric("Volume", "--")
col4.metric("Market Cap", "--")

st.divider()

st.subheader("Price Trend")

st.info("Price chart will be displayed here.")

st.subheader("Trading Volume")

st.info("Volume chart will be displayed here.")

st.subheader("Candlestick Chart")

st.info("Candlestick chart will be displayed here.")

st.subheader("Moving Average")

st.info("Moving Average chart will be displayed here.")