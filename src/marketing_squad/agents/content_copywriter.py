"""Content Copywriter: turn an approved blueprint into natural social copy."""

from __future__ import annotations

from typing import Any

from marketing_squad.config import Settings


def build_content_copywriter(settings: Settings) -> Any:
    """Build the final-copy agent."""
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
    except ImportError as exc:
        raise RuntimeError(
            "Agent dependencies are missing. Install the project with `pip install -e '.[dev]'`."
        ) from exc

    return Agent(
        name="Content Copywriter",
        role="Write clear, natural and audience-aware social content",
        model=OpenAIChat(id=settings.model_id),
        instructions=[
            "Write conversational, specific copy that sounds like a knowledgeable human editor.",
            "Avoid filler, generic hype, repetitive sentence patterns, and unsupported promises.",
            "Keep each slide easy to read and aligned with its visual idea.",
            "Preserve factual nuance; never invent statistics, quotes, sources, or outcomes.",
            "Provide one caption and ten relevant hashtags; do not force irrelevant keywords.",
        ],
    )
