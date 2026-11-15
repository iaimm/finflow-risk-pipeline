from sqlalchemy import func, select
from sqlalchemy.orm import Session

from finflow.models.entities import Account, Transaction
from finflow.orm_models import (
    AccountRecord,
    TransactionRecord,
)
from finflow.repositories.interfaces import (
    AccountRepository,
    TransactionRepository,
)


class PostgresAccountRepository(AccountRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(
        self,
        account_id: str,
    ) -> Account | None:
        record = self._session.get(
            AccountRecord,
            account_id,
        )

        if record is None:
            return None

        return Account(
            account_id=record.account_id,
            customer_id=record.customer_id,
            currency=record.currency,
        )


class PostgresTransactionRepository(TransactionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_domain(
        record: TransactionRecord,
    ) -> Transaction:
        return Transaction(
            transaction_id=record.transaction_id,
            account_id=record.account_id,
            amount=record.amount,
            currency=record.currency,
            transaction_type=record.transaction_type,
            occurred_at=record.occurred_at,
        )

    def add(self, transaction: Transaction) -> None:
        record = TransactionRecord(
            transaction_id=transaction.transaction_id,
            account_id=transaction.account_id,
            amount=transaction.amount,
            currency=transaction.currency,
            transaction_type=transaction.transaction_type,
            occurred_at=transaction.occurred_at,
        )

        self._session.add(record)

    def get_by_id(
        self,
        transaction_id: str,
    ) -> Transaction | None:
        record = self._session.get(
            TransactionRecord,
            transaction_id,
        )

        if record is None:
            return None

        return self._to_domain(record)

    def list(
        self,
        limit: int,
        offset: int,
    ) -> list[Transaction]:
        statement = (
            select(TransactionRecord)
            .order_by(
                TransactionRecord.occurred_at,
                TransactionRecord.transaction_id,
            )
            .offset(offset)
            .limit(limit)
        )

        records = self._session.scalars(statement).all()

        return [
            self._to_domain(record)
            for record in records
        ]

    def count(self) -> int:
        statement = select(
            func.count()
        ).select_from(TransactionRecord)

        return self._session.scalar(statement) or 0