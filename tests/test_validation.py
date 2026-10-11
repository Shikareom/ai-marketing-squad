from marketing_squad.validation import evaluate_campaign, validate_carousel_structure


def test_carousel_validator_accepts_configured_range():
    result = validate_carousel_structure(8)
    assert result.valid is True
    assert result.minimum == 7
    assert result.maximum == 10


def test_carousel_validator_rejects_out_of_range():
    assert validate_carousel_structure(6).valid is False
    assert validate_carousel_structure(11).valid is False


def test_carousel_validator_rejects_non_integer():
    assert validate_carousel_structure(8.5).valid is False
    assert validate_carousel_structure(True).valid is False


def _valid_campaign():
    return {
        "topic": "How to explain career gaps",
        "slides": [
            {
                "slide_number": number,
                "title": f"Slide {number}",
                "visual_idea": "A clean, readable visual with one key takeaway.",
                "script": "Use a truthful, specific example and avoid overclaiming.",
            }
            for number in range(1, 8)
        ],
        "caption": "A practical guide to explaining a career gap with clarity.",
        "hashtags": [f"#tag{number}" for number in range(10)],
        "sources": [{"url": "https://example.com/research", "title": "Example source"}],
    }


def test_evaluate_campaign_passes_when_structural_checks_are_met():
    report = evaluate_campaign(_valid_campaign())
    assert report["passed"] is True
    assert report["metrics"]["slide_count"] == 7
    assert report["metrics"]["slide_field_completeness"] == 1.0
    assert report["metrics"]["valid_hashtag_count"] == 10
    assert report["metrics"]["http_source_count"] == 1


def test_evaluate_campaign_flags_missing_fields_and_sources():
    campaign = _valid_campaign()
    campaign["slides"][0]["visual_idea"] = "  "
    campaign["sources"] = [{"url": "not-a-url"}]
    report = evaluate_campaign(campaign)
    assert report["passed"] is False
    assert report["checks"]["all_slide_fields_complete"] is False
    assert report["checks"]["at_least_one_http_source"] is False
