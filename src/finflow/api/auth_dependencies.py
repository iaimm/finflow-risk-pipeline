from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from finflow.config import AuthSettings
from finflow.exceptions import (
    AuthenticationError,
    AuthorizationError,
)
from finflow.models.entities import User
from finflow.security import decode_access_token
from finflow.services.auth_service import AuthService


bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def get_auth_settings(request: Request) -> AuthSettings:
    return request.app.state.auth_settings


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]

AuthSettingsDep = Annotated[
    AuthSettings,
    Depends(get_auth_settings),
]


def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> User:
    if credentials is None:
        raise AuthenticationError(
            "Authentication credentials were not provided"
        )

    settings = get_auth_settings(request)

    try:
        username = decode_access_token(
            credentials.credentials,
            settings,
        )
    except (
        jwt.InvalidTokenError,
        AuthenticationError,
    ) as exc:
        raise AuthenticationError(
            "Invalid or expired token"
        ) from exc

    user = get_auth_service(request).get_user(username)

    if user is None or user.disabled:
        raise AuthenticationError(
            "Invalid or expired token"
        )

    return user


CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
]


def require_role(required_role: str):
    def check_role(user: CurrentUserDep) -> User:
        if required_role not in user.roles:
            raise AuthorizationError(
                "Insufficient permissions"
            )
        return user

    return check_role


AdminUserDep = Annotated[
    User,
    Depends(require_role("admin")),
]