from pathlib import Path

import pytest

from finflow.config import Settings


def test_load_settings_from_environment(monkeypatch):
    monkeypatch.setenv("FINFLOW_LOG_LEVEL", "debug")
    monkeypatch.setenv(
        "FINFLOW_DATA_DIR",
        "data/test-output",
    )

    settings = Settings.from_env()

    assert settings.log_level == "DEBUG"
    assert settings.data_dir == Path("data/test-output")


def test_reject_invalid_log_level(monkeypatch):
    monkeypatch.setenv("FINFLOW_LOG_LEVEL", "LOUD")

    with pytest.raises(ValueError, match="Invalid"):
        Settings.from_env()