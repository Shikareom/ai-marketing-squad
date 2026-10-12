# AI Marketing Squad

A modular, research-informed multi-agent workflow that turns a campaign brief into a structured social-content draft with source references and objective quality gates.

## What it does

Three focused agents handle distinct stages:

1. **Trend Scout** researches three current hooks, evidence summaries, and source references.
2. **Creative Director** transforms the research brief into a validated, slide-by-slide blueprint.
3. **Content Copywriter** writes slide scripts, a caption, hashtags, and source references.

The application explicitly passes each structured result to the next stage. The workflow validates slide count and sequencing, corrects invalid drafts once, and evaluates the final campaign before returning it.

This is a working prototype. It creates drafts for human review; it does not automatically publish posts or track campaign performance.

## Architecture

\`\`\`text
src/marketing_squad/
├── agents/
│   ├── trend_scout.py
│   ├── creative_director.py
│   └── content_copywriter.py
├── models.py
├── workflow.py
├── squad.py
├── cli.py
├── config.py
├── tools.py
└── validation.py
\`\`\`

See [the architecture guide](docs/architecture.md) for stage contracts, error behavior, and trust boundaries.

## Quick start

Requires Python 3.10+, an OpenAI API key, and a Tavily API key.

\`\`\`bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
\`\`\`

Copy \`.env.example\` to \`.env\` and add your credentials:

\`\`\`dotenv
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
MARKETING_MODEL_ID=gpt-4o
MIN_CAROUSEL_SLIDES=7
MAX_CAROUSEL_SLIDES=10
\`\`\`

Never commit \`.env\` or real API keys.

## Run a campaign

\`\`\`bash
marketing-squad --topic "How to explain career gaps" --audience "early-career professionals" --platforms Instagram LinkedIn
\`\`\`

Save the campaign, intermediate artifacts, and evaluation report as JSON while also printing Markdown:

\`\`\`bash
marketing-squad --topic "Build a strong project portfolio" --output artifacts/portfolio-campaign.json
\`\`\`

Python API:

\`\`\`python
from marketing_squad import generate_campaign, generate_campaign_result

markdown = generate_campaign("How to explain career gaps")
print(markdown)

result = generate_campaign_result("How to explain career gaps")
print(result.evaluation)
print(result.campaign.model_dump(mode="json"))
\`\`\`

Running a campaign makes live model and search requests and can incur charges. Automated tests use fake agents or test credentials and do not make provider calls.

## Validation and metrics

The final campaign is checked for:

- Configured slide-count range (default 7–10)
- Sequential slide numbers
- Complete slide number/title/visual idea/script fields
- Non-empty topic and caption
- At least ten distinct hashtags beginning with \`#\`
- At least one well-formed HTTP(S) source URL

If objective checks fail, the workflow asks the copywriter for one correction attempt. The report exposes the individual gates and counts, not an invented quality score.

These checks do **not** establish factual accuracy, source relevance, naturalness, originality, or marketing effectiveness. No measured improvements in engagement, conversions, speed, or time saved are claimed. The manual evaluation protocol is documented in [docs/evaluation.md](docs/evaluation.md).

Run tests and linting:

\`\`\`bash
pytest
ruff check .
\`\`\`

Evaluate a stored campaign JSON or the workflow JSON produced with \`--output\`:

\`\`\`bash
python scripts/evaluate_campaign.py path/to/campaign.json
\`\`\`

## Security and responsible use

- Verify linked pages and publication dates; search snippets alone are not proof.
- Treat retrieved content and model output as untrusted until checked.
- Review audience fit, factual nuance, sensitive claims, and copyright/licensing before use.
- Do not auto-publish generated content without a human review.
- Use API spending limits; never store keys in source files, notebooks, or issue comments.

See [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
