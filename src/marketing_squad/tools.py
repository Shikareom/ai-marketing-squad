"""Small, deterministic tools made available to the agents."""

from __future__ import annotations

from typing import Any

from marketing_squad.config import Settings
from marketing_squad.validation import validate_carousel_structure


def build_carousel_validation_tool(settings: Settings) -> Any:
    """Wrap the deterministic slide-count validator as an Agno tool."""
    try:
        from agno.tools import tool
    except ImportError as exc:
        raise RuntimeError(
            "Agent dependencies are missing. Install with pip install -e '.[dev]'."
        ) from exc

    @tool(
        name="validate_carousel_slide_count",
        title="Carousel Structure Validator",
        description=(
            "Check a planned carousel count against configured minimum and maximum. "
            "This validates count only, not content quality."
        ),
    )
    def validate_carousel_slide_count(slide_count: int) -> str:
        """Validate the planned carousel count against the configured range."""
        result = validate_carousel_structure(
            slide_count,
            minimum=settings.min_carousel_slides,
            maximum=settings.max_carousel_slides,
        )
        return result.message

    return validate_carousel_slide_count
