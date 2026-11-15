from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from finflow.db import Base


class CustomerRecord(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class AccountRecord(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        CheckConstraint(
            "char_length(currency) = 3",
            name="ck_accounts_currency_length",
        ),
    )

    account_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"),
        nullable=False,
        index=True,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )


class TransactionRecord(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_transactions_amount_positive",
        ),
        CheckConstraint(
            "transaction_type IN ('DEBIT', 'CREDIT')",
            name="ck_transactions_transaction_type",
        ),
        CheckConstraint(
            "char_length(currency) = 3",
            name="ck_transactions_currency_length",
        ),
    )

    transaction_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[str | None] = mapped_column(
        ForeignKey("ingestion_batches.batch_id"),
        nullable=True,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )


class IngestionBatchRecord(Base):
    __tablename__ = "ingestion_batches"

    __table_args__ = (
        UniqueConstraint(
            "source_name",
            "source_checksum",
            name="uq_ingestion_batches_source_checksum",
        ),
        CheckConstraint(
            "status IN "
            "('PENDING', 'PROCESSING', 'SUCCEEDED', 'FAILED')",
            name="ck_ingestion_batches_status",
        ),
        CheckConstraint(
            "received_count >= 0",
            name="ck_ingestion_batches_received_count",
        ),
        CheckConstraint(
            "success_count >= 0",
            name="ck_ingestion_batches_success_count",
        ),
        CheckConstraint(
            "failed_count >= 0",
            name="ck_ingestion_batches_failed_count",
        ),
    )

    batch_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    source_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    source_checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
    )
    received_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    success_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    failed_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )