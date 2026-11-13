from fastapi import FastAPI

from finflow.api.errors import register_exception_handlers
from finflow.api.routes.transactions import router as transactions_router
from finflow.pipelines.generate_mock_data import generate_mock_data
from finflow.repositories.memory import (
    InMemoryAccountRepository,
    InMemoryTransactionRepository,
)
from finflow.services.transaction_service import TransactionService


def create_app() -> FastAPI:
    dataset = generate_mock_data(
        transaction_count=100,
        seed=42,
    )

    account_repository = InMemoryAccountRepository(
        dataset.accounts
    )
    transaction_repository = InMemoryTransactionRepository()

    # 预加载模拟交易，方便启动后立即测试查询接口。
    for transaction in dataset.transactions:
        transaction_repository.add(transaction)

    transaction_service = TransactionService(
        account_repository=account_repository,
        transaction_repository=transaction_repository,
    )

    app = FastAPI(
        title="FinFlow Risk Pipeline API",
        version="0.1.0",
    )

    app.state.transaction_service = transaction_service

    register_exception_handlers(app)
    app.include_router(transactions_router)

    return app


app = create_app()