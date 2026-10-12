"""Creative Director: translate research into a coherent visual sequence."""

from __future__ import annotations

from typing import Any

from marketing_squad.config import Settings
from marketing_squad.models import CreativeBrief


def build_creative_director(settings: Settings, validation_tool: Any) -> Any:
    """Build the creative-planning agent with structured output and slide validation."""
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
    except ImportError as exc:
        raise RuntimeError(
            "Agent dependencies are missing. Install with pip install -e '.[dev]'."
        ) from exc

    return Agent(
        name="Creative Director",
        role="Turn validated research into a clear visual story and slide blueprint",
        model=OpenAIChat(id=settings.model_id),
        tools=[validation_tool],
        output_schema=CreativeBrief,
        instructions=[
            "Create a carousel blueprint based only on the supplied research brief.",
            f"Return between {settings.min_carousel_slides} and {settings.max_carousel_slides} slides, inclusive.",
            "Use the carousel validator and revise the plan if the slide count is out of range.",
            "Give every slide a sequential number, concise title, visual idea, and clear purpose.",
            "Use a strong opening, logical progression, practical takeaways, and a clear closing CTA.",
            "Do not imply that slide count guarantees reach, retention, or engagement.",
        ],
    )
