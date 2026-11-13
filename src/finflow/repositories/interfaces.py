from abc import ABC, abstractmethod

from finflow.models.entities import Account, Transaction


class AccountRepository(ABC):
    @abstractmethod
    def get_by_id(self, account_id: str) -> Account | None:
        """根据账户 ID 查询账户；不存在时返回 None。"""
        ...


class TransactionRepository(ABC):
    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        """保存一笔交易。"""
        ...

    @abstractmethod
    def get_by_id(
        self,
        transaction_id: str,
    ) -> Transaction | None:
        """根据交易 ID 查询交易；不存在时返回 None。"""
        ...

    @abstractmethod
    def list(
        self,
        limit: int,
        offset: int,
    ) -> list[Transaction]:
        """按创建顺序分页查询交易。"""
        ...

    @abstractmethod
    def count(self) -> int:
        """返回交易总数。"""
        ...


class UserRepository(ABC):
    @abstractmethod
    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        ...