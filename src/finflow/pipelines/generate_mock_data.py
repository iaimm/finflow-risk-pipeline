import argparse
import csv
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Sequence

import logging

from finflow.config import Settings
from finflow.logging_config import configure_logging

logger = logging.getLogger(__name__)

from finflow.models.entities import Account, Customer, Transaction


@dataclass(frozen=True, slots=True)
class MockDataset:
    customers: tuple[Customer, ...]
    accounts: tuple[Account, ...]
    transactions: tuple[Transaction, ...]


def generate_mock_data(
    transaction_count: int = 100,
    seed: int = 42,
) -> MockDataset:
    """生成具有完整客户、账户和交易引用关系的模拟数据。"""
    if transaction_count < 1:
        raise ValueError("transaction_count must be greater than zero")

    rng = random.Random(seed)
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    customers: list[Customer] = []
    accounts: list[Account] = []

    account_number = 1

    for customer_number in range(1, 11):
        customer = Customer(
            customer_id=f"C{customer_number:06d}",
            name=f"Mock Customer {customer_number:02d}",
            created_at=base_time,
        )
        customers.append(customer)

        # 每个客户拥有两个账户。
        for _ in range(2):
            accounts.append(
                Account(
                    account_id=f"A{account_number:06d}",
                    customer_id=customer.customer_id,
                    currency="CNY",
                )
            )
            account_number += 1

    transactions: list[Transaction] = []

    for transaction_number in range(1, transaction_count + 1):
        account = rng.choice(accounts)

        # 生成 1.00～5000.00 之间的金额，不使用 float。
        amount = (
            Decimal(rng.randint(100, 500_000))
            / Decimal("100")
        )

        transactions.append(
            Transaction(
                transaction_id=f"T{transaction_number:08d}",
                account_id=account.account_id,
                amount=amount,
                currency=account.currency,
                transaction_type=rng.choice(("DEBIT", "CREDIT")),
                occurred_at=base_time
                + timedelta(minutes=transaction_number * 15),
            )
        )

    return MockDataset(
        customers=tuple(customers),
        accounts=tuple(accounts),
        transactions=tuple(transactions),
    )


def _write_csv(path: Path, rows: Sequence[object]) -> None:
    """将数据类对象写入 CSV。"""
    if not rows:
        raise ValueError(f"No rows to write for {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    dictionaries = [asdict(row) for row in rows]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(dictionaries[0].keys()),
        )
        writer.writeheader()
        writer.writerows(dictionaries)


def write_dataset(dataset: MockDataset, output_dir: Path) -> None:
    _write_csv(output_dir / "customers.csv", dataset.customers)
    _write_csv(output_dir / "accounts.csv", dataset.accounts)
    _write_csv(output_dir / "transactions.csv", dataset.transactions)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic financial mock data."
    )
    parser.add_argument(
        "--transactions",
        type=int,
        default=100,
        help="Number of transactions to generate.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible output.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=settings.data_dir,
        help="CSV output directory.",
    )
    args = parser.parse_args()

    dataset = generate_mock_data(
        transaction_count=args.transactions,
        seed=args.seed,
    )
    write_dataset(dataset, args.output_dir)

    logger.info(
        "Generated %d customers, %d accounts, and %d transactions in %s",
        len(dataset.customers),
        len(dataset.accounts),
        len(dataset.transactions),
        args.output_dir,
    )


if __name__ == "__main__":
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    main()