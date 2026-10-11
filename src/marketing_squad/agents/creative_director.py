"""Creative Director: translate research into a coherent visual sequence."""

from __future__ import annotations

from typing import Any

from marketing_squad.config import Settings


def build_creative_director(settings: Settings, validation_tool: Any) -> Any:
    """Build the creative-planning agent with the configured slide validator."""
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
    except ImportError as exc:
        raise RuntimeError(
            "Agent dependencies are missing. Install the project with `pip install -e '.[dev]'`."
        ) from exc

    return Agent(
        name="Creative Director",
        role="Turn validated research into a clear visual story and slide blueprint",
        model=OpenAIChat(id=settings.model_id),
        tools=[validation_tool],
        instructions=[
            "Create a slide-by-slide visual plan grounded in the research handed to you.",
            (
                "Use the carousel validator and revise the plan if the count is outside "
                "the configured range."
            ),
            (
                "Give every slide a clear purpose, title, and specific visual direction "
                "for a designer."
            ),
            (
                "Use a strong opening, logical progression, practical takeaways, "
                "and a clear closing call to action."
            ),
            "Do not imply that a slide count guarantees reach, retention, or engagement.",
        ],
    )
