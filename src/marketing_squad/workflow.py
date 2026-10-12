"""Explicit, sequential orchestration for the multi-agent marketing workflow."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from marketing_squad.agents import (
    build_content_copywriter,
    build_creative_director,
    build_trend_scout,
)
from marketing_squad.config import Settings, get_settings
from marketing_squad.models import CampaignDraft, CreativeBrief, ResearchBrief
from marketing_squad.tools import build_carousel_validation_tool
from marketing_squad.validation import evaluate_campaign, validate_carousel_structure

TModel = TypeVar("TModel", bound=BaseModel)


class WorkflowOutputError(RuntimeError):
    """Raised when an agent does not return a valid structured response."""


class WorkflowValidationError(RuntimeError):
    """Raised when campaign structure still fails after a correction attempt."""

    def __init__(self, message: str, report: dict[str, Any]) -> None:
        super().__init__(message)
        self.report = report


@dataclass(frozen=True, slots=True)
class AgentPipeline:
    """Injectable set of role-specific agents used by the explicit workflow."""

    trend_scout: Any
    creative_director: Any
    copywriter: Any
    settings: Settings


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    """Final campaign plus the intermediate artifacts and structural evaluation."""

    research: ResearchBrief
    creative_brief: CreativeBrief
    campaign: CampaignDraft
    evaluation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "research": self.research.model_dump(mode="json"),
            "creative_brief": self.creative_brief.model_dump(mode="json"),
            "campaign": self.campaign.model_dump(mode="json"),
            "evaluation": self.evaluation,
        }

    def to_markdown(self) -> str:
        """Render the validated campaign as a review-ready Markdown document."""
        campaign = self.campaign
        sections = [
            f"# Campaign: {campaign.topic}",
            f"**Audience:** {campaign.audience}",
            f"**Platforms:** {', '.join(campaign.platforms)}",
            "",
            "## Slides",
        ]
        for slide in campaign.slides:
            sections.extend(
                [
                    "",
                    f"### Slide {slide.slide_number}: {slide.title}",
                    f"**Visual idea:** {slide.visual_idea}",
                    "",
                    slide.script,
                ]
            )
        sections.extend(["", "## Caption", "", campaign.caption, "", "## Hashtags", ""])
        sections.append(" ".join(campaign.hashtags))
        sections.extend(["", "## Sources", ""])
        for source in campaign.sources:
            url = source.url.strip()
            if url.startswith(("https://", "http://")):
                sections.append(f"- [{source.title}]({url})")
            else:
                sections.append(f"- {source.title} — {url}")
            if source.published_date:
                sections.append(f"  - Publication date: {source.published_date}")
        metrics = self.evaluation["metrics"]
        sections.extend(
            [
                "",
                "## Structural validation",
                "",
                f"- **Passed:** {self.evaluation['passed']}",
                f"- **Slide count:** {metrics['slide_count']}",
                f"- **Slide-field completeness:** {metrics['slide_field_completeness']:.0%}",
                f"- **Valid hashtags:** {metrics['valid_hashtag_count']}",
                f"- **HTTP source URLs:** {metrics['http_source_count']}",
                "",
                (
                    "> Structural checks do not establish factual accuracy, writing quality, "
                    "or marketing performance. Verify the cited sources and content before publishing."
                ),
            ]
        )
        return "\n".join(sections)


def build_agent_pipeline(settings: Settings | None = None) -> AgentPipeline:
    """Build all three real agents without making provider calls."""
    config = settings or get_settings()
    config.validate_api_keys()
    validation_tool = build_carousel_validation_tool(config)
    return AgentPipeline(
        trend_scout=build_trend_scout(config),
        creative_director=build_creative_director(config, validation_tool),
        copywriter=build_content_copywriter(config),
        settings=config,
    )


def run_campaign_workflow(
    topic: str,
    *,
    audience: str = "professionals and early-career job seekers",
    platforms: Sequence[str] = ("Instagram", "LinkedIn"),
    pipeline: AgentPipeline | None = None,
    settings: Settings | None = None,
    max_correction_attempts: int = 1,
) -> WorkflowResult:
    """Run research → creative plan → final copy in an explicitly enforced order."""
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("topic must not be empty.")
    if not isinstance(audience, str):
        raise TypeError("audience must be a string.")
    if isinstance(platforms, str) or not isinstance(platforms, Sequence) or not platforms:
        raise ValueError("Provide at least one non-empty platform.")
    normalized_platforms = tuple(
        platform.strip() for platform in platforms if isinstance(platform, str)
    )
    if len(normalized_platforms) != len(platforms) or any(
        not platform for platform in normalized_platforms
    ):
        raise ValueError("Every platform must be a non-empty string.")
    if isinstance(max_correction_attempts, bool) or not isinstance(max_correction_attempts, int):
        raise TypeError("max_correction_attempts must be an integer.")
    if max_correction_attempts < 0:
        raise ValueError("max_correction_attempts must be non-negative.")

    config = settings or (pipeline.settings if pipeline is not None else get_settings())
    agents = pipeline or build_agent_pipeline(config)
    clean_topic = topic.strip()
    clean_audience = audience.strip() or "general professional audience"

    # Stage 1 — parse the research artifact before passing it downstream.
    research_prompt = f"""Research brief
