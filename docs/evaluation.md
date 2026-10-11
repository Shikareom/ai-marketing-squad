# Evaluation protocol

## Purpose

The current evaluator checks campaign **structure**, not factual accuracy or business impact. Do not use a structural pass rate as a proxy for content quality, audience response, or conversion.

## Implemented objective checks

Given a normalized JSON payload, `evaluate_campaign` reports:

| Check/metric | Definition |
|---|---|
| Topic present | Topic is a non-empty string |
| Slide count in range | Number of slides falls within configured bounds (defaults: 7–10) |
| Slide-field completeness | Share of required slide fields that are non-empty: `slide_number`, `title`, `visual_idea`, `script` |
| Caption present | Caption is a non-empty string |
| Minimum hashtags met | At least ten string entries begin with `#` by default |
| HTTP source present | At least one source uses a valid HTTP(S) URL with a network location |

The output contains individual gates, derived counts, a completeness ratio, and an overall structural pass/fail.

## Run the checks

```bash
pytest
ruff check .
python scripts/evaluate_campaign.py path/to/campaign.json
```

The template in `examples/campaign_payload.template.json` is intentionally incomplete and is intended as a schema starting point.

## Recommended quality evaluation

For a more meaningful quality assessment, create a fixed set of representative topics and have reviewers independently rate each generated campaign on a 1–5 scale for:

- Source relevance and recency
- Factual grounding (claims are supported by linked sources)
- Audience relevance
- Clarity and naturalness
- Slide-to-slide narrative flow
- Specificity and usefulness of advice
- Brand/style fit

Record reviewer rubric, model identifier, run date, topic set, source links, failures, and whether content required major edits. Keep model-generated quality judgments separate from human ratings.

## Report results honestly

The original notebook does not establish measured baseline scores for factuality, relevance, copy quality, latency, token usage, cost per campaign, engagement, or conversion. These values must be collected through actual runs and documented with a repeatable protocol; they must not be guessed or backfilled.
