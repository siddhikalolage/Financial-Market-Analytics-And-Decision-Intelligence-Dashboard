-- KPI analysis for analyst / BI reporting.
-- SQL dialect: PostgreSQL-style window functions.
-- Assumes stock_data(Date, Open, High, Low, Close, Volume).

WITH daily AS (
    SELECT
        Date,
        Close,
        Volume,
        LAG(Close) OVER (ORDER BY Date) AS previous_close,
        FIRST_VALUE(Close) OVER (ORDER BY Date) AS first_close,
        MAX(Close) OVER (ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_peak,
        AVG(Volume) OVER (ORDER BY Date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS avg_volume_20d,
        ROW_NUMBER() OVER (ORDER BY Date DESC) AS latest_rank
    FROM stock_data
), metrics AS (
    SELECT
        *,
        (Close / NULLIF(previous_close, 0) - 1) * 100 AS daily_return_pct,
        (Close / NULLIF(first_close, 0) - 1) * 100 AS cumulative_return_pct,
        (Close / NULLIF(running_peak, 0) - 1) * 100 AS drawdown_pct,
        Close / NULLIF(avg_volume_20d, 0) AS volume_ratio
    FROM daily
)
SELECT
    Date AS latest_date,
    ROUND(Close::numeric, 2) AS latest_close,
    ROUND(daily_return_pct::numeric, 4) AS latest_daily_return_pct,
    ROUND(cumulative_return_pct::numeric, 4) AS period_return_pct,
    ROUND((Close / NULLIF(LAG(Close, 5) OVER (ORDER BY Date), 0) - 1)::numeric * 100, 4) AS five_day_return_pct,
    ROUND((Close / NULLIF(LAG(Close, 20) OVER (ORDER BY Date), 0) - 1)::numeric * 100, 4) AS twenty_day_return_pct,
    ROUND(drawdown_pct::numeric, 4) AS current_drawdown_pct,
    ROUND((SELECT MIN(drawdown_pct) FROM metrics)::numeric, 4) AS maximum_drawdown_pct,
    ROUND(avg_volume_20d::numeric, 2) AS average_volume_20d,
    ROUND(volume_ratio::numeric, 4) AS latest_volume_ratio,
    (SELECT COUNT(*) FROM stock_data) AS observations,
    (SELECT MIN(Date) FROM stock_data) AS first_date,
    (SELECT MAX(Date) FROM stock_data) AS last_date
FROM metrics
WHERE latest_rank = 1;

-- KPI distribution: positive vs negative sessions.
WITH returns AS (
    SELECT Close, LAG(Close) OVER (ORDER BY Date) AS previous_close
    FROM stock_data
)
SELECT
    COUNT(*) FILTER (WHERE Close > previous_close) AS up_days,
    COUNT(*) FILTER (WHERE Close < previous_close) AS down_days,
    COUNT(*) FILTER (WHERE Close = previous_close) AS flat_days,
    ROUND(AVG((Close / NULLIF(previous_close, 0) - 1) * 100)::numeric, 4) AS average_daily_return_pct
FROM returns
WHERE previous_close IS NOT NULL;
