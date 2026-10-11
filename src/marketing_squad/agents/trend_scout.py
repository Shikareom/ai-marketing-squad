"""Trend Scout: gather timely hooks and evidence from live search."""

from __future__ import annotations

from typing import Any

from marketing_squad.config import Settings


def build_trend_scout(settings: Settings) -> Any:
    """Build the research agent. Provider imports are deferred until runtime."""
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.tools.tavily import TavilyTools
    except ImportError as exc:
        raise RuntimeError(
            "Agent dependencies are missing. Install the project with `pip install -e '.[dev]'`."
        ) from exc

    return Agent(
        name="Trend Scout",
        role="Research current audience-relevant marketing hooks using live search",
        model=OpenAIChat(id=settings.model_id),
        tools=[TavilyTools()],
        instructions=[
            "Research three timely, audience-relevant hooks for the requested topic.",
            (
                "Use live search results for current-trend claims; "
                "do not present model memory as current evidence."
            ),
            "For every hook, include the source title, URL, and any available publication date.",
            "Separate observed source facts from your own recommendations or hypotheses.",
            "If evidence is weak or a date is unavailable, say so rather than inventing it.",
        ],
    )
