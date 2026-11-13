from typing import Annotated

from fastapi import APIRouter, Query, status

from finflow.api.dependencies import TransactionServiceDep
from finflow.api.schemas import (
    TransactionCreateRequest,
    TransactionListResponse,
    TransactionResponse,
)


router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["transactions"],
)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payload: TransactionCreateRequest,
    service: TransactionServiceDep,
) -> object:
    return service.create_transaction(
        transaction_id=payload.transaction_id,
        account_id=payload.account_id,
        amount=payload.amount,
        currency=payload.currency,
        transaction_type=payload.transaction_type,
        occurred_at=payload.occurred_at,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: str,
    service: TransactionServiceDep,
) -> object:
    return service.get_transaction(transaction_id)


@router.get(
    "",
    response_model=TransactionListResponse,
)
def list_transactions(
    service: TransactionServiceDep,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> dict:
    transactions, total = service.list_transactions(
        limit=limit,
        offset=offset,
    )

    return {
        "items": transactions,
        "total": total,
        "limit": limit,
        "offset": offset,
    }