from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from finflow.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def handle_validation_error(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    async def handle_not_found_error(
        request: Request,
        exc: NotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ConflictError)
    async def handle_conflict_error(
        request: Request,
        exc: ConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )


    @app.exception_handler(AuthenticationError)
    async def handle_authentication_error(
        request: Request,
        exc: AuthenticationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )


    @app.exception_handler(AuthorizationError)
    async def handle_authorization_error(
        request: Request,
        exc: AuthorizationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)},
        )