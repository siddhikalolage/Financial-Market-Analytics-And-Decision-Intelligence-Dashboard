-- Core KPI analysis for analyst / BI reporting.
-- Assumes a SQL table named stock_data(Date, Open, High, Low, Close, Volume).

WITH daily AS (
    SELECT
        Date,
        Close,
        Volume,
        LAG(Close) OVER (ORDER BY Date) AS previous_close,
        FIRST_VALUE(Close) OVER (ORDER BY Date) AS first_close,
        MAX(Close) OVER (ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_peak,
        ROW_NUMBER() OVER (ORDER BY Date DESC) AS latest_rank
    FROM stock_data
), metrics AS (
    SELECT
        *,
        (Close / NULLIF(previous_close, 0) - 1) * 100 AS daily_return_pct,
        (Close / NULLIF(first_close, 0) - 1) * 100 AS cumulative_return_pct,
        (Close / NULLIF(running_peak, 0) - 1) * 100 AS drawdown_pct
    FROM daily
)
SELECT
    Date AS latest_date,
    Close AS latest_close,
    daily_return_pct AS latest_daily_return_pct,
    cumulative_return_pct,
    (SELECT AVG(Volume) FROM stock_data) AS average_volume,
    (SELECT MIN(drawdown_pct) FROM metrics) AS maximum_drawdown_pct
FROM metrics
WHERE latest_rank = 1;
