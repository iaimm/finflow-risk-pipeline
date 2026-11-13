import os
from dataclasses import dataclass
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