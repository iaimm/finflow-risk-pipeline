from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Customer:
    customer_id: str
    name: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Account:
    account_id: str
    customer_id: str
    currency: str


@dataclass(frozen=True, slots=True)
class Transaction:
    transaction_id: str
    account_id: str
    amount: Decimal
    currency: str
    transaction_type: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class User:
    user_id: str
    username: str
    password_hash: str
    roles: tuple[str, ...]
    disabled: bool = False