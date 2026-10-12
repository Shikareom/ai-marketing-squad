"""Contract tests for the public workflow API without live provider calls."""

import pytest

from marketing_squad.config import Settings
from marketing_squad.models import (
    CampaignDraft,
    CampaignSlide,
    CreativeBrief,
    PlannedSlide,
    ResearchBrief,
    ResearchFinding,
    SourceReference,
)
from marketing_squad.squad import generate_campaign
from marketing_squad.workflow import AgentPipeline

SOURCE = SourceReference(title="Example source", url="https://example.com/research")


def _research():
    return ResearchBrief(
        topic="Build a project portfolio",
        findings=[
            ResearchFinding(
                hook=f"Portfolio hook {number}",
                audience_relevance="Useful for students",
                evidence_summary="A source-backed note used only in testing.",
                sources=[SOURCE],
            )
            for number in range(1, 4)
        ],
    )


def _blueprint():
    return CreativeBrief(
        core_message="A portfolio should prove skills with evidence.",
        slides=[
            PlannedSlide(
                slide_number=number,
                title=f"Slide {number}",
                visual_idea="One clear visual idea for this slide.",
                purpose="Explain one useful takeaway.",
            )
            for number in range(1, 8)
        ],
    )


def _campaign():
    return CampaignDraft(
        topic="Build a project portfolio",
        audience="students",
        platforms=["LinkedIn", "Instagram"],
        slides=[
            CampaignSlide(
                slide_number=number,
                title=f"Slide {number}",
                visual_idea="One clear visual idea for this slide.",
                script="Explain one useful takeaway with a concrete next step.",
            )
            for number in range(1, 8)
        ],
        caption="A practical portfolio guide for students.",
        hashtags=[f"#portfolio{number}" for number in range(10)],
        sources=[SOURCE],
    )


class FakeAgent:
    def __init__(self, result):
        self.result = result
        self.prompts = []

    def run(self, prompt):
        self.prompts.append(prompt)
        return type("Response", (), {"content": self.result})()


def _pipeline():
    return AgentPipeline(
        trend_scout=FakeAgent(_research()),
        creative_director=FakeAgent(_blueprint()),
        copywriter=FakeAgent(_campaign()),
        settings=Settings(None, None),
    )


def test_public_api_returns_review_ready_markdown():
    result = generate_campaign(
        "Build a project portfolio",
        audience="students",
        platforms=("LinkedIn", "Instagram"),
        pipeline=_pipeline(),
    )
    assert "# Campaign: Build a project portfolio" in result
    assert "## Structural validation" in result
    assert "https://example.com/research" in result
    assert "## Hashtags" in result


def test_public_api_rejects_blank_topic():
    with pytest.raises(ValueError, match="topic must not be empty"):
        generate_campaign("  ", pipeline=_pipeline())


def test_public_api_rejects_empty_platforms():
    with pytest.raises(ValueError, match="at least one non-empty platform"):
        generate_campaign("Valid topic", platforms=(), pipeline=_pipeline())
