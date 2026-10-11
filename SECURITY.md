# Security

## API keys

- Store credentials in a local `.env` file or environment variables.
- Never commit `.env`, API keys, provider responses containing private data, or credentials in notebooks.
- Rotate a key immediately if it is accidentally exposed.
- Use provider-side usage limits and monitor usage for unexpected activity.

## Generated and retrieved content

Search snippets and model output are untrusted inputs. Verify source pages, publication dates, and factual claims before use. Do not automatically publish generated content without a human review.

## Reporting a concern

For a suspected secret leak or security issue, remove exposed credentials from use first, then contact the repository owner privately with enough detail to reproduce the issue. Avoid publishing exploitable details in a public issue.
