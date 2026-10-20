from datetime import date, datetime, timedelta, timezone

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from database.repository import StockRepository
from service.analytics_service import AnalyticsService
from service.ingestion_service import IngestionService
from service.realtime_service import RealtimeService

st.set_page_config(page_title="Market Pulse", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root {
        --ink: #17221e;
        --muted: #58675e;
        --paper: #f2f5f1;
        --line: #dce4dc;
        --green: #1d8a5a;
        --lime: #d7f36b;
        --coral: #db6b57;
    }
    .stApp { background: linear-gradient(135deg, #f4f6f2 0%, #edf2ed 100%); color: var(--ink); }
    html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
    [data-testid="stSidebar"] { background: #17221e; }
    [data-testid="stSidebar"] * { color: #eef4ed; }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color: #17221e; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div { background: #f7faf7; border-color: #aebbb0; }
    [data-testid="stSidebar"] [data-testid="stDateInput"] input { background: #f7faf7; color: #17221e; border-color: #aebbb0; }
    [data-testid="stSidebar"] [data-testid="stDateInput"] input::placeholder { color: #59675f; }
    [data-testid="stSidebar"] button[kind="primary"] { background: var(--lime); color: var(--ink); border: 0; }
    [data-testid="stSidebar"] button[kind="primary"] * { color: var(--ink); }
    [data-testid="stMetric"] { background: #ffffff; border: 1px solid var(--line); padding: 16px 18px; border-radius: 6px; }
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: 0.78rem; }
    [data-testid="stMetricValue"] { color: var(--ink); font-family: 'DM Mono', monospace; }
    [data-testid="stMetricDelta"] { font-weight: 700; }
    h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
    [data-testid="stAlert"] { background: #edf3ec; border: 1px solid #cad8c9; color: #20372a; }
    [data-testid="stAlert"] p, [data-testid="stAlert"] [data-testid="stMarkdownContainer"] { color: #20372a !important; }
    [data-baseweb="tab-list"] button { color: #43564a !important; opacity: 1 !important; }
    [data-baseweb="tab-list"] button:not([aria-selected="true"]) p { color: #43564a !important; opacity: 1 !important; }
    [data-baseweb="tab-list"] button[aria-selected="true"] { color: #17221e !important; border-bottom-color: #1d8a5a !important; }
    [data-baseweb="tab-list"] button p { color: inherit !important; }
    [data-testid="stTabs"] [role="tab"], [data-testid="stTabs"] [role="tab"] * { color: #43564a !important; opacity: 1 !important; }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"], [data-testid="stTabs"] [role="tab"][aria-selected="true"] * { color: #17221e !important; }
    .masthead { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); padding: 8px 0 18px; margin-bottom: 22px; }
    .brand { color: var(--ink); font-weight: 800; letter-spacing: 0; font-size: 1rem; }
    .brand-mark { display: inline-grid; place-items: center; background: var(--lime); width: 28px; height: 28px; border-radius: 5px; margin-right: 9px; font-family: 'DM Mono', monospace; }
    .eyebrow { color: var(--muted); font-family: 'DM Mono', monospace; font-size: 0.72rem; }
    .stream-status { font-family: 'DM Mono', monospace; font-size: 0.72rem; font-weight: 500; padding: 6px 9px; border-radius: 4px; background: #e0f2e7; color: #176b46; }
    .stream-status.waiting { background: #f2eddb; color: #8d6a1e; }
    .stream-status.offline { background: #f8e5e1; color: #a94435; }
    .section-label { font-family: 'DM Mono', monospace; color: #59675f; font-size: 0.72rem; text-transform: uppercase; }
    div[data-testid="stPlotlyChart"] { border: 1px solid var(--line); border-radius: 6px; background: white; padding: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"]
DEFAULT_START = date.today() - timedelta(days=365)
CHART_LAYOUT = {
    "template": "plotly_white",
    "paper_bgcolor": "#ffffff",
    "plot_bgcolor": "#ffffff",
    "font": {"family": "Manrope, sans-serif", "color": "#36453b", "size": 11},
    "margin": {"l": 12, "r": 12, "t": 22, "b": 12},
    "hovermode": "x unified",
    "xaxis": {
        "showgrid": False,
        "zeroline": False,
        "tickfont": {"color": "#46554b"},
        "title_font": {"color": "#36453b"},
    },
    "yaxis": {
        "gridcolor": "#e2e9e2",
        "zeroline": False,
        "tickfont": {"color": "#46554b"},
        "title_font": {"color": "#36453b"},
    },
    "legend": {
        "orientation": "h",
        "y": 1.12,
        "x": 0,
        "font": {"color": "#36453b"},
    },
}


@st.cache_resource
def get_services():
    repository = StockRepository()
    return (
        repository,
        IngestionService(repository=repository),
        AnalyticsService(),
        RealtimeService(repository=repository),
    )


repository, ingestion_service, analytics, realtime = get_services()

st.sidebar.markdown("## MARKET PULSE")
st.sidebar.markdown(
    '<span class="eyebrow">LIVE EQUITIES</span>', unsafe_allow_html=True
)
ticker = st.sidebar.selectbox("Ticker", TICKERS)
start_date = st.sidebar.date_input("History from", DEFAULT_START)
end_date = st.sidebar.date_input("Through", date.today())

if start_date >= end_date:
    st.sidebar.error("Start date must be earlier than end date.")
    st.stop()

if st.sidebar.button("Sync daily history", type="primary", width="stretch"):
    with st.spinner(f"Loading {ticker} history..."):
        try:
            count = ingestion_service.ingest(
                ticker, start_date, end_date + timedelta(days=1)
            )
            st.sidebar.success(f"Updated {count} daily rows")
        except Exception as exc:
            st.sidebar.error(f"History sync failed: {exc}")

try:
    realtime.start(TICKERS)
except Exception as exc:
    st.sidebar.error(f"Realtime startup failed: {exc}")

try:
    data = repository.get_prices(ticker, start_date, end_date)
except Exception as exc:
    st.error(f"Database query failed: {exc}")
    st.stop()

if data.empty:
    metrics = analytics.latest_metrics(data)
    forecast_result = {
        "forecast": data,
        "mae": None,
        "samples": 0,
        "model": "Autoregressive linear regression",
    }
else:
    data = analytics.add_indicators(data)
    metrics = analytics.latest_metrics(data)
    forecast_result = analytics.forecast_prices(data)

st.markdown(
    '<div class="masthead"><div class="brand"><span class="brand-mark">M</span>MARKET PULSE</div><div class="eyebrow">EQUITY MONITOR &nbsp; / &nbsp; US MARKETS</div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="section-label">{ticker} &nbsp; / &nbsp; MARKET OVERVIEW</div>',
    unsafe_allow_html=True,
)


@st.fragment(run_every="3s")
def render_live_market(
    symbol: str,
    history: pd.DataFrame,
    history_metrics: dict,
    forecast: pd.DataFrame,
) -> None:
    stream_state = realtime.status_for(symbol)
    tick = stream_state["tick"]
    if tick is None:
        try:
            tick = repository.get_latest_tick(symbol)
        except Exception:
            tick = None

    if tick is not None:
        current_price = float(tick["price"])
        baseline = history_metrics["current_price"]
        daily_change = (
            (current_price / baseline - 1) * 100 if baseline not in (None, 0) else None
        )
        volume = tick.get("day_volume") or history_metrics["volume"]
        last_update = (
            tick["timestamp"].astimezone(timezone.utc).strftime("%H:%M:%S UTC")
        )
    else:
        current_price = history_metrics["current_price"]
        daily_change = history_metrics["daily_return"]
        volume = history_metrics["volume"]
        last_update = "Awaiting first quote"

    state = stream_state["status"]
    status_class = "stream-status"
    if state in ("connecting", "idle"):
        status_class += " waiting"
    elif state == "reconnecting":
        status_class += " offline"
    st.markdown(
        f'<span class="{status_class}">● {state.upper()}</span> &nbsp; <span class="eyebrow">{last_update}</span>',
        unsafe_allow_html=True,
    )

    price_col, change_col, volume_col = st.columns(3)
    price_col.metric(
        "Last price",
        f"${current_price:,.2f}" if current_price is not None else "—",
    )
    change_col.metric(
        "Daily return",
        f"{daily_change:+.2f}%" if daily_change is not None else "—",
    )
    volume_col.metric("Session volume", f"{volume:,}" if volume is not None else "—")

    period_col, volatility_col, drawdown_col, rsi_col = st.columns(4)
    period_col.metric(
        "Period return",
        f"{history_metrics['period_return']:+.2f}%"
        if history_metrics["period_return"] is not None
        else "—",
    )
    volatility_col.metric(
        "30-session volatility",
        f"{history_metrics['volatility_30d']:.1f}%"
        if history_metrics["volatility_30d"] is not None
        else "—",
        help="Annualized standard deviation of daily returns over the last 30 sessions.",
    )
    drawdown_col.metric(
        "Max drawdown",
        f"{history_metrics['max_drawdown']:.2f}%"
        if history_metrics["max_drawdown"] is not None
        else "—",
    )
    rsi_col.metric(
        "RSI · 14",
        f"{history_metrics['rsi']:.1f}"
        if history_metrics["rsi"] is not None
        else "—",
        help="Below 30 is commonly considered oversold; above 70 is commonly considered overbought.",
    )

    left, right = st.columns([1.75, 1])
    with left:
        st.subheader("Price action")
        try:
            live_ticks = repository.get_recent_ticks(
                symbol, datetime.now(timezone.utc) - timedelta(hours=24)
            )
        except Exception:
            live_ticks = history.iloc[0:0]
        intraday_tab, history_tab = st.tabs(["Live · 24h", "Daily · forecast"])
        with intraday_tab:
            if live_ticks.empty:
                st.info("Waiting for the first live quote from Yahoo Finance.")
            else:
                intraday_chart = go.Figure(
                    go.Scatter(
                        x=live_ticks.index,
                        y=live_ticks["price"],
                        name="Live prints",
                        mode="lines",
                        line={"color": "#223cda", "width": 2},
                    )
                )
                intraday_chart.update_layout(
                    **CHART_LAYOUT, height=350, yaxis_title="USD"
                )
                st.plotly_chart(
                    intraday_chart,
                    width="stretch",
                    config={"displayModeBar": False},
                )
        with history_tab:
            daily_chart = go.Figure()
            if not history.empty:
                daily_chart.add_trace(
                    go.Scatter(
                        x=history.index,
                        y=history["close"],
                        name="Daily close",
                        mode="lines",
                        line={"color": "#1d8a5a", "width": 2},
                    )
                )
                daily_chart.add_trace(
                    go.Scatter(
                        x=history.index,
                        y=history["moving_average"],
                        name="20-session average",
                        mode="lines",
                        line={"color": "#d2a841", "width": 1.5, "dash": "dot"},
                    )
                )
            if not forecast.empty:
                daily_chart.add_trace(
                    go.Scatter(
                        x=forecast.index,
                        y=forecast["forecast"],
                        name="Model outlook",
                        mode="lines+markers",
                        line={"color": "#db6b57", "width": 2, "dash": "dash"},
                        marker={"size": 5},
                    )
                )
            daily_chart.update_layout(**CHART_LAYOUT, height=350, yaxis_title="USD")
            st.plotly_chart(
                daily_chart, width="stretch", config={"displayModeBar": False}
            )

    with right:
        st.subheader("Daily volume")
        volume_chart = go.Figure()
        if not history.empty:
            volume_chart.add_trace(
                go.Bar(
                    x=history.index,
                    y=history["volume"],
                    name="Volume",
                    marker_color="#789483",
                    opacity=0.85,
                )
            )
        volume_chart.update_layout(**CHART_LAYOUT, height=390, showlegend=False)
        volume_chart.update_yaxes(title_text="Shares")
        st.plotly_chart(
            volume_chart, width="stretch", config={"displayModeBar": False}
        )


render_live_market(ticker, data, metrics, forecast_result["forecast"])

if not data.empty:
    st.divider()
    st.subheader("Risk & momentum")
    rsi_col, macd_col = st.columns(2)
    with rsi_col:
        rsi_chart = go.Figure()
        rsi_chart.add_trace(
            go.Scatter(
                x=data.index,
                y=data["rsi"],
                name="RSI · 14",
                mode="lines",
                line={"color": "#223cda", "width": 2},
                fill="tozeroy",
                fillcolor="rgba(34,60,218,0.08)",
            )
        )
        rsi_chart.add_hline(y=70, line_dash="dash", line_color="#db6b57")
        rsi_chart.add_hline(y=30, line_dash="dash", line_color="#1d8a5a")
        rsi_chart.update_layout(**CHART_LAYOUT, height=300)
        rsi_chart.update_yaxes(range=[0, 100], title_text="RSI")
        st.plotly_chart(rsi_chart, width="stretch", config={"displayModeBar": False})
    with macd_col:
        macd_chart = go.Figure()
        macd_chart.add_trace(
            go.Scatter(x=data.index, y=data["macd"], name="MACD", mode="lines", line={"color": "#1d8a5a", "width": 2})
        )
        macd_chart.add_trace(
            go.Scatter(x=data.index, y=data["macd_signal"], name="Signal", mode="lines", line={"color": "#db6b57", "width": 1.5})
        )
        macd_chart.update_layout(**CHART_LAYOUT, height=300, yaxis_title="USD")
        st.plotly_chart(macd_chart, width="stretch", config={"displayModeBar": False})

    st.subheader("Return profile")
    return_col, drawdown_chart_col = st.columns(2)
    with return_col:
        return_chart = go.Figure(
            go.Bar(
                x=data.index,
                y=data["daily_return"] * 100,
                name="Daily return",
                marker_color=["#1d8a5a" if value >= 0 else "#db6b57" for value in data["daily_return"].fillna(0)],
            )
        )
        return_chart.add_hline(y=0, line_color="#829087", line_width=1)
        return_chart.update_layout(**CHART_LAYOUT, height=300, yaxis_title="Return %", showlegend=False)
        st.plotly_chart(return_chart, width="stretch", config={"displayModeBar": False})
    with drawdown_chart_col:
        drawdown_chart = go.Figure(
            go.Scatter(
                x=data.index,
                y=data["drawdown"],
                name="Drawdown",
                mode="lines",
                line={"color": "#db6b57", "width": 2},
                fill="tozeroy",
                fillcolor="rgba(219,107,87,0.12)",
            )
        )
        drawdown_chart.update_layout(**CHART_LAYOUT, height=300, yaxis_title="From peak %")
        st.plotly_chart(drawdown_chart, width="stretch", config={"displayModeBar": False})

forecast_col, details_col = st.columns([1, 1])
with forecast_col:
    st.subheader("Five-session model outlook")
    if forecast_result["forecast"].empty:
        st.info("Sync at least 20 daily observations to calculate a forecast.")
    else:
        forecast = forecast_result["forecast"]
        start_price = metrics["current_price"]
        end_price = float(forecast["forecast"].iloc[-1])
        projected_return = (end_price / start_price - 1) * 100
        st.metric(
            "Projected fifth session", f"${end_price:,.2f}", f"{projected_return:+.2f}%"
        )
        mae = forecast_result["mae"]
        st.caption(
            f"{forecast_result['model']} · walk-forward holdout MAE: ${mae:,.2f} · {forecast_result['samples']} training samples"
            if mae is not None
            else forecast_result["model"]
        )
with details_col:
    st.subheader("Historical observations")
    if data.empty:
        st.info("No daily history is stored for this range.")
    else:
        st.dataframe(
            data.sort_index(ascending=False),
            width="stretch",
            height=260,
        )

st.caption(
    "Market data: Yahoo Finance · Forecasts are statistical estimates, not investment advice."
)
