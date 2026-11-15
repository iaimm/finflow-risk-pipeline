SELECT
    (
        occurred_at AT TIME ZONE 'Asia/Shanghai'
    )::date AS transaction_date,

    COUNT(*) AS transaction_count,

    COUNT(DISTINCT account_id) AS active_accounts,

    SUM(amount) AS total_amount,

    SUM(
        CASE
            WHEN transaction_type = 'DEBIT'
            THEN amount
            ELSE 0
        END
    ) AS debit_amount,

    SUM(
        CASE
            WHEN transaction_type = 'CREDIT'
            THEN amount
            ELSE 0
        END
    ) AS credit_amount,

    SUM(
        CASE
            WHEN transaction_type = 'CREDIT'
            THEN amount
            WHEN transaction_type = 'DEBIT'
            THEN -amount
            ELSE 0
        END
    ) AS net_amount

FROM transactions

GROUP BY
    (
        occurred_at AT TIME ZONE 'Asia/Shanghai'
    )::date

ORDER BY transaction_date;