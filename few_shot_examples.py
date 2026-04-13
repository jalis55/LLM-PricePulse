FEW_SHOT_EXAMPLES = [
    {
        "name": "recent instrument prices",
        "keywords": ["last", "recent", "closing price", "close price", "price history", "company", "instrument"],
        "example": """User: Show me the closing price of ACI for the last 7 days
SQL:
SELECT
    date,
    inst_code,
    close
FROM price_file_data
WHERE UPPER(inst_code) = UPPER('ACI')
ORDER BY date DESC
LIMIT 7;""",
    },
    {
        "name": "lowercase company name",
        "keywords": ["company", "lowercase", "price of company", "last 30 days price"],
        "example": """User: last 30 days price of company besthldng
SQL:
SELECT
    date,
    inst_code,
    open,
    high,
    low,
    close,
    ltp
FROM price_file_data
WHERE UPPER(inst_code) = UPPER('besthldng')
ORDER BY date DESC
LIMIT 30;""",
    },
    {
        "name": "contains wildcard match",
        "keywords": ["wildcard", "contains", "partial", "pattern", "like"],
        "example": """User: show last 30 days price for companies containing best
SQL:
SELECT
    date,
    inst_code,
    open,
    high,
    low,
    close,
    ltp
FROM price_file_data
WHERE inst_code ILIKE '%best%'
ORDER BY date DESC;""",
    },
    {
        "name": "starts with wildcard match",
        "keywords": ["starts with", "beginning with", "prefix"],
        "example": """User: show all companies starting with bex
SQL:
SELECT DISTINCT
    inst_code
FROM price_file_data
WHERE inst_code ILIKE 'bex%'
ORDER BY inst_code;""",
    },
    {
        "name": "ends with wildcard match",
        "keywords": ["ends with", "suffix"],
        "example": """User: show all companies ending with holding
SQL:
SELECT DISTINCT
    inst_code
FROM price_file_data
WHERE inst_code ILIKE '%holding'
ORDER BY inst_code;""",
    },
    {
        "name": "price on a date",
        "keywords": ["on date", "specific date", "on 2024", "on 2023", "on 2022"],
        "example": """User: show me the open, high, low, close of ACI on 2024-01-01
SQL:
SELECT
    date,
    inst_code,
    open,
    high,
    low,
    close
FROM price_file_data
WHERE date = '2024-01-01'
  AND UPPER(inst_code) = UPPER('ACI');""",
    },
    {
        "name": "date range for one instrument",
        "keywords": ["between", "date range", "from 202", "to 202"],
        "example": """User: show close price of ACI from 2024-01-01 to 2024-01-31
SQL:
SELECT
    date,
    inst_code,
    close
FROM price_file_data
WHERE UPPER(inst_code) = UPPER('ACI')
  AND date BETWEEN '2024-01-01' AND '2024-01-31'
ORDER BY date;""",
    },
    {
        "name": "latest trading day snapshot",
        "keywords": ["latest day", "latest trading day", "most recent date", "latest snapshot"],
        "example": """User: show all instruments with close price on the latest trading day
SQL:
SELECT
    date,
    inst_code,
    close
FROM price_file_data
WHERE date = (SELECT MAX(date) FROM price_file_data)
ORDER BY inst_code;""",
    },
    {
        "name": "previous day comparison",
        "keywords": ["previous day", "increase", "decrease", "comparison", "change", "summary"],
        "example": """User: last 14 days trade summary with total trade, volume, value, increase/decrease than the previous day
SQL:
WITH daily_summary AS (
    SELECT
        date,
        SUM(trade) AS total_trade,
        SUM(volume) AS total_volume,
        SUM(value) AS total_value
    FROM price_file_data
    GROUP BY date
),
last_14_days AS (
    SELECT *
    FROM daily_summary
    ORDER BY date DESC
    LIMIT 14
)
SELECT
    date,
    total_trade,
    total_volume,
    total_value,
    total_trade - LAG(total_trade) OVER (ORDER BY date) AS trade_change,
    total_volume - LAG(total_volume) OVER (ORDER BY date) AS volume_change,
    total_value - LAG(total_value) OVER (ORDER BY date) AS value_change
FROM (
    SELECT *
    FROM last_14_days
    ORDER BY date
) t
ORDER BY date DESC;""",
    },
    {
        "name": "daily market summary",
        "keywords": ["market summary", "daily summary", "total trade", "total volume", "total value"],
        "example": """User: show daily market summary for the last 30 days
SQL:
SELECT
    date,
    SUM(trade) AS total_trade,
    SUM(volume) AS total_volume,
    SUM(value) AS total_value
FROM price_file_data
GROUP BY date
ORDER BY date DESC
LIMIT 30;""",
    },
    {
        "name": "moving average",
        "keywords": ["moving average", "rolling", "average", "running average"],
        "example": """User: show 7 day moving average of close price for ACI
SQL:
SELECT
    date,
    inst_code,
    close,
    AVG(close) OVER (
        PARTITION BY inst_code
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7
FROM price_file_data
WHERE UPPER(inst_code) = UPPER('ACI')
ORDER BY date;""",
    },
    {
        "name": "running total",
        "keywords": ["running total", "cumulative", "cumulative volume", "cumulative trade"],
        "example": """User: show cumulative volume for ACI by date
SQL:
SELECT
    date,
    inst_code,
    volume,
    SUM(volume) OVER (
        PARTITION BY inst_code
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_volume
FROM price_file_data
WHERE UPPER(inst_code) = UPPER('ACI')
ORDER BY date;""",
    },
    {
        "name": "lag previous close",
        "keywords": ["previous close", "previous day close", "lag", "day before"],
        "example": """User: show close price and previous day close for ACI
SQL:
SELECT
    date,
    inst_code,
    close,
    LAG(close) OVER (
        PARTITION BY inst_code
        ORDER BY date
    ) AS previous_close
FROM price_file_data
WHERE UPPER(inst_code) = UPPER('ACI')
ORDER BY date;""",
    },
    {
        "name": "day over day percentage change",
        "keywords": ["percent change", "percentage change", "day over day", "daily return"],
        "example": """User: show daily percentage change in close price for ACI
SQL:
SELECT
    date,
    inst_code,
    close,
    ROUND(
        (
            (close - LAG(close) OVER (PARTITION BY inst_code ORDER BY date))
            / NULLIF(LAG(close) OVER (PARTITION BY inst_code ORDER BY date), 0)
        ) * 100,
        2
    ) AS pct_change
FROM price_file_data
WHERE UPPER(inst_code) = UPPER('ACI')
ORDER BY date;""",
    },
    {
        "name": "top by aggregate",
        "keywords": ["top", "highest", "lowest", "best", "worst", "top 5", "top 10"],
        "example": """User: top 5 instruments by average close price
SQL:
SELECT
    inst_code,
    AVG(close) AS avg_close
FROM price_file_data
GROUP BY inst_code
ORDER BY avg_close DESC
LIMIT 5;""",
    },
    {
        "name": "top by date",
        "keywords": ["top gainer", "top loser", "highest volume on date", "highest trade on date"],
        "example": """User: top 10 instruments by volume on 2024-01-01
SQL:
SELECT
    inst_code,
    volume
FROM price_file_data
WHERE date = '2024-01-01'
ORDER BY volume DESC, inst_code
LIMIT 10;""",
    },
    {
        "name": "ranking",
        "keywords": ["rank", "ranking", "row number", "dense rank"],
        "example": """User: rank instruments by volume on 2024-01-01
SQL:
SELECT
    inst_code,
    volume,
    RANK() OVER (ORDER BY volume DESC) AS volume_rank
FROM price_file_data
WHERE date = '2024-01-01'
ORDER BY volume_rank, inst_code;""",
    },
    {
        "name": "nth highest per day",
        "keywords": ["nth", "second highest", "third highest", "per day rank"],
        "example": """User: show the second highest volume instrument for each date
SQL:
WITH ranked AS (
    SELECT
        date,
        inst_code,
        volume,
        ROW_NUMBER() OVER (
            PARTITION BY date
            ORDER BY volume DESC
        ) AS rn
    FROM price_file_data
)
SELECT
    date,
    inst_code,
    volume
FROM ranked
WHERE rn = 2
ORDER BY date;""",
    },
    {
        "name": "max per instrument",
        "keywords": ["highest close", "max close", "maximum close", "peak close"],
        "example": """User: show highest close price for each instrument
SQL:
SELECT
    inst_code,
    MAX(close) AS highest_close
FROM price_file_data
GROUP BY inst_code
ORDER BY highest_close DESC;""",
    },
    {
        "name": "latest row per instrument",
        "keywords": ["latest for each instrument", "most recent for each instrument", "latest row per instrument"],
        "example": """User: show the latest close price for each instrument
SQL:
WITH ranked AS (
    SELECT
        date,
        inst_code,
        close,
        ROW_NUMBER() OVER (
            PARTITION BY inst_code
            ORDER BY date DESC
        ) AS rn
    FROM price_file_data
)
SELECT
    date,
    inst_code,
    close
FROM ranked
WHERE rn = 1
ORDER BY inst_code;""",
    },
    {
        "name": "count trading days",
        "keywords": ["count days", "number of trading days", "how many days"],
        "example": """User: how many trading days are there for each instrument
SQL:
SELECT
    inst_code,
    COUNT(*) AS trading_days
FROM price_file_data
GROUP BY inst_code
ORDER BY trading_days DESC, inst_code;""",
    },
    {
        "name": "average metrics by instrument",
        "keywords": ["average volume", "average trade", "average value"],
        "example": """User: show average volume and average trade for each instrument
SQL:
SELECT
    inst_code,
    AVG(volume) AS avg_volume,
    AVG(trade) AS avg_trade
FROM price_file_data
GROUP BY inst_code
ORDER BY avg_volume DESC;""",
    },
    {
        "name": "monthly aggregate",
        "keywords": ["monthly", "per month", "month wise", "month-wise"],
        "example": """User: show monthly total trade and volume for 2024
SQL:
SELECT
    DATE_TRUNC('month', date)::date AS month_start,
    SUM(trade) AS total_trade,
    SUM(volume) AS total_volume
FROM price_file_data
WHERE date >= '2024-01-01' AND date < '2025-01-01'
GROUP BY DATE_TRUNC('month', date)::date
ORDER BY month_start;""",
    },
    {
        "name": "weekly aggregate",
        "keywords": ["weekly", "per week", "week wise", "week-wise"],
        "example": """User: show weekly total value for the last 12 weeks
SQL:
SELECT
    DATE_TRUNC('week', date)::date AS week_start,
    SUM(value) AS total_value
FROM price_file_data
GROUP BY DATE_TRUNC('week', date)::date
ORDER BY week_start DESC
LIMIT 12;""",
    },
    {
        "name": "volatility proxy",
        "keywords": ["volatility", "high low spread", "spread"],
        "example": """User: show average daily high low spread for each instrument
SQL:
SELECT
    inst_code,
    AVG(high - low) AS avg_spread
FROM price_file_data
GROUP BY inst_code
ORDER BY avg_spread DESC;""",
    },
    {
        "name": "gain loss streak",
        "keywords": ["streak", "consecutive", "gain streak", "loss streak"],
        "example": """User: show whether ACI had an up day or down day each trading day
SQL:
SELECT
    date,
    inst_code,
    close,
    LAG(close) OVER (
        PARTITION BY inst_code
        ORDER BY date
    ) AS previous_close,
    CASE
        WHEN close > LAG(close) OVER (PARTITION BY inst_code ORDER BY date) THEN 'up'
        WHEN close < LAG(close) OVER (PARTITION BY inst_code ORDER BY date) THEN 'down'
        ELSE 'flat'
    END AS day_direction
FROM price_file_data
WHERE UPPER(inst_code) = UPPER('ACI')
ORDER BY date;""",
    },
    {
        "name": "instrument filter by threshold",
        "keywords": ["greater than", "less than", "more than", "above", "below"],
        "example": """User: show instruments where close price was above 100 on 2024-01-01
SQL:
SELECT
    date,
    inst_code,
    close
FROM price_file_data
WHERE date = '2024-01-01'
  AND close > 100
ORDER BY close DESC, inst_code;""",
    },
    {
        "name": "multi instrument comparison",
        "keywords": ["compare", "versus", "vs", "among"],
        "example": """User: compare close price of ACI and BEXIMCO for the last 10 days
SQL:
SELECT
    date,
    inst_code,
    close
FROM price_file_data
WHERE UPPER(inst_code) IN (UPPER('ACI'), UPPER('BEXIMCO'))
ORDER BY date DESC, inst_code
LIMIT 20;""",
    },
]
