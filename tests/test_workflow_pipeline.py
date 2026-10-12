"""Offline tests for enforced stage order, retries, and agent construction."""

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
from marketing_squad.workflow import (
    AgentPipeline,
    WorkflowOutputError,
    WorkflowValidationError,
    build_agent_pipeline,
    run_campaign_workflow,
)


SOURCE = SourceReference(
    title="Example research source",
    url="https://example.com/research",
    published_date="2026-01-01",
    relevance_note="Supports the example research point.",
)


def make_research():
    return ResearchBrief(
        topic="Career planning",
        findings=[
            ResearchFinding(
                hook=f"Research hook {index}",
                audience_relevance="This matters to early-career professionals.",
                evidence_summary="A short test evidence summary from a source.",
                sources=[SOURCE],
            )
            for index in range(1, 4)
        ],
    )


def make_blueprint(count=7, *, bad_numbers=False):
    return CreativeBrief(
        core_message="Make career advice specific, practical, and evidence-aware.",
        slides=[
            PlannedSlide(
                slide_number=index + (1 if bad_numbers else 0),
                title=f"Slide {index}",
                visual_idea="A clear headline and one visual takeaway.",
                purpose="Explain one practical point to the target audience.",
            )
            for index in range(1, count + 1)
        ],
    )


def make_campaign(count=7, hashtags=10):
    return CampaignDraft(
        topic="Placeholder topic",
        audience="Placeholder audience",
        platforms=["Instagram"],
        slides=[
            CampaignSlide(
                slide_number=index,
                title=f"Slide {index}",
                visual_idea="A clear headline and one visual takeaway.",
                script="Explain one practical point and offer a concrete next step.",
            )
            for index in range(1, count + 1)
        ],
        caption="A practical guide to make your next step clearer.",
        hashtags=[f"#career{index}" for index in range(hashtags)],
        sources=[SOURCE],
    )


class FakeAgent:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.prompts = []

    def run(self, prompt):
        self.prompts.append(prompt)
        result = self.responses.pop(0)
        return type("Response", (), {"content": result})()


def make_pipeline(*, blueprints=None, campaigns=None, research=None):
    research_agent = FakeAgent(*(research or [make_research()]))
    creative_agent = FakeAgent(*(blueprints or [make_blueprint()]))
    copywriter = FakeAgent(*(campaigns or [make_campaign()]))
    pipeline = AgentPipeline(
        trend_scout=research_agent,
        creative_director=creative_agent,
        copywriter=copywriter,
        settings=Settings(None, None),
    )
    return pipeline, research_agent, creative_agent, copywriter


def test_pipeline_enforces_research_then_creative_then_copywriting():
    pipeline, research_agent, creative_agent, copywriter = make_pipeline()
    result = run_campaign_workflow("Career planning", audience="students", pipeline=pipeline)
    assert result.evaluation["passed"] is True
    assert len(research_agent.prompts) == 1
    assert len(creative_agent.prompts) == 1
    assert len(copywriter.prompts) == 1
    assert "Research hook 1" in creative_agent.prompts[0]
    assert "Slide 7" in copywriter.prompts[0]
    assert "Career planning" in copywriter.prompts[0]


def test_pipeline_retries_invalid_blueprint_before_copywriting():
    pipeline, _, creative_agent, copywriter = make_pipeline(
        blueprints=[make_blueprint(6), make_blueprint(7)]
    )
    result = run_campaign_workflow("Career planning", pipeline=pipeline)
    assert result.evaluation["passed"] is True
    assert len(creative_agent.prompts) == 2
    assert "CORRECTION REQUIRED" in creative_agent.prompts[1]
    assert len(copywriter.prompts) == 1


def test_pipeline_retries_invalid_campaign():
    pipeline, _, _, copywriter = make_pipeline(campaigns=[make_campaign(hashtags=3), make_campaign()])
    result = run_campaign_workflow("Career planning", pipeline=pipeline)
    assert result.evaluation["passed"] is True
    assert len(copywriter.prompts) == 2
    assert "minimum_hashtags_met" in copywriter.prompts[1]


def test_pipeline_raises_when_blueprint_remains_invalid():
    pipeline, _, creative_agent, _ = make_pipeline(
        blueprints=[make_blueprint(6), make_blueprint(6)]
    )
    with pytest.raises(WorkflowValidationError, match="did not produce a valid slide blueprint"):
        run_campaign_workflow("Career planning", pipeline=pipeline)
    assert len(creative_agent.prompts) == 2


def test_pipeline_rejects_blank_topic_and_invalid_platforms():
    pipeline, *_ = make_pipeline()
    with pytest.raises(ValueError, match="topic must not be empty"):
        run_campaign_workflow("  ", pipeline=pipeline)
    with pytest.raises(ValueError, match="at least one non-empty platform"):
        run_campaign_workflow("Okay", platforms=(), pipeline=pipeline)
    with pytest.raises(ValueError, match="non-empty string"):
        run_campaign_workflow("Okay", platforms=("LinkedIn", " "), pipeline=pipeline)


def test_agent_construction_works_without_network_calls(monkeypatch):
    """Catch incorrect Agno imports and constructors without spending API credits."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key-not-valid")
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key-not-valid")
    settings = Settings.from_env()
    pipeline = build_agent_pipeline(settings)
    assert pipeline.trend_scout is not None
    assert pipeline.creative_director is not None
    assert pipeline.copywriter is not None


def test_invalid_agent_output_is_reported():
    pipeline, *_ = make_pipeline(research=["not json"])
    with pytest.raises(WorkflowOutputError, match="valid structured ResearchBrief"):
        run_campaign_workflow("Career planning", pipeline=pipeline)
