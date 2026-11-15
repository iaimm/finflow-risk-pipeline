import os
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from finflow.db import build_session_factory
from finflow.models.entities import Transaction
from finflow.orm_models import TransactionRecord
from finflow.repositories.postgres import (
    PostgresTransactionRepository,
)


def test_commit_and_rollback():
    database_url = os.getenv(
        "FINFLOW_TEST_DATABASE_URL"
    )

    if not database_url:
        pytest.skip("PostgreSQL integration test is not configured")

    session_factory = build_session_factory(database_url)

    transaction = Transaction(
        transaction_id=f"T-TEST-{uuid4().hex}",
        account_id="A000001",
        amount=Decimal("10.00"),
        currency="CNY",
        transaction_type="DEBIT",
        occurred_at=datetime.now(timezone.utc),
    )

    # 添加后回滚，新 Session 中不应存在。
    with session_factory() as session:
        repository = PostgresTransactionRepository(session)
        repository.add(transaction)
        session.rollback()

    with session_factory() as session:
        repository = PostgresTransactionRepository(session)
        assert repository.get_by_id(
            transaction.transaction_id
        ) is None

    # 再次添加并提交，新 Session 中应当存在。
    with session_factory() as session:
        repository = PostgresTransactionRepository(session)
        repository.add(transaction)
        session.commit()

    with session_factory() as session:
        repository = PostgresTransactionRepository(session)
        saved = repository.get_by_id(
            transaction.transaction_id
        )
        assert saved is not None

    # 清理测试数据。
    with session_factory() as session:
        record = session.get(
            TransactionRecord,
            transaction.transaction_id,
        )
        if record is not None:
            session.delete(record)
            session.commit()