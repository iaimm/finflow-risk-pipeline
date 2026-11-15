import os
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from finflow.db import build_session_factory
from finflow.orm_models import TransactionRecord


def get_session_factory():
    database_url = os.getenv(
        "FINFLOW_TEST_DATABASE_URL"
    )

    if not database_url:
        pytest.skip(
            "PostgreSQL integration test is not configured"
        )

    return build_session_factory(database_url)


def build_transaction(
    transaction_id: str,
    amount: Decimal,
) -> TransactionRecord:
    return TransactionRecord(
        transaction_id=transaction_id,
        account_id="A000001",
        amount=amount,
        currency="CNY",
        transaction_type="DEBIT",
        occurred_at=datetime.now(timezone.utc),
    )


def test_duplicate_transaction_id_is_rejected():
    session_factory = get_session_factory()

    with session_factory() as session:
        # 种子数据中已经存在 T00000001。
        session.add(
            build_transaction(
                transaction_id="T00000001",
                amount=Decimal("10.00"),
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()


def test_negative_amount_is_rejected():
    session_factory = get_session_factory()

    with session_factory() as session:
        session.add(
            build_transaction(
                transaction_id=f"T-NEGATIVE-{uuid4().hex}",
                amount=Decimal("-1.00"),
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()