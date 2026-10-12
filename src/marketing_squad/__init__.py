"""AI Marketing Squad: research-backed marketing content workflows."""

from marketing_squad.squad import generate_campaign, generate_campaign_result
from marketing_squad.validation import (
    CarouselValidation,
    evaluate_campaign,
    validate_carousel_structure,
)

__all__ = [
    "CarouselValidation",
    "evaluate_campaign",
    "generate_campaign",
    "generate_campaign_result",
    "validate_carousel_structure",
]
__version__ = "1.1.0"
