-- Performance analysis queries (PostgreSQL-style SQL).
-- Assumes stock_data(Date, Open, High, Low, Close, Volume).
-- Purpose: expose reusable trend, return, and performance analysis for BI reporting.

-- 1. Daily performance and moving-average trend layer.
WITH returns AS (
    SELECT
        Date,
        Close,
        Volume,
        LAG(Close) OVER (ORDER BY Date) AS previous_close
    FROM stock_data
), enriched AS (
    SELECT
        Date,
        Close,
        Volume,
        previous_close,
        (Close / NULLIF(previous_close, 0) - 1) * 100 AS daily_return_pct
    FROM returns
)
SELECT
    Date,
    Close,
    Volume,
    ROUND(daily_return_pct, 4) AS daily_return_pct,
    ROUND(AVG(Close) OVER (
        ORDER BY Date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ), 2) AS ma_20,
    ROUND(AVG(Close) OVER (
        ORDER BY Date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
    ), 2) AS ma_50,
    ROUND(AVG(Volume) OVER (
        ORDER BY Date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ), 2) AS avg_volume_20d,
    ROUND(
        Volume / NULLIF(AVG(Volume) OVER (
            ORDER BY Date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ), 0),
        4
    ) AS volume_ratio
FROM enriched
ORDER BY Date;

-- 2. Strongest positive daily-return observations.
WITH returns AS (
    SELECT
        Date,
        Close,
        LAG(Close) OVER (ORDER BY Date) AS previous_close
    FROM stock_data
), ranked AS (
    SELECT
        Date,
        Close,
        (Close / NULLIF(previous_close, 0) - 1) * 100 AS daily_return_pct
    FROM returns
    WHERE previous_close IS NOT NULL
)
SELECT
    Date,
    Close,
    ROUND(daily_return_pct, 4) AS daily_return_pct,
    DENSE_RANK() OVER (ORDER BY daily_return_pct DESC) AS performance_rank
FROM ranked
ORDER BY daily_return_pct DESC
FETCH FIRST 10 ROWS ONLY;

-- 3. Weakest daily-return observations.
WITH returns AS (
    SELECT
        Date,
        Close,
        LAG(Close) OVER (ORDER BY Date) AS previous_close
    FROM stock_data
), ranked AS (
    SELECT
        Date,
        Close,
        (Close / NULLIF(previous_close, 0) - 1) * 100 AS daily_return_pct
    FROM returns
    WHERE previous_close IS NOT NULL
)
SELECT
    Date,
    Close,
    ROUND(daily_return_pct, 4) AS daily_return_pct,
    DENSE_RANK() OVER (ORDER BY daily_return_pct ASC) AS performance_rank
FROM ranked
ORDER BY daily_return_pct ASC
FETCH FIRST 10 ROWS ONLY;

-- 4. Period-level performance summary.
WITH returns AS (
    SELECT
        Date,
        Close,
        LAG(Close) OVER (ORDER BY Date) AS previous_close
    FROM stock_data
), period_stats AS (
    SELECT
        MIN(Date) AS start_date,
        MAX(Date) AS end_date,
        FIRST_VALUE(Close) OVER (ORDER BY Date) AS starting_close,
        FIRST_VALUE(Close) OVER (ORDER BY Date DESC) AS latest_close
    FROM returns
)
SELECT DISTINCT
    start_date,
    end_date,
    starting_close,
    latest_close,
    ROUND((latest_close / NULLIF(starting_close, 0) - 1) * 100, 4) AS period_return_pct,
    ROUND(latest_close - starting_close, 2) AS absolute_change
FROM period_stats;
