"""Typed payloads exchanged between the agents and evaluation layer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """A source surfaced during research and carried through the content pipeline."""

    title: str = Field(min_length=1, description="Page title or source headline.")
    url: str = Field(min_length=8, description="Canonical HTTP(S) source URL.")
    published_date: str | None = Field(default=None, description="Publication date if provided.")
    relevance_note: str | None = Field(default=None, description="Which campaign point it informs.")


class ResearchFinding(BaseModel):
    """A research hook with rationale and one or more source references."""

    hook: str = Field(min_length=3)
    audience_relevance: str = Field(min_length=3)
    evidence_summary: str = Field(min_length=3)
    sources: list[SourceReference] = Field(min_length=1)


class ResearchBrief(BaseModel):
    """Structured research output from Trend Scout."""

    topic: str = Field(min_length=1)
    findings: list[ResearchFinding] = Field(min_length=3, max_length=3)
    caveats: list[str] = Field(default_factory=list)


class PlannedSlide(BaseModel):
    """A slide-level creative plan, before final copy is written."""

    slide_number: int = Field(ge=1)
    title: str = Field(min_length=2)
    visual_idea: str = Field(min_length=4)
    purpose: str = Field(min_length=3)


class CreativeBrief(BaseModel):
    """Structured carousel plan from Creative Director."""

    core_message: str = Field(min_length=3)
    slides: list[PlannedSlide] = Field(min_length=1, max_length=12)


class CampaignSlide(BaseModel):
    """A completed slide combining title, visual direction, and script."""

    slide_number: int = Field(ge=1)
    title: str = Field(min_length=2)
    visual_idea: str = Field(min_length=4)
    script: str = Field(min_length=3)


class CampaignDraft(BaseModel):
    """Typed, machine-evaluable campaign output from Content Copywriter."""

    topic: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    platforms: list[str] = Field(min_length=1)
    slides: list[CampaignSlide] = Field(min_length=1, max_length=12)
    caption: str = Field(min_length=5)
    hashtags: list[str] = Field(min_length=1)
    sources: list[SourceReference] = Field(min_length=1)
