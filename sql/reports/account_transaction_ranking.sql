WITH account_totals AS (
    SELECT
        a.account_id,
        a.customer_id,
        c.name AS customer_name,

        COUNT(t.transaction_id) AS transaction_count,

        SUM(t.amount) AS total_amount

    FROM accounts AS a

    JOIN customers AS c
        ON c.customer_id = a.customer_id

    JOIN transactions AS t
        ON t.account_id = a.account_id

    GROUP BY
        a.account_id,
        a.customer_id,
        c.name
),

ranked_accounts AS (
    SELECT
        account_id,
        customer_id,
        customer_name,
        transaction_count,
        total_amount,

        RANK() OVER (
            ORDER BY total_amount DESC
        ) AS amount_rank

    FROM account_totals
)

SELECT
    account_id,
    customer_id,
    customer_name,
    transaction_count,
    total_amount,
    amount_rank

FROM ranked_accounts

ORDER BY
    amount_rank,
    account_id;