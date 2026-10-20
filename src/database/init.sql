CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR(20) PRIMARY KEY,
    company_name VARCHAR(255),
    exchange VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGSERIAL PRIMARY KEY,

    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,

    open NUMERIC(18, 4),
    high NUMERIC(18, 4),
    low NUMERIC(18, 4),
    close NUMERIC(18, 4),
    adj_close NUMERIC(18, 4),

    volume BIGINT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_stock_prices_stock
        FOREIGN KEY (symbol)
        REFERENCES stocks(symbol),

    CONSTRAINT uq_stock_prices_symbol_date
        UNIQUE (symbol, date)
);


CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol
    ON stock_prices(symbol);

CREATE INDEX IF NOT EXISTS idx_stock_prices_date
    ON stock_prices(date);

CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date
    ON stock_prices(symbol, date);


CREATE TABLE IF NOT EXISTS stock_ticks (
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price NUMERIC(18, 4) NOT NULL,
    day_volume BIGINT,
    bid NUMERIC(18, 4),
    ask NUMERIC(18, 4),
    exchange VARCHAR(50),
    market_hours SMALLINT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_stock_ticks_stock
        FOREIGN KEY (symbol)
        REFERENCES stocks(symbol),
    CONSTRAINT uq_stock_ticks_symbol_timestamp
        UNIQUE (symbol, timestamp)
);


CREATE INDEX IF NOT EXISTS idx_stock_ticks_symbol_timestamp
    ON stock_ticks(symbol, timestamp DESC);