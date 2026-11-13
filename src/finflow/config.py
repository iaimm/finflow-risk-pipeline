import os
from dataclasses import dataclass, field
from pathlib import Path

VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


@dataclass(frozen=True, slots=True)
class Settings:
    log_level: str
    data_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        log_level = os.getenv(
            "FINFLOW_LOG_LEVEL",
            "INFO",
        ).upper()

        if log_level not in VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid FINFLOW_LOG_LEVEL: {log_level}"
            )

        data_dir = Path(
            os.getenv(
                "FINFLOW_DATA_DIR",
                "data/raw",
            )
        )

        return cls(
            log_level=log_level,
            data_dir=data_dir,
        )

@dataclass(frozen=True, slots=True)
class AuthSettings:
    jwt_secret_key: str = field(repr=False)
    access_token_expire_minutes: int
    demo_admin_password: str = field(repr=False)
    demo_viewer_password: str = field(repr=False)
    jwt_algorithm: str = "HS256"

    @classmethod
    def from_env(cls) -> "AuthSettings":
        secret_key = os.getenv(
            "FINFLOW_JWT_SECRET_KEY",
            "",
        )
        admin_password = os.getenv(
            "FINFLOW_DEMO_ADMIN_PASSWORD",
            "",
        )
        viewer_password = os.getenv(
            "FINFLOW_DEMO_VIEWER_PASSWORD",
            "",
        )

        if len(secret_key) < 32:
            raise ValueError(
                "FINFLOW_JWT_SECRET_KEY must contain "
                "at least 32 characters"
            )

        if not admin_password or not viewer_password:
            raise ValueError(
                "Demo user passwords must be configured"
            )

        expires_minutes = int(
            os.getenv(
                "FINFLOW_ACCESS_TOKEN_EXPIRE_MINUTES",
                "30",
            )
        )

        if expires_minutes < 1:
            raise ValueError(
                "Token expiration must be positive"
            )

        return cls(
            jwt_secret_key=secret_key,
            access_token_expire_minutes=expires_minutes,
            demo_admin_password=admin_password,
            demo_viewer_password=viewer_password,
        )