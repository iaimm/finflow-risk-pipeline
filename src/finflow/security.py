from datetime import datetime, timedelta, timezone

import jwt

from pwdlib import PasswordHash

from finflow.config import AuthSettings
from finflow.exceptions import AuthenticationError


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    return password_hasher.verify(
        plain_password,
        password_hash,
    )


def create_access_token(
    username: str,
    settings: AuthSettings,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.access_token_expire_minutes
        )

    payload = {
        "sub": username,
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
    settings: AuthSettings,
) -> str:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={
            "require": ["sub", "iat", "exp"],
        },
    )

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    username = payload.get("sub")

    if not isinstance(username, str) or not username:
        raise AuthenticationError("Invalid token subject")

    return username