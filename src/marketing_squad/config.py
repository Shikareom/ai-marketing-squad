"""Configuration handling for the marketing squad.

Secrets are read from environment variables (normally populated from a local .env file).
This module never prints or logs API-key values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded from the environment."""

    openai_api_key: str | None
    tavily_api_key: str | None
    model_id: str = "gpt-4o"
    min_carousel_slides: int = 7
    max_carousel_slides: int = 10

    @classmethod
    def from_env(cls, *, load_dotenv_file: bool = True) -> Settings:
        """Load settings without exposing secret values."""
        if load_dotenv_file:
            load_dotenv()

        settings = cls(
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            tavily_api_key=os.getenv("TAVILY_API_KEY") or None,
            model_id=os.getenv("MARKETING_MODEL_ID", "gpt-4o").strip() or "gpt-4o",
            min_carousel_slides=_read_int("MIN_CAROUSEL_SLIDES", 7),
            max_carousel_slides=_read_int("MAX_CAROUSEL_SLIDES", 10),
        )
        if settings.min_carousel_slides < 1:
            raise ValueError("MIN_CAROUSEL_SLIDES must be at least 1.")
        if settings.max_carousel_slides < settings.min_carousel_slides:
            raise ValueError("MAX_CAROUSEL_SLIDES must be >= MIN_CAROUSEL_SLIDES.")
        return settings

    def validate_api_keys(self) -> None:
        """Raise a helpful error when required credentials are missing."""
        missing = []
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.tavily_api_key:
            missing.append("TAVILY_API_KEY")
        if missing:
            raise ValueError(
                "Missing required environment variable(s): "
                + ", ".join(missing)
                + ". Copy .env.example to .env and add your keys."
            )


def _read_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}.") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached environment settings for application code."""
    return Settings.from_env()