Topic: {clean_topic}
Audience: {clean_audience}
Platforms: {", ".join(normalized_platforms)}

Find exactly three current, useful content hooks using live search.
For each, provide evidence, audience relevance, and source references with real URLs.
Distinguish facts from advice, include available publication dates, and note uncertainty.
Do not invent source metadata or engagement/performance statistics.
"""
    research = _run_agent(agents.trend_scout, research_prompt, ResearchBrief)

    # Stage 2 — creative planning receives the actual structured research artifact.
    creative_prompt = _creative_prompt(
        clean_topic, clean_audience, normalized_platforms, research, config
    )
    creative_brief = _run_agent(agents.creative_director, creative_prompt, CreativeBrief)
    for _ in range(max_correction_attempts):
        creative_issues = _creative_issues(creative_brief, config)
        if not creative_issues:
            break
        creative_prompt = (
            _creative_prompt(clean_topic, clean_audience, normalized_platforms, research, config)
            + "\n\nCORRECTION REQUIRED. Fix these issues in the prior blueprint: "
            + "; ".join(creative_issues)
            + "\nPrior blueprint:\n"
            + creative_brief.model_dump_json(indent=2)
        )
        creative_brief = _run_agent(agents.creative_director, creative_prompt, CreativeBrief)
    creative_issues = _creative_issues(creative_brief, config)
    if creative_issues:
        raise WorkflowValidationError(
            "Creative Director did not produce a valid slide blueprint after correction.",
            {"passed": False, "issues": creative_issues},
        )

    # Stage 3 — copywriting receives both research and the validated blueprint.
    copy_prompt = _copywriter_prompt(
        clean_topic, clean_audience, normalized_platforms, research, creative_brief
    )
    campaign = _run_agent(agents.copywriter, copy_prompt, CampaignDraft)
    campaign = _apply_request_metadata(campaign, clean_topic, clean_audience, normalized_platforms)
    report = _evaluate(campaign, config)

    for _ in range(max_correction_attempts):
        if report["passed"]:
            break
        failed_checks = [name for name, passed in report["checks"].items() if not passed]
        copy_prompt = (
            _copywriter_prompt(
                clean_topic, clean_audience, normalized_platforms, research, creative_brief
            )
            + "\n\nCORRECTION REQUIRED. The previous draft failed these objective checks: "
            + ", ".join(failed_checks)
            + ". Return a corrected structured campaign that passes every check."
            + "\nPrevious campaign:\n"
            + campaign.model_dump_json(indent=2)
        )
        campaign = _run_agent(agents.copywriter, copy_prompt, CampaignDraft)
        campaign = _apply_request_metadata(
            campaign, clean_topic, clean_audience, normalized_platforms
        )
        report = _evaluate(campaign, config)

    if not report["passed"]:
        raise WorkflowValidationError(
            "Generated campaign still fails structural validation after correction.",
            report,
        )

    return WorkflowResult(
        research=research,
        creative_brief=creative_brief,
        campaign=campaign,
        evaluation=report,
    )


def _run_agent(agent: Any, prompt: str, schema: type[TModel]) -> TModel:
    response = agent.run(prompt)
    raw = getattr(response, "content", response)
    if isinstance(raw, schema):
        return raw
    if isinstance(raw, BaseModel):
        raw = raw.model_dump()
    if isinstance(raw, Mapping):
        try:
            return schema.model_validate(raw)
        except ValidationError as exc:
            raise WorkflowOutputError(
                f"Agent output did not match {schema.__name__}: {exc}"
            ) from exc
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return schema.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise WorkflowOutputError(
                f"Agent did not return valid structured {schema.__name__} output."
            ) from exc
    raise WorkflowOutputError(
        f"Agent returned {type(raw).__name__}; expected structured {schema.__name__}."
    )


def _creative_prompt(
    topic: str,
    audience: str,
    platforms: Sequence[str],
    research: ResearchBrief,
    settings: Settings,
) -> str:
    return f"""Create a slide-by-slide carousel blueprint.
