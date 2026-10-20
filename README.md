# Stock Market Analytics Dashboard

An end-to-end market dashboard built with Streamlit, PostgreSQL, and Yahoo Finance data.

## Run

```bash
docker compose up --build
```

Open [http://localhost:8501](http://localhost:8501). PostgreSQL is initialized from `src/database/init.sql`; the application also creates the realtime table on startup so an existing `pg_data` volume can be upgraded without deleting stored data.

## Market data

- Historical daily bars are loaded for the selected ticker and date range using **Sync daily history**.
- A background `yfinance.live.WebSocket` subscribes to the dashboard watchlist and writes timestamped quotes to PostgreSQL. The live panel refreshes every three seconds and reconnects when the stream drops.
- Yahoo Finance stream availability and quote timing depend on Yahoo's service and market hours. This community-maintained yfinance integration is intended for research and personal use; it is not an exchange-grade feed.

## Forecast

The dashboard fits an autoregressive linear regression to daily log returns and projects five business days. Its reported mean absolute error is measured with an expanding, walk-forward holdout. Forecasts are estimates for exploration, not investment advice.
