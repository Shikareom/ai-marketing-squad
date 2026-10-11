"""Public workflow API for campaign generation."""

from __future__ import annotations

import logging
from typing import Any

from marketing_squad.team import create_marketing_squad

LOGGER = logging.getLogger(__name__)


def generate_campaign(
    topic: str,
    *,
    audience: str = "professionals and early-career job seekers",
    platforms: tuple[str, ...] = ("Instagram", "LinkedIn"),
    squad: Any | None = None,
) -> str:
    """Generate a research-backed campaign draft for a requested topic.

    Pass ``squad`` to inject a prebuilt team or a compatible test double.
    """
    clean_topic = topic.strip() if isinstance(topic, str) else ""
    if not clean_topic:
        raise ValueError("topic must not be empty.")
    invalid_platforms = not platforms or any(
        not isinstance(platform, str) or not platform.strip() for platform in platforms
    )
    if invalid_platforms:
        raise ValueError("Provide at least one non-empty platform.")

    clean_audience = audience.strip() if isinstance(audience, str) else ""
    team = squad or create_marketing_squad()
    prompt = f"""Create a research-backed social carousel.

Topic: {clean_topic}
Target audience: {clean_audience or 'general professional audience'}
Platforms: {', '.join(platforms)}

Requirements:
- Research three current hooks and show sources as clickable URLs.
- Clearly distinguish sourced facts from creative recommendations.
- Produce between the configured minimum and maximum slide count; use the validator.
- Keep each slide aligned across title, visual idea, and script.
- Finish with one caption and ten relevant hashtags.
- Never invent performance metrics, engagement guarantees, quotations, or source details.
- Write in natural, specific language rather than generic AI-style filler.
"""
    LOGGER.info("Generating a campaign draft for topic: %s", clean_topic)
    response = team.run(prompt)
    content = getattr(response, "content", None)
    return str(content if content is not None else response)