Topic: {topic}
Audience: {audience}
Platforms: {", ".join(platforms)}
Required number of slides: {settings.min_carousel_slides}–{settings.max_carousel_slides}, inclusive.

Use this structured research output as your evidence base:
{research.model_dump_json(indent=2)}

Return a typed creative brief with one core message and slides containing a sequential
slide_number, concise title, specific visual_idea, and purpose. Use the slide-count
validation tool before returning the plan. Do not invent statistics or performance claims.
"""


def _copywriter_prompt(
    topic: str,
    audience: str,
    platforms: Sequence[str],
    research: ResearchBrief,
    creative_brief: CreativeBrief,
) -> str:
    return f"""Write the final social campaign using the research and approved creative plan.
Topic: {topic}
Audience: {audience}
Platforms: {", ".join(platforms)}

Research brief:
{research.model_dump_json(indent=2)}

Validated creative blueprint:
{creative_brief.model_dump_json(indent=2)}

Return structured campaign fields: topic, audience, platforms, slides, caption, hashtags,
and source references. Follow the approved slide numbering and visual ideas.
Include at least ten distinct hashtags beginning with # and preserve real source URLs.
Do not invent facts, dates, citations, quotes, or campaign-performance figures.
"""


def _creative_issues(brief: CreativeBrief, settings: Settings) -> list[str]:
    issues = []
    count = len(brief.slides)
    validation = validate_carousel_structure(
        count, settings.min_carousel_slides, settings.max_carousel_slides
    )
    if not validation.valid:
        issues.append(validation.message)
    expected_numbers = list(range(1, count + 1))
    actual_numbers = [slide.slide_number for slide in brief.slides]
    if actual_numbers != expected_numbers:
        issues.append(f"slide numbers must be sequential: expected {expected_numbers}")
    return issues


def _apply_request_metadata(
    campaign: CampaignDraft,
    topic: str,
    audience: str,
    platforms: Sequence[str],
) -> CampaignDraft:
    """Use the user's campaign brief as the source of truth for campaign metadata."""
    return campaign.model_copy(
        update={"topic": topic, "audience": audience, "platforms": list(platforms)}
    )


def _evaluate(campaign: CampaignDraft, settings: Settings) -> dict[str, Any]:
    return evaluate_campaign(
        campaign.model_dump(mode="json"),
        minimum_slides=settings.min_carousel_slides,
        maximum_slides=settings.max_carousel_slides,
        minimum_hashtags=10,
    )
