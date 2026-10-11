"""Deterministic validation and lightweight campaign-structure evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class CarouselValidation:
    """Result of checking a requested carousel slide count."""

    valid: bool
    slide_count: int
    minimum: int
    maximum: int
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_carousel_structure(
    slide_count: int,
    minimum: int = 7,
    maximum: int = 10,
) -> CarouselValidation:
    """Check a slide count against the project's configurable design constraint.

    The 7–10 default is an implementation choice inherited from the original workflow;
    it is not a claim that this count guarantees engagement or business performance.
    """
    if isinstance(slide_count, bool) or not isinstance(slide_count, int):
        return CarouselValidation(
            False, -1, minimum, maximum, "slide_count must be an integer."
        )
    if minimum < 1 or maximum < minimum:
        raise ValueError("Require 1 <= minimum <= maximum.")
    valid = minimum <= slide_count <= maximum
    if valid:
        message = (
            f"Valid: {slide_count} slides is within the configured range "
            f"({minimum}–{maximum})."
        )
    else:
        message = (
            f"Invalid: {slide_count} slides is outside the configured range "
            f"({minimum}–{maximum})."
        )
    return CarouselValidation(valid, slide_count, minimum, maximum, message)


def evaluate_campaign(
    campaign: Mapping[str, Any],
    *,
    minimum_slides: int = 7,
    maximum_slides: int = 10,
    minimum_hashtags: int = 10,
) -> dict[str, Any]:
    """Evaluate objective checks on a structured campaign JSON payload.

    Expected shape:
      {"topic": str, "slides": [{"slide_number": int, "title": str,
       "visual_idea": str, "script": str}], "caption": str,
       "hashtags": [str], "sources": [{"url": str, "title": str?}]}

    This evaluator checks completeness and structure only. It cannot determine whether
    claims are true, trends are genuinely popular, or copy is effective; those require
    source review and a human quality rubric.
    """
    if not isinstance(campaign, Mapping):
        campaign = {}

    slides = campaign.get("slides") or []
    hashtags = campaign.get("hashtags") or []
    sources = campaign.get("sources") or []
    if not isinstance(slides, Sequence) or isinstance(slides, (str, bytes)):
        slides = []
    if not isinstance(hashtags, Sequence) or isinstance(hashtags, (str, bytes)):
        hashtags = []
    if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes)):
        sources = []

    required_fields = ("slide_number", "title", "visual_idea", "script")
    total_fields = len(slides) * len(required_fields)
    completed_fields = 0
    for slide in slides:
        if isinstance(slide, Mapping):
            for field in required_fields:
                value = slide.get(field)
                if value is not None and str(value).strip():
                    completed_fields += 1

    completeness = completed_fields / total_fields if total_fields else 0.0
    slide_count = len(slides)
    slide_count_check = validate_carousel_structure(slide_count, minimum_slides, maximum_slides)
    valid_hashtags = [
        item for item in hashtags
        if isinstance(item, str) and item.strip() and item.strip().startswith("#")
    ]
    source_urls = []
    for source in sources:
        if isinstance(source, Mapping):
            url = source.get("url")
        elif isinstance(source, str):
            url = source
        else:
            url = None
        if isinstance(url, str):
            parsed = urlparse(url.strip())
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                source_urls.append(url.strip())

    caption = campaign.get("caption")
    topic = campaign.get("topic")
    checks = {
        "topic_present": isinstance(topic, str) and bool(topic.strip()),
        "slide_count_in_range": slide_count_check.valid,
        "all_slide_fields_complete": bool(slides) and completeness == 1.0,
        "caption_present": isinstance(caption, str) and bool(caption.strip()),
        "minimum_hashtags_met": len(valid_hashtags) >= minimum_hashtags,
        "at_least_one_http_source": len(source_urls) >= 1,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "slide_count": slide_count,
            "slide_field_completeness": round(completeness, 4),
            "valid_hashtag_count": len(valid_hashtags),
            "http_source_count": len(source_urls),
        },
        "notes": [
            (
                "These are structural checks, not a score of factual accuracy "
                "or marketing effectiveness."
            ),
            "Sources must be reviewed manually to confirm they support the related trend claims.",
        ],
    }
