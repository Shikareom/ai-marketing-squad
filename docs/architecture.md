# Architecture

## Overview

The application enforces the three stages in Python. Each step receives a typed Pydantic model rather than relying on a team leader to follow ordering instructions.

\`\`\`mermaid
flowchart TD
    A[Topic, audience, platforms] --> B[Trend Scout]
    B --> C[ResearchBrief schema validation]
    C --> D[Creative Director]
    D --> E[CreativeBrief schema and slide-count validation]
    E -->|Invalid: one correction attempt| D
    E -->|Valid| F[Content Copywriter]
    F --> G[CampaignDraft schema validation]
    G --> H[Objective structural evaluation]
    H -->|Failed: one correction attempt| F
    H -->|Passed| I[Markdown and JSON artifacts]
    I --> J[Human review]
\`\`\`

## Stage contracts

### 1. Trend Scout — \`agents/trend_scout.py\`

Receives topic, audience, and platform context. It uses Tavily search and returns a typed \`ResearchBrief\` with exactly three \`ResearchFinding\` objects. Each finding has audience relevance, an evidence summary, and at least one \`SourceReference\`. Source URLs and publication dates still require human verification.

### 2. Creative Director — \`agents/creative_director.py\`

Receives the serialized research artifact and returns a \`CreativeBrief\`. Each planned slide includes a sequential number, title, visual idea, and purpose. The agent has a deterministic count validator; the workflow independently checks returned count and numbering, then requests one correction attempt if needed.

### 3. Content Copywriter — \`agents/content_copywriter.py\`

Receives both the research artifact and the accepted creative blueprint. It returns a typed \`CampaignDraft\` with final slide scripts, a caption, hashtags, and source references. The workflow evaluates the artifact, issues one correction request when objective checks fail, then raises a validation error rather than returning a structurally invalid campaign.

## Core modules

- \`models.py\`: Pydantic contracts shared by agents and tests.
- \`workflow.py\`: sequential orchestration, bounded correction loops, rendering, and evaluation integration.
- \`squad.py\`: public library functions; Markdown output or a structured result with intermediate artifacts.
- \`validation.py\`: deterministic slide-count and payload checks.
- \`config.py\`: model selection, slide limits, and secret configuration.
- \`cli.py\`: command-line usage and optional JSON artifact output.

## Trust boundaries and failure behavior

- Structured schemas constrain shape, not truth. A schema-valid URL may still be irrelevant or misleading.
- Agent/provider exceptions surface to the CLI, which returns a non-zero exit code and can print a traceback with \`--verbose\`.
- Creative and final-copy correction attempts are bounded to one by default; the workflow fails explicitly if the result remains invalid.
- The system does not auto-publish, keep a database of campaigns, or collect live performance analytics.
- API keys should be supplied through environment variables or a local ignored \`.env\` file.

## Test strategy

Unit tests exercise validators and the campaign input contract. Workflow tests inject fake agents to verify stage ordering, artifact hand-off, correction paths, and structural evaluation. An agent-construction smoke test creates real Agno objects with test-only credentials without calling model or search APIs. GitHub Actions runs tests and Ruff on supported Python versions.
