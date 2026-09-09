-- Data quality checks for the historical OHLCV dataset.
-- Assumes a SQL table named stock_data(Date, Open, High, Low, Close, Volume).

-- 1. Required-column / null audit
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN Date IS NULL THEN 1 ELSE 0 END) AS null_dates,
    SUM(CASE WHEN Open IS NULL THEN 1 ELSE 0 END) AS null_open,
    SUM(CASE WHEN High IS NULL THEN 1 ELSE 0 END) AS null_high,
    SUM(CASE WHEN Low IS NULL THEN 1 ELSE 0 END) AS null_low,
    SUM(CASE WHEN Close IS NULL THEN 1 ELSE 0 END) AS null_close,
    SUM(CASE WHEN Volume IS NULL THEN 1 ELSE 0 END) AS null_volume
FROM stock_data;

-- 2. Duplicate-date audit
SELECT Date, COUNT(*) AS duplicate_count
FROM stock_data
GROUP BY Date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 3. OHLC consistency checks
SELECT *
FROM stock_data
WHERE High < Low
   OR High < Open
   OR High < Close
   OR Low > Open
   OR Low > Close
   OR Volume < 0;

-- 4. Date coverage
SELECT MIN(Date) AS first_date, MAX(Date) AS last_date, COUNT(*) AS observations
FROM stock_data;
