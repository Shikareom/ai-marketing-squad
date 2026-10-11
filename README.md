# AI Marketing Squad

A modular multi-agent workflow for research-backed social marketing content.

## Overview

The project coordinates three specialized agents: **Trend Scout** researches current hooks and source URLs, **Creative Director** plans the carousel structure and visual direction, and **Content Copywriter** drafts slide copy, a caption, and hashtags. Agno coordinates the team, OpenAI provides the chat model, and Tavily provides web search.

This is a working prototype. Generated content requires human review. No live content-quality or marketing-performance baselines have been measured, and this repository does not claim engagement, conversion, or time-savings results.

## Workflow

1. Provide a topic, audience, and target platforms.
2. Research timely hooks and request source URLs.
3. Produce a slide-by-slide visual blueprint.
4. Validate the configured carousel slide-count range (default 7–10).
5. Generate slide scripts, caption, and hashtags.
6. Review all sources and content before publishing.

## Quick start

Requires Python 3.10+, an OpenAI API key, and a Tavily API key.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and add your credentials:

```dotenv
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
MARKETING_MODEL_ID=gpt-4o
MIN_CAROUSEL_SLIDES=7
MAX_CAROUSEL_SLIDES=10
```

Never commit `.env` or real API keys.

Generate a draft:

```bash
marketing-squad --topic "How to explain career gaps" --audience "early-career professionals" --platforms Instagram LinkedIn
```

Or:

```bash
python -m marketing_squad.cli --topic "Building a strong project portfolio"
```

## Architecture

```text
src/marketing_squad/
├── agents/
│   ├── trend_scout.py          # Research and trend sources
│   ├── creative_director.py    # Carousel narrative and visuals
│   └── content_copywriter.py  # Slide copy, caption, hashtags
├── cli.py                      # Command-line interface
├── config.py                   # Environment-driven settings
├── squad.py                    # Public generation API
├── team.py                     # Agent coordination
├── tools.py                    # Custom tools
└── validation.py               # Structural validation/evaluation
```

Other key directories: `notebooks/` holds a cleaned Jupyter walkthrough; `tests/` contains deterministic tests; `docs/` contains architecture and evaluation notes; `scripts/` contains the campaign structure evaluator; `examples/` contains a JSON payload template.

## Metrics and results

Current checks cover input validation, slide-count rules, required slide fields, hashtag format, and presence of HTTP(S) source links. The structural evaluator reports slide count, field completeness, hashtag count, source count, and pass/fail gates.

Run tests and linting:

```bash
pytest
ruff check .
```

Evaluate a completed normalized campaign JSON:

```bash
python scripts/evaluate_campaign.py path/to/campaign.json
```

These checks evaluate structure only. They do not prove factual accuracy, source relevance, writing quality, or marketing effectiveness. Those measures, along with latency, token use, API costs, engagement, and conversion, have not yet been measured. See [`docs/evaluation.md`](docs/evaluation.md).

## Safety and limitations

- Treat retrieved sources and generated claims as untrusted until reviewed.
- Verify source pages and dates, not just search snippets.
- Review audience fit, tone, originality, copyright/licensing, and sensitive claims.
- Do not auto-publish solely based on model output.
- This prototype does not publish to social platforms or track campaign performance.
- API usage may incur provider charges.

## Contributing and security

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md). Keep tests reproducible, never commit secrets, and label results as measured, estimated, or not yet measured.
