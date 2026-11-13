from datetime import datetime, timezone
from decimal import Decimal

import logging

from finflow.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)

from finflow.models.entities import Transaction
from finflow.repositories.interfaces import (
    AccountRepository,
    TransactionRepository,
)


class TransactionService:
    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self._account_repository = account_repository
        self._transaction_repository = transaction_repository

    def create_transaction(
        self,
        transaction_id: str,
        account_id: str,
        amount: Decimal,
        currency: str = "CNY",
        transaction_type: str = "DEBIT",
        occurred_at: datetime | None = None,
    ) -> Transaction:
        if amount <= 0:
            raise ValidationError("Transaction amount must be positive")

        account = self._account_repository.get_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account not found: {account_id}")

        if currency != account.currency:
            raise ValidationError(
                "Transaction currency must match account currency"
            )

        if transaction_type not in {"DEBIT", "CREDIT"}:
            raise ValidationError("Invalid transaction type")

        existing = self._transaction_repository.get_by_id(
            transaction_id
        )
        if existing is not None:
            raise ConflictError(
                f"Transaction already exists: {transaction_id}"
            )

        transaction = Transaction(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            occurred_at=occurred_at or datetime.now(timezone.utc),
        )

        self._transaction_repository.add(transaction)
        logger.info(
            "Transaction created: transaction_id=%s, account_id=%s",
            transaction.transaction_id,
            transaction.account_id,
        )
        return transaction

    def get_transaction(
        self,
        transaction_id: str,
    ) -> Transaction:
        transaction = self._transaction_repository.get_by_id(
            transaction_id
        )

        if transaction is None:
            raise NotFoundError(
                f"Transaction not found: {transaction_id}"
            )

        return transaction


    def list_transactions(
        self,
        limit: int,
        offset: int,
    ) -> tuple[list[Transaction], int]:
        transactions = self._transaction_repository.list(
            limit=limit,
            offset=offset,
        )
        total = self._transaction_repository.count()

        return transactions, total