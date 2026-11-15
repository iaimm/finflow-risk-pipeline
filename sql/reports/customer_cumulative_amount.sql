WITH daily_customer_amounts AS (
    SELECT
        c.customer_id,
        c.name AS customer_name,

        (
            t.occurred_at AT TIME ZONE 'Asia/Shanghai'
        )::date AS transaction_date,

        COUNT(t.transaction_id) AS transaction_count,

        SUM(t.amount) AS daily_amount

    FROM customers AS c

    JOIN accounts AS a
        ON a.customer_id = c.customer_id

    JOIN transactions AS t
        ON t.account_id = a.account_id

    GROUP BY
        c.customer_id,
        c.name,
        (
            t.occurred_at AT TIME ZONE 'Asia/Shanghai'
        )::date
),

customer_cumulative AS (
    SELECT
        customer_id,
        customer_name,
        transaction_date,
        transaction_count,
        daily_amount,

        SUM(daily_amount) OVER (
            PARTITION BY customer_id
            ORDER BY transaction_date
            ROWS BETWEEN
                UNBOUNDED PRECEDING
                AND CURRENT ROW
        ) AS cumulative_amount

    FROM daily_customer_amounts
)

SELECT
    customer_id,
    customer_name,
    transaction_date,
    transaction_count,
    daily_amount,
    cumulative_amount

FROM customer_cumulative

ORDER BY
    customer_id,
    transaction_date;