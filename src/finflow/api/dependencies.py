from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request

from finflow.services.transaction_service import TransactionService
def get_transaction_service(
    request: Request,
) -> Iterator[TransactionService]:
    provider = (
        request.app.state.transaction_service_provider
    )
    yield from provider()


TransactionServiceDep = Annotated[
    TransactionService,
    Depends(get_transaction_service),
]