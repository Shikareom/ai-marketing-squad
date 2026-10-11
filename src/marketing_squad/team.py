"""Assemble and coordinate the specialized marketing agents."""

from __future__ import annotations

from typing import Any

from marketing_squad.agents import (
    build_content_copywriter,
    build_creative_director,
    build_trend_scout,
)
from marketing_squad.config import Settings, get_settings
from marketing_squad.tools import build_carousel_validation_tool


def create_marketing_squad(settings: Settings | None = None) -> Any:
    """Construct the Agno team without making a live model call.

    Provider imports are deferred by each builder so structural utilities and tests
    can be used without loading the provider integration until a team is requested.
    """
    try:
        from agno.models.openai import OpenAIChat
        from agno.team import Team
        from agno.team.mode import TeamMode
    except ImportError as exc:
        raise RuntimeError(
            "Agno dependencies are not installed. Run `pip install -e '.[dev]'`."
        ) from exc

    config = settings or get_settings()
    config.validate_api_keys()

    validation_tool = build_carousel_validation_tool(config)
    trend_scout = build_trend_scout(config)
    creative_director = build_creative_director(config, validation_tool)
    copywriter = build_content_copywriter(config)

    return Team(
        name="AI Marketing Squad",
        model=OpenAIChat(id=config.model_id),
        members=[trend_scout, creative_director, copywriter],
        mode=TeamMode.coordinate,
        instructions=[
            "Coordinate the workflow in this order: research, visual blueprint, final copy.",
            "Ask the Trend Scout for three current, source-backed hooks first.",
            "Pass research to the Creative Director and require validation of the slide count.",
            (
                "Pass the validated blueprint to the Content Copywriter "
                "without losing slide alignment."
            ),
            (
                "Return a polished Markdown deliverable with the topic, research summary, "
                "and source links;"
            ),
            (
                "then each slide's number, title, visual idea, and final script; "
                "then caption and hashtags."
            ),
            "Mark uncertain trend interpretations explicitly and do not fabricate source details.",
        ],
        markdown=True,
    )
