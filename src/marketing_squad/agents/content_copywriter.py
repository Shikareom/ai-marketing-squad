"""Content Copywriter: turn an approved blueprint into natural social copy."""

from __future__ import annotations

from typing import Any

from marketing_squad.config import Settings
from marketing_squad.models import CampaignDraft


def build_content_copywriter(settings: Settings) -> Any:
    """Build the final-copy agent with a machine-validated output schema."""
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
    except ImportError as exc:
        raise RuntimeError(
            "Agent dependencies are missing. Install with pip install -e '.[dev]'."
        ) from exc

    return Agent(
        name="Content Copywriter",
        role="Write clear, natural and audience-aware social content",
        model=OpenAIChat(id=settings.model_id),
        output_schema=CampaignDraft,
        instructions=[
            "Write conversational, specific copy that sounds like a knowledgeable human editor.",
            "Avoid filler, generic hype, repetitive patterns, and unsupported promises.",
            "Follow the approved blueprint and preserve its slide sequence and visual ideas.",
            "Each slide must have a useful title, visual idea, and complete script.",
            "Copy source references from research; never invent facts, dates, sources or outcomes.",
            "Include at least ten distinct, relevant hashtags beginning with #.",
            "Return only the structured campaign fields requested by the output schema.",
        ],
    )
