from pydantic import BaseModel, Field

from fastapi import APIRouter

from finflow.api.auth_dependencies import (
    AuthServiceDep,
    AuthSettingsDep,
)
from finflow.security import create_access_token


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    auth_service: AuthServiceDep,
    settings: AuthSettingsDep,
) -> TokenResponse:
    user = auth_service.authenticate(
        username=payload.username,
        password=payload.password,
    )

    token = create_access_token(
        username=user.username,
        settings=settings,
    )

    return TokenResponse(
        access_token=token,
        expires_in=(
            settings.access_token_expire_minutes * 60
        ),
    )