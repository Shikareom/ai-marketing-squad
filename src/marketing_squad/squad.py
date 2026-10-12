"""Public API for generating a review-ready marketing campaign."""

from __future__ import annotations

from collections.abc import Sequence

from marketing_squad.config import Settings
from marketing_squad.workflow import (
    AgentPipeline,
    WorkflowResult,
    run_campaign_workflow,
)


def generate_campaign_result(
    topic: str,
    *,
    audience: str = "professionals and early-career job seekers",
    platforms: Sequence[str] = ("Instagram", "LinkedIn"),
    pipeline: AgentPipeline | None = None,
    settings: Settings | None = None,
) -> WorkflowResult:
    """Generate a typed campaign and its structural evaluation report."""
    return run_campaign_workflow(
        topic,
        audience=audience,
        platforms=platforms,
        pipeline=pipeline,
        settings=settings,
    )


def generate_campaign(
    topic: str,
    *,
    audience: str = "professionals and early-career job seekers",
    platforms: Sequence[str] = ("Instagram", "LinkedIn"),
    pipeline: AgentPipeline | None = None,
    settings: Settings | None = None,
) -> str:
    """Generate and render the validated campaign as Markdown."""
    result = generate_campaign_result(
        topic,
        audience=audience,
        platforms=platforms,
        pipeline=pipeline,
        settings=settings,
    )
    return result.to_markdown()
