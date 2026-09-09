-- Decision-support ranking queries.
-- Assumes stock_data(Date, Open, High, Low, Close, Volume).

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
        (Close / NULLIF(running_peak, 0) - 1) * 100 AS drawdown_pct
    FROM daily
)
SELECT
    Date,
    Close,
    ROUND(daily_return_pct, 4) AS daily_return_pct,
    ROUND(drawdown_pct, 4) AS drawdown_pct,
    CASE
        WHEN daily_return_pct > 0 THEN 'Positive'
        WHEN daily_return_pct < 0 THEN 'Negative'
        ELSE 'Flat'
    END AS daily_direction,
    CASE
        WHEN drawdown_pct <= -10 THEN 'High Drawdown'
        WHEN drawdown_pct <= -5 THEN 'Moderate Drawdown'
        ELSE 'Normal Range'
    END AS risk_band
FROM metrics
ORDER BY Date;

-- Rank the strongest positive observations for analyst review.
WITH returns AS (
    SELECT Date, Close,
           (Close / NULLIF(LAG(Close) OVER (ORDER BY Date), 0) - 1) * 100 AS daily_return_pct
    FROM stock_data
)
SELECT
    Date,
    Close,
    ROUND(daily_return_pct, 4) AS daily_return_pct,
    DENSE_RANK() OVER (ORDER BY daily_return_pct DESC) AS performance_rank
FROM returns
WHERE daily_return_pct IS NOT NULL
ORDER BY performance_rank
FETCH FIRST 10 ROWS ONLY;
