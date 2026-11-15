import os

from sqlalchemy import func, select

from finflow.db import build_session_factory
from finflow.orm_models import (
    AccountRecord,
    CustomerRecord,
    TransactionRecord,
)
from finflow.pipelines.generate_mock_data import (
    generate_mock_data,
)


def main() -> None:
    database_url = os.getenv("FINFLOW_DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "FINFLOW_DATABASE_URL is not configured"
        )

    session_factory = build_session_factory(database_url)
    dataset = generate_mock_data(
        transaction_count=100,
        seed=42,
    )

    with session_factory() as session:
        try:
            customer_count = session.scalar(
                select(func.count()).select_from(
                    CustomerRecord
                )
            )

            if customer_count:
                print("Database already contains data; skipping seed")
                return

            # 1. 先写客户，并立即执行 SQL，但暂不提交事务。
            session.add_all(
                CustomerRecord(
                    customer_id=customer.customer_id,
                    name=customer.name,
                    created_at=customer.created_at,
                )
                for customer in dataset.customers
            )
            session.flush()

            # 2. 客户已经写入当前事务，再写账户。
            session.add_all(
                AccountRecord(
                    account_id=account.account_id,
                    customer_id=account.customer_id,
                    currency=account.currency,
                )
                for account in dataset.accounts
            )
            session.flush()

            # 3. 账户已经写入当前事务，再写交易。
            session.add_all(
                TransactionRecord(
                    transaction_id=transaction.transaction_id,
                    account_id=transaction.account_id,
                    amount=transaction.amount,
                    currency=transaction.currency,
                    transaction_type=transaction.transaction_type,
                    occurred_at=transaction.occurred_at,
                )
                for transaction in dataset.transactions
            )

            # 4. 三组数据都成功后，统一提交。
            session.commit()
            print("Database seeded successfully")

        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    main()