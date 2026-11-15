WITH new_batch AS (
    INSERT INTO etl_batches (
        batch_no,
        status
    )
    VALUES (
        'BATCH-20261115-001',
        'SUCCESS'
    )
    RETURNING id
),
new_customer AS (
    INSERT INTO customers (
        customer_no,
        name
    )
    VALUES (
        'CUST-000001',
        '测试客户'
    )
    RETURNING id
),
new_account AS (
    INSERT INTO accounts (
        account_no,
        customer_id,
        currency,
        status
    )
    SELECT
        'ACC-000001',
        id,
        'CNY',
        'ACTIVE'
    FROM new_customer
    RETURNING id
)
INSERT INTO transactions (
    transaction_no,
    batch_id,
    account_id,
    amount,
    currency,
    transaction_type,
    occurred_at
)
SELECT
    'TXN-20261115-000001',
    new_batch.id,
    new_account.id,
    100.25,
    'CNY',
    'DEPOSIT',
    NOW()
FROM new_batch
CROSS JOIN new_account;