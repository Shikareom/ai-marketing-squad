"""Command-line entry point for generating a marketing campaign draft."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from marketing_squad.squad import generate_campaign_result
from marketing_squad.workflow import WorkflowValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="marketing-squad",
        description="Generate research-backed social carousel content with a multi-agent workflow.",
    )
    parser.add_argument("--topic", required=True, help="Topic or campaign angle to explore.")
    parser.add_argument(
        "--audience",
        default="professionals and early-career job seekers",
        help="Intended audience (default: professionals and early-career job seekers).",
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=["Instagram", "LinkedIn"],
        help="Target platforms (default: Instagram LinkedIn).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to save the campaign, intermediate artifacts, and evaluation as JSON.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable diagnostic logs.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    try:
        result = generate_campaign_result(
            args.topic,
            audience=args.audience,
            platforms=tuple(args.platforms),
        )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result.to_dict(), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"Saved structured campaign report to {args.output}")
        print(result.to_markdown())
        return 0
    except WorkflowValidationError as exc:
        print(f"Campaign validation failed: {exc}", file=sys.stderr)
        print(json.dumps(exc.report, indent=2, ensure_ascii=False), file=sys.stderr)
        return 3
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception:
        if args.verbose:
            logging.exception("Campaign generation failed")
        else:
            print(
                "Campaign generation failed. Re-run with --verbose for diagnostics.",
                file=sys.stderr,
            )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
