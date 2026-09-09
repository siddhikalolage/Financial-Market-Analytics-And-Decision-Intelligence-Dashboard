-- Performance analysis queries.
-- Assumes stock_data(Date, Open, High, Low, Close, Volume).

WITH returns AS (
    SELECT
        Date,
        Close,
        Volume,
        LAG(Close) OVER (ORDER BY Date) AS previous_close
    FROM stock_data
)
SELECT
    Date,
    Close,
    ROUND((Close / NULLIF(previous_close, 0) - 1) * 100, 4) AS daily_return_pct,
    ROUND(AVG(Close) OVER (ORDER BY Date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2) AS ma_20,
    ROUND(AVG(Close) OVER (ORDER BY Date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2) AS ma_50
FROM returns
ORDER BY Date;

-- Best and worst daily return observations.
WITH returns AS (
    SELECT Date, Close, LAG(Close) OVER (ORDER BY Date) AS previous_close
    FROM stock_data
)
SELECT Date, Close,
       ROUND((Close / NULLIF(previous_close, 0) - 1) * 100, 4) AS daily_return_pct
FROM returns
WHERE previous_close IS NOT NULL
ORDER BY daily_return_pct DESC
FETCH FIRST 10 ROWS ONLY;
