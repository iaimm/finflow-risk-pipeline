import pytest

from finflow.pipelines.generate_mock_data import generate_mock_data


def test_generate_complete_and_consistent_dataset():
    dataset = generate_mock_data(transaction_count=100, seed=42)

    assert len(dataset.customers) == 10
    assert len(dataset.accounts) == 20
    assert len(dataset.transactions) == 100

    customer_ids = {
        customer.customer_id for customer in dataset.customers
    }
    account_ids = {
        account.account_id for account in dataset.accounts
    }
    transaction_ids = {
        transaction.transaction_id
        for transaction in dataset.transactions
    }

    # 每个账户都属于真实存在的客户。
    assert all(
        account.customer_id in customer_ids
        for account in dataset.accounts
    )

    # 每笔交易都属于真实存在的账户。
    assert all(
        transaction.account_id in account_ids
        for transaction in dataset.transactions
    )

    # 交易编号唯一，金额必须为正数。
    assert len(transaction_ids) == 100
    assert all(
        transaction.amount > 0
        for transaction in dataset.transactions
    )


def test_same_seed_produces_same_dataset():
    first = generate_mock_data(transaction_count=100, seed=42)
    second = generate_mock_data(transaction_count=100, seed=42)

    assert first == second


def test_invalid_transaction_count_is_rejected():
    with pytest.raises(ValueError):
        generate_mock_data(transaction_count=0)