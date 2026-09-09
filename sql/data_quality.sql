-- Data quality controls for the historical OHLCV dataset (PostgreSQL-style SQL).
-- Assumes stock_data(Date, Open, High, Low, Close, Volume).
-- Goal: make data validation explicit before KPI and BI consumption.

-- 1. Required-field and null audit.
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN Date IS NULL THEN 1 ELSE 0 END) AS null_dates,
    SUM(CASE WHEN Open IS NULL THEN 1 ELSE 0 END) AS null_open,
    SUM(CASE WHEN High IS NULL THEN 1 ELSE 0 END) AS null_high,
    SUM(CASE WHEN Low IS NULL THEN 1 ELSE 0 END) AS null_low,
    SUM(CASE WHEN Close IS NULL THEN 1 ELSE 0 END) AS null_close,
    SUM(CASE WHEN Volume IS NULL THEN 1 ELSE 0 END) AS null_volume,
    SUM(CASE WHEN Close = 0 THEN 1 ELSE 0 END) AS zero_close,
    SUM(CASE WHEN Open < 0 OR High < 0 OR Low < 0 OR Close < 0 OR Volume < 0 THEN 1 ELSE 0 END) AS negative_value_rows
FROM stock_data;

-- 2. Duplicate-date audit.
SELECT
    Date,
    COUNT(*) AS duplicate_count
FROM stock_data
GROUP BY Date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, Date;

-- 3. OHLC logical-consistency audit.
SELECT
    Date,
    Open,
    High,
    Low,
    Close,
    Volume,
    CASE
        WHEN High < GREATEST(Open, Close) THEN 'Invalid High'
        WHEN Low > LEAST(Open, Close) THEN 'Invalid Low'
        WHEN High < Low THEN 'Invalid Range'
        WHEN Volume < 0 THEN 'Invalid Volume'
        WHEN Close = 0 THEN 'Zero Close'
        ELSE 'Valid'
    END AS quality_status
FROM stock_data
WHERE High < GREATEST(Open, Close)
   OR Low > LEAST(Open, Close)
   OR High < Low
   OR Volume < 0
   OR Close = 0
ORDER BY Date;

-- 4. Date coverage and chronological integrity.
SELECT
    MIN(Date) AS first_date,
    MAX(Date) AS last_date,
    COUNT(*) AS observations,
    COUNT(DISTINCT Date) AS distinct_dates,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT Date) THEN 'PASS'
        ELSE 'FAIL'
    END AS unique_date_check
FROM stock_data;

-- 5. Compact quality scorecard for BI review.
WITH checks AS (
    SELECT
        COUNT(*) AS total_rows,
        SUM(CASE WHEN Date IS NULL OR Open IS NULL OR High IS NULL
                      OR Low IS NULL OR Close IS NULL OR Volume IS NULL
                 THEN 1 ELSE 0 END) AS null_rows,
        SUM(CASE WHEN High < GREATEST(Open, Close)
                      OR Low > LEAST(Open, Close)
                      OR High < Low
                      OR Volume < 0
                      OR Close = 0
                 THEN 1 ELSE 0 END) AS invalid_rows,
        COUNT(*) - COUNT(DISTINCT Date) AS duplicate_date_rows
    FROM stock_data
)
SELECT
    total_rows,
    null_rows,
    invalid_rows,
    duplicate_date_rows,
    CASE
        WHEN null_rows = 0 AND invalid_rows = 0 AND duplicate_date_rows = 0
        THEN 'PASS'
        ELSE 'REVIEW'
    END AS overall_quality_status
FROM checks;
