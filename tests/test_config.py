"""Tests for environment-driven settings."""

import pytest

from marketing_squad.config import Settings


def test_settings_defaults(monkeypatch):
    for key in (
        "OPENAI_API_KEY",
        "TAVILY_API_KEY",
        "MARKETING_MODEL_ID",
        "MIN_CAROUSEL_SLIDES",
        "MAX_CAROUSEL_SLIDES",
    ):
        monkeypatch.delenv(key, raising=False)
    settings = Settings.from_env(load_dotenv_file=False)
    assert settings.model_id == "gpt-4o"
    assert (settings.min_carousel_slides, settings.max_carousel_slides) == (7, 10)


def test_settings_rejects_invalid_range(monkeypatch):
    monkeypatch.setenv("MIN_CAROUSEL_SLIDES", "10")
    monkeypatch.setenv("MAX_CAROUSEL_SLIDES", "7")
    with pytest.raises(ValueError, match="MAX_CAROUSEL_SLIDES"):
        Settings.from_env(load_dotenv_file=False)


def test_validate_api_keys_names_missing_values_without_printing_them():
    settings = Settings(None, None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY, TAVILY_API_KEY"):
        settings.validate_api_keys()
