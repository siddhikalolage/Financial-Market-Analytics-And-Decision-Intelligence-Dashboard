-- Core KPI analysis for analyst / BI reporting.
-- Assumes a SQL table named stock_data(Date, Open, High, Low, Close, Volume).

WITH daily AS (
    SELECT
        Date,
        Close,
        Volume,
        LAG(Close) OVER (ORDER BY Date) AS previous_close,
        MAX(Close) OVER (ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_peak
    FROM stock_data
), metrics AS (
    SELECT
        *,
        (Close / NULLIF(previous_close, 0) - 1) * 100 AS daily_return_pct,
        (Close / NULLIF(FIRST_VALUE(Close) OVER (ORDER BY Date), 0) - 1) * 100 AS cumulative_return_pct,
        (Close / NULLIF(running_peak, 0) - 1) * 100 AS drawdown_pct
    FROM daily
)
SELECT
    MAX(Date) AS latest_date,
    MAX(Close) KEEP (DENSE_RANK LAST ORDER BY Date) AS latest_close,
    MAX(daily_return_pct) KEEP (DENSE_RANK LAST ORDER BY Date) AS latest_daily_return_pct,
    MAX(cumulative_return_pct) KEEP (DENSE_RANK LAST ORDER BY Date) AS cumulative_return_pct,
    AVG(Volume) AS average_volume,
    MIN(drawdown_pct) AS maximum_drawdown_pct
FROM metrics;
