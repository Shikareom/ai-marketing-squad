# Evaluation protocol

## What is measured in code

The runtime performs deterministic structure checks on a Pydantic campaign artifact:

| Check | Rule |
|---|---|
| Topic present | Non-empty topic string |
| Slide count in range | Default 7–10, configurable through environment variables |
| Sequential numbers | Slide numbers equal 1 through slide count in order |
| Slide completeness | Every slide has non-empty slide number, title, visual idea, and script |
| Caption present | Non-empty caption |
| Hashtags | At least ten distinct strings beginning with `#` |
| Source URL | At least one HTTP(S) URL with a network location |

The workflow retries the creative stage once if the blueprint count or numbering is invalid. It retries the copywriting stage once if the final campaign fails objective structural checks. If it still fails, the workflow raises a validation error and does not report success.

## Run the automated checks

```bash
pytest
ruff check .
python scripts/evaluate_campaign.py path/to/campaign.json
```

The evaluator accepts either a normalized campaign object or the workflow JSON emitted by the CLI's `--output` option, which contains a `campaign` object.

## What is not measured

Structural checks do not evaluate factual accuracy, source support, source freshness, originality, naturalness, audience relevance, brand fit, or slide-to-slide storytelling. The project has no verified benchmark scores for latency, token use, API cost, engagement, or conversion. Do not infer performance from the count of unit tests or structural passes.

## Recommended manual quality study

Create a fixed test set of representative campaign topics. For each run, store a timestamp, configured model, prompt/version, output artifacts, sources, any correction attempt, and latency/cost when providers expose those data. Ask at least two reviewers to independently rate each campaign from 1–5 for:

- Source relevance and recency
- Factual grounding against linked pages
- Audience relevance
- Clarity and naturalness
- Narrative flow
- Specificity and usefulness
- Stylistic fit

Report the number of campaigns reviewed, the rubric, inter-reviewer disagreement, and examples of failure. Keep reviewer scores separate from automated structural checks. Only publish metrics collected through a repeatable protocol.
