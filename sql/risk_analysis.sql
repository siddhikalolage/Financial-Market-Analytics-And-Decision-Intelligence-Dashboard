-- Risk analytics queries.
-- Assumes stock_data(Date, Open, High, Low, Close, Volume).

WITH returns AS (
    SELECT
        Date,
        Close,
        (Close / NULLIF(LAG(Close) OVER (ORDER BY Date), 0) - 1) * 100 AS daily_return_pct,
        MAX(Close) OVER (ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_peak
    FROM stock_data
), risk AS (
    SELECT
        *,
        (Close / NULLIF(running_peak, 0) - 1) * 100 AS drawdown_pct,
        STDDEV(daily_return_pct) OVER (ORDER BY Date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) * SQRT(252) AS rolling_20d_volatility
    FROM returns
)
SELECT
    Date,
    Close,
    ROUND(daily_return_pct, 4) AS daily_return_pct,
    ROUND(rolling_20d_volatility, 4) AS rolling_20d_annualized_volatility_pct,
    ROUND(drawdown_pct, 4) AS drawdown_pct
FROM risk
ORDER BY Date;

-- Largest drawdown observations.
WITH peaks AS (
    SELECT Date, Close,
           MAX(Close) OVER (ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_peak
    FROM stock_data
)
SELECT Date, Close,
       ROUND((Close / NULLIF(running_peak, 0) - 1) * 100, 4) AS drawdown_pct
FROM peaks
ORDER BY drawdown_pct ASC
FETCH FIRST 10 ROWS ONLY;
