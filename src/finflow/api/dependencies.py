from typing import Annotated

from fastapi import Depends, Request

from finflow.services.transaction_service import TransactionService


def get_transaction_service(
    request: Request,
) -> TransactionService:
    return request.app.state.transaction_service


TransactionServiceDep = Annotated[
    TransactionService,
    Depends(get_transaction_service),
]