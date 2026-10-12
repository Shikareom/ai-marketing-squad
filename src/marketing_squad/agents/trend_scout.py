"""Trend Scout: gather timely hooks and evidence from live search."""

from __future__ import annotations

from typing import Any

from marketing_squad.config import Settings
from marketing_squad.models import ResearchBrief


def build_trend_scout(settings: Settings) -> Any:
    """Build the research agent. Provider imports are deferred until runtime."""
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.tools.tavily import TavilyTools
    except ImportError as exc:
        raise RuntimeError(
            "Agent dependencies are missing. Install with pip install -e '.[dev]'."
        ) from exc

    return Agent(
        name="Trend Scout",
        role="Research current audience-relevant marketing hooks using live search",
        model=OpenAIChat(id=settings.model_id),
        tools=[TavilyTools()],
        output_schema=ResearchBrief,
        instructions=[
            "Research exactly three current and audience-relevant hooks using live search.",
            "For each finding, include evidence, audience relevance, and source references with real URLs.",
            "Separate source facts from recommendations. Never invent source titles, dates or URLs.",
            "If evidence is weak or a publication date is unavailable, say so explicitly.",
            "Do not invent engagement or campaign-performance statistics.",
        ],
    )
