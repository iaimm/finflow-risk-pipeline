DROP TABLE IF EXISTS perf_transactions;

CREATE TABLE perf_transactions (
    transaction_id VARCHAR(40) PRIMARY KEY,
    account_id VARCHAR(32) NOT NULL,
    amount NUMERIC(14, 2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL
);
s
INSERT INTO perf_transactions (
    transaction_id,
    account_id,
    amount,
    transaction_type,
    occurred_at
)
SELECT
    'P' || LPAD(g::TEXT, 8, '0'),
    'A' || LPAD((g % 1000)::TEXT, 6, '0'),
    ROUND((RANDOM() * 5000 + 1)::NUMERIC, 2),
    CASE
        WHEN g % 2 = 0 THEN 'DEBIT'
        ELSE 'CREDIT'
    END,
    TIMESTAMPTZ '2025-01-01 00:00:00+00'
        + (g % 31536000) * INTERVAL '1 second'
FROM generate_series(1, 300000) AS g;

ANALYZE perf_transactions;