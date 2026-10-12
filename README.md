# AI Marketing Squad

[![Tests](https://github.com/Shikareom/ai-marketing-squad/actions/workflows/tests.yml/badge.svg)](https://github.com/Shikareom/ai-marketing-squad/actions/workflows/tests.yml)

A research-informed multi-agent workflow that turns a campaign brief into a structured social-content draft, including research references, a creative plan, final copy, and objective validation.

## What it does

1. **Trend Scout** researches three current hooks and returns evidence summaries with source references.
2. **Creative Director** turns the research into a slide-by-slide plan and validates slide count and numbering.
3. **Content Copywriter** writes the slide scripts, caption, hashtags, and source references.

The stages run sequentially in Python. Each stage returns a typed Pydantic model that is validated before the next stage receives it. Invalid creative plans and final drafts receive at most one correction attempt by default.

This is a working prototype for human-reviewed drafts. It does not automatically publish social posts or measure campaign performance.

## Architecture

```text
src/marketing_squad/
├── agents/
│   ├── trend_scout.py
│   ├── creative_director.py
│   └── content_copywriter.py
├── models.py       # Typed Pydantic stage contracts
├── workflow.py     # Sequential orchestration and correction
├── squad.py        # Public Python API
├── cli.py          # Command-line interface
├── config.py       # Environment settings and secrets
├── tools.py        # Carousel validation tool
└── validation.py   # Deterministic structure checks
```

See [docs/architecture.md](docs/architecture.md) for stage contracts, failure behavior, and trust boundaries.

## Quick start

Requirements: Python 3.10+, an OpenAI API key, and a Tavily API key.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and add your keys:

```dotenv
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
MARKETING_MODEL_ID=gpt-4o
MIN_CAROUSEL_SLIDES=7
MAX_CAROUSEL_SLIDES=10
```

Never commit `.env` or real API keys.

## Generate a campaign

```bash
marketing-squad --topic "How to explain career gaps" --audience "early-career professionals" --platforms Instagram LinkedIn
```

Save the structured result (research, blueprint, campaign, and evaluation) as JSON while also printing Markdown:

```bash
marketing-squad --topic "Build a strong project portfolio" --output artifacts/portfolio-campaign.json
```

Use the Python API:

```python
from marketing_squad import generate_campaign, generate_campaign_result

markdown = generate_campaign("How to explain career gaps")
print(markdown)

result = generate_campaign_result("How to explain career gaps")
print(result.evaluation)
print(result.campaign.model_dump(mode="json"))
```

Running a campaign makes live model and search requests and may incur provider charges. Automated tests use fake agents or test credentials and do not call the live model or search APIs.

## Validation and results

The final campaign is checked for:

- Slide count within the configured range (default 7–10)
- Sequential slide numbering
- Complete slide number, title, visual idea, and script fields
- Non-empty topic and caption
- At least ten distinct hashtags beginning with `#`
- At least one well-formed HTTP(S) source URL

The evaluator reports individual checks and structural counts. It does **not** establish factual accuracy, source relevance, naturalness, originality, or marketing effectiveness. No measured improvements in engagement, conversions, speed, or time saved are claimed. See [docs/evaluation.md](docs/evaluation.md) for a repeatable human-review protocol.

Run the automated checks:

```bash
pytest
ruff check .
```

Evaluate either a campaign JSON object or the workflow JSON saved with `--output`:

```bash
python scripts/evaluate_campaign.py path/to/campaign.json
```

## Security and responsible use

- Verify cited pages and publication dates; search snippets are not evidence by themselves.
- Treat retrieved content and model output as untrusted until reviewed.
- Check factual nuance, audience fit, sensitive claims, and copyright/licensing before publishing.
- Do not auto-publish generated content without human review.
- Use provider-side spending limits and keep keys out of code, notebooks, logs, and issue comments.

See [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
