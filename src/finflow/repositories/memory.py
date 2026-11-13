from collections.abc import Iterable

from finflow.models.entities import Account, Transaction
from finflow.repositories.interfaces import (
    AccountRepository,
    TransactionRepository,
)


class InMemoryAccountRepository(AccountRepository):
    def __init__(self, accounts: Iterable[Account] = ()) -> None:
        self._accounts = {
            account.account_id: account
            for account in accounts
        }

    def get_by_id(self, account_id: str) -> Account | None:
        return self._accounts.get(account_id)


class InMemoryTransactionRepository(TransactionRepository):
    def __init__(self) -> None:
        self._transactions: dict[str, Transaction] = {}

    def add(self, transaction: Transaction) -> None:
        self._transactions[transaction.transaction_id] = transaction

    def get_by_id(
        self,
        transaction_id: str,
    ) -> Transaction | None:
        return self._transactions.get(transaction_id)


    def list(
        self,
        limit: int,
        offset: int,
    ) -> list[Transaction]:
        transactions = list(self._transactions.values())
        return transactions[offset:offset + limit]

    def count(self) -> int:
        return len(self._transactions)


class InMemoryUserRepository(UserRepository):
    def __init__(self, users: Iterable[User]) -> None:
        self._users = {
            user.username: user
            for user in users
        }

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        return self._users.get(username)