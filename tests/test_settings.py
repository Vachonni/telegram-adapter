"""
Unit tests for telegram_adapter.config.settings.

These tests verify environment variable handling, enum validation, and settings loading.
"""

from importlib import reload

import pytest
from _pytest.monkeypatch import MonkeyPatch

import telegram_adapter.config.settings as config_mod
from telegram_adapter.config.settings import AppEnvEnum


def set_required_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "dummy")
    monkeypatch.setenv("TELEGRAM_NV_ID", "111")
    monkeypatch.setenv("TELEGRAM_GF_ID", "222")


def test_env_defaults_to_dev(monkeypatch: MonkeyPatch) -> None:
    """Should default to dev environment if APP_ENV is not set."""
    monkeypatch.delenv("APP_ENV", raising=False)
    set_required_env(monkeypatch)
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.DEV


def test_env_variables_are_loaded(monkeypatch: MonkeyPatch) -> None:
    """Should load settings from environment variables correctly."""
    monkeypatch.setenv("APP_ENV", "dev")
    set_required_env(monkeypatch)
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.DEV
    assert settings.log_level == "DEBUG"
    assert settings.TELEGRAM_BOT_TOKEN == "dummy"
    assert settings.TELEGRAM_NV_ID == 111
    assert settings.TELEGRAM_GF_ID == 222
    assert settings.allowed_ids == [111, 222]


def test_app_env_enum_variants(monkeypatch: MonkeyPatch) -> None:
    """Should correctly parse and validate all AppEnvEnum variants."""

    set_required_env(monkeypatch)

    monkeypatch.setenv("APP_ENV", "staging")
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.STAGING
    assert settings.log_level == "DEBUG"

    monkeypatch.setenv("APP_ENV", "prod")
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.PROD
    assert settings.log_level == "INFO"


@pytest.mark.parametrize("invalid_env", ["foo", "", "DEV "])
def test_invalid_app_env_raises(monkeypatch: MonkeyPatch, invalid_env: str) -> None:
    """Should raise ValueError for invalid APP_ENV values."""
    set_required_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", invalid_env)
    with pytest.raises(ValueError):
        reload(config_mod)
        _ = config_mod.settings
