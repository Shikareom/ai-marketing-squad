"""Evaluate a normalized campaign JSON payload from the command line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from marketing_squad.validation import evaluate_campaign


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign_json", type=Path, help="Path to normalized campaign JSON.")
    parser.add_argument("--min-slides", type=int, default=7)
    parser.add_argument("--max-slides", type=int, default=10)
    parser.add_argument("--min-hashtags", type=int, default=10)
    args = parser.parse_args()

    try:
        campaign: Any = json.loads(args.campaign_json.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"Could not read campaign file: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2

    report = evaluate_campaign(
        campaign,
        minimum_slides=args.min_slides,
        maximum_slides=args.max_slides,
        minimum_hashtags=args.min_hashtags,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
