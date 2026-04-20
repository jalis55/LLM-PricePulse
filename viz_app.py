from app import fetch_data


def trade_summary(days: int = 7):
    days = max(1, int(days))
    query = """
    WITH recent_dates AS (
    SELECT DISTINCT date
    FROM price_file_data
    ORDER BY date DESC
    LIMIT {days}
)
    SELECT 
    p.date
    ,sum(p.trade) as total_trade
    ,sum(p.value) as total_value
    ,sum(p.volume) as total_volume

    FROM price_file_data p
    WHERE p.date IN (SELECT date FROM recent_dates)
    group by p.date
    ORDER BY p.date desc;

    """.format(days=days)
    return fetch_data(query)


def top_companies_summary(days: int = 7):
    days = max(1, int(days))
    query = """
    WITH recent_dates AS (
    SELECT DISTINCT date
    FROM price_file_data
    ORDER BY date DESC
    LIMIT {days}
)
    SELECT
    inst_code,
    SUM(trade) AS total_trade,
    SUM(value) AS total_value,
    SUM(volume) AS total_volume
    FROM price_file_data
    WHERE date IN (SELECT date FROM recent_dates)
    GROUP BY inst_code
    ORDER BY inst_code;
    """.format(days=days)
    return fetch_data(query)


def cumulative_trade_summary(days: int = 7):
    days = max(1, int(days))
    query = """
    WITH recent_dates AS (
    SELECT DISTINCT date
    FROM price_file_data
    ORDER BY date DESC
    LIMIT {days}
),
    daily_summary AS (
    SELECT
    p.date,
    SUM(p.trade) AS total_trade,
    SUM(p.value) AS total_value,
    SUM(p.volume) AS total_volume
    FROM price_file_data p
    WHERE p.date IN (SELECT date FROM recent_dates)
    GROUP BY p.date
)
    SELECT
    date,
    SUM(total_trade) OVER (ORDER BY date) AS cumulative_trade,
    SUM(total_value) OVER (ORDER BY date) AS cumulative_value,
    SUM(total_volume) OVER (ORDER BY date) AS cumulative_volume
    FROM daily_summary
    ORDER BY date;
    """.format(days=days)
    return fetch_data(query)


def market_breadth_summary(days: int = 7):
    days = max(2, int(days))
    query = """
    WITH recent_dates AS (
    SELECT DISTINCT date
    FROM price_file_data
    ORDER BY date DESC
    LIMIT {days}
),
    base AS (
    SELECT
    p.date,
    p.inst_code,
    p.close,
    LAG(p.close) OVER (PARTITION BY p.inst_code ORDER BY p.date) AS prev_close
    FROM price_file_data p
    WHERE p.date IN (SELECT date FROM recent_dates)
)
    SELECT
    date,
    COUNT(*) FILTER (WHERE close > prev_close) AS gainers,
    COUNT(*) FILTER (WHERE close < prev_close) AS losers,
    COUNT(*) FILTER (WHERE close = prev_close) AS unchanged
    FROM base
    WHERE prev_close IS NOT NULL
    GROUP BY date
    ORDER BY date;
    """.format(days=days)
    return fetch_data(query)


def top_movers_summary(days: int = 7):
    days = max(2, int(days))
    query = """
    WITH recent_dates AS (
    SELECT DISTINCT date
    FROM price_file_data
    ORDER BY date DESC
    LIMIT {days}
),
    bounds AS (
    SELECT MIN(date) AS start_date, MAX(date) AS end_date
    FROM recent_dates
),
    start_prices AS (
    SELECT DISTINCT ON (inst_code)
    inst_code,
    close AS start_close
    FROM price_file_data
    WHERE date = (SELECT start_date FROM bounds)
    ORDER BY inst_code
),
    end_prices AS (
    SELECT DISTINCT ON (inst_code)
    inst_code,
    close AS end_close
    FROM price_file_data
    WHERE date = (SELECT end_date FROM bounds)
    ORDER BY inst_code
)
    SELECT
    e.inst_code,
    s.start_close,
    e.end_close,
    ROUND(((((e.end_close - s.start_close) / NULLIF(s.start_close, 0)) * 100)::numeric), 2) AS pct_change
    FROM end_prices e
    JOIN start_prices s ON e.inst_code = s.inst_code
    WHERE s.start_close IS NOT NULL
      AND e.end_close IS NOT NULL
    ORDER BY pct_change DESC;
    """.format(days=days)
    return fetch_data(query)
