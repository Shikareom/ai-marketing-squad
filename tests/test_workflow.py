"""Tests for the public workflow API without making provider calls."""

import pytest

from marketing_squad.squad import generate_campaign


class FakeResponse:
    content = "A generated campaign draft."


class FakeTeam:
    def __init__(self):
        self.prompt = None

    def run(self, prompt: str):
        self.prompt = prompt
        return FakeResponse()


def test_generate_campaign_uses_injected_team():
    team = FakeTeam()
    result = generate_campaign(
        "  Build a project portfolio  ",
        audience="students",
        platforms=("LinkedIn", "Instagram"),
        squad=team,
    )
    assert result == "A generated campaign draft."
    assert "Topic: Build a project portfolio" in team.prompt
    assert "Target audience: students" in team.prompt
    assert "Platforms: LinkedIn, Instagram" in team.prompt
    assert "clickable URLs" in team.prompt


def test_generate_campaign_falls_back_for_blank_audience():
    team = FakeTeam()
    generate_campaign("Portfolio planning", audience="  ", squad=team)
    assert "Target audience: general professional audience" in team.prompt


def test_generate_campaign_rejects_empty_topic():
    with pytest.raises(ValueError, match="topic must not be empty"):
        generate_campaign("   ", squad=FakeTeam())


def test_generate_campaign_rejects_empty_platforms():
    with pytest.raises(ValueError, match="at least one non-empty platform"):
        generate_campaign("Portfolio planning", platforms=(), squad=FakeTeam())


def test_generate_campaign_rejects_blank_platform_name():
    with pytest.raises(ValueError, match="at least one non-empty platform"):
        generate_campaign("Portfolio planning", platforms=("LinkedIn", " "), squad=FakeTeam())
