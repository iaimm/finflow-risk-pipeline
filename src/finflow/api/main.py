from fastapi import FastAPI

from finflow.api.errors import register_exception_handlers
from finflow.api.routes.transactions import router as transactions_router
from finflow.pipelines.generate_mock_data import generate_mock_data
from finflow.repositories.memory import (
    InMemoryAccountRepository,
    InMemoryTransactionRepository,
)
from finflow.services.transaction_service import TransactionService

from finflow.api.auth_dependencies import (
    get_auth_service,
)
from finflow.api.routes.auth import router as auth_router
from finflow.api.routes.reports import router as reports_router
from finflow.config import AuthSettings
from finflow.models.entities import User
from finflow.repositories.memory import InMemoryUserRepository
from finflow.security import hash_password
from finflow.services.auth_service import AuthService


def create_app(
    auth_settings: AuthSettings | None = None,
) -> FastAPI:
    auth_settings = (
        auth_settings or AuthSettings.from_env()
    )

    dataset = generate_mock_data(
        transaction_count=100,
        seed=42,
    )

    account_repository = InMemoryAccountRepository(
        dataset.accounts
    )
    transaction_repository = InMemoryTransactionRepository()

    for transaction in dataset.transactions:
        transaction_repository.add(transaction)

    transaction_service = TransactionService(
        account_repository=account_repository,
        transaction_repository=transaction_repository,
    )

    users = (
        User(
            user_id="U-ADMIN",
            username="admin",
            password_hash=hash_password(
                auth_settings.demo_admin_password
            ),
            roles=("admin", "viewer"),
        ),
        User(
            user_id="U-VIEWER",
            username="viewer",
            password_hash=hash_password(
                auth_settings.demo_viewer_password
            ),
            roles=("viewer",),
        ),
    )

    user_repository = InMemoryUserRepository(users)
    auth_service = AuthService(user_repository)

    app = FastAPI(
        title="FinFlow Risk Pipeline API",
        version="0.1.0",
    )

    app.state.transaction_service = transaction_service
    app.state.auth_service = auth_service
    app.state.auth_settings = auth_settings

    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(reports_router)
    app.include_router(transactions_router)

    return app


app = create_app()