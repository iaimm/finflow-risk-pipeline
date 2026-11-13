from decimal import Decimal

import pytest

from finflow.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)

from finflow.pipelines.generate_mock_data import generate_mock_data
from finflow.repositories.memory import (
    InMemoryAccountRepository,
    InMemoryTransactionRepository,
)
from finflow.services.transaction_service import TransactionService


def build_service():
    dataset = generate_mock_data(
        transaction_count=100,
        seed=42,
    )

    account_repository = InMemoryAccountRepository(
        dataset.accounts
    )
    transaction_repository = InMemoryTransactionRepository()

    service = TransactionService(
        account_repository=account_repository,
        transaction_repository=transaction_repository,
    )

    return (
        service,
        transaction_repository,
        dataset.accounts[0],
    )


def test_create_transaction_successfully():
    service, repository, account = build_service()

    transaction = service.create_transaction(
        transaction_id="T-TEST-001",
        account_id=account.account_id,
        amount=Decimal("99.90"),
        currency=account.currency,
    )

    assert transaction.transaction_id == "T-TEST-001"
    assert repository.get_by_id("T-TEST-001") == transaction


def test_reject_transaction_for_unknown_account():
    service, _, _ = build_service()

    with pytest.raises(NotFoundError, match="Account not found"):
        service.create_transaction(
            transaction_id="T-TEST-002",
            account_id="A-NOT-EXIST",
            amount=Decimal("99.90"),
        )


def test_reject_duplicate_transaction_id():
    service, _, account = build_service()

    service.create_transaction(
        transaction_id="T-TEST-003",
        account_id=account.account_id,
        amount=Decimal("99.90"),
    )

    with pytest.raises(ConflictError, match="already exists"):
        service.create_transaction(
            transaction_id="T-TEST-003",
            account_id=account.account_id,
            amount=Decimal("99.90"),
        )

def test_allow_small_positive_amount():
    service, repository, account = build_service()

    transaction = service.create_transaction(
        transaction_id="T-BOUNDARY-001",
        account_id=account.account_id,
        amount=Decimal("0.01"),
    )

    assert transaction.amount == Decimal("0.01")
    assert repository.get_by_id("T-BOUNDARY-001") == transaction


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0"),
        Decimal("-0.01"),
        Decimal("-100"),
    ],
)
def test_reject_non_positive_amount(amount: Decimal):
    service, _, account = build_service()

    with pytest.raises(
        ValidationError,
        match="must be positive",
    ):
        service.create_transaction(
            transaction_id="T-INVALID-AMOUNT",
            account_id=account.account_id,
            amount=amount,
        )


def test_reject_currency_mismatch():
    service, _, account = build_service()

    with pytest.raises(ValidationError, match="currency"):
        service.create_transaction(
            transaction_id="T-CURRENCY-001",
            account_id=account.account_id,
            amount=Decimal("100"),
            currency="USD",
        )