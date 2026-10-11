"""Command-line entry point for generating a marketing campaign draft."""

from __future__ import annotations

import argparse
import logging
import sys

from marketing_squad.squad import generate_campaign


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="marketing-squad",
        description="Generate research-backed social carousel content with a multi-agent team.",
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
    parser.add_argument("--verbose", action="store_true", help="Enable informational logs.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    try:
        result = generate_campaign(
            args.topic,
            audience=args.audience,
            platforms=tuple(args.platforms),
        )
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
