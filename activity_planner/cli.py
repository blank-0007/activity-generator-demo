"""Command-line interface for GitHub Activity Planner."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
import re

from .analysis import filter_activity, summarize_activity
from .loader import ActivityDataError, load_activity
from .report import render_markdown, render_text


def _parse_filter_date(value: str, flag: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ActivityDataError(
            f"Invalid {flag} date {value!r}; expected YYYY-MM-DD"
        )
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ActivityDataError(
            f"Invalid {flag} date {value!r}; expected YYYY-MM-DD"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="activity-planner",
        description="Analyze local GitHub activity snapshots and create a report.",
    )
    parser.add_argument("--input", required=True, help="Path to a .json or .csv activity file")
    parser.add_argument(
        "--format",
        choices=("text", "markdown"),
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("--output", help="Optional output file; defaults to the terminal")
    parser.add_argument("--from", dest="start_date", help="Include records on or after YYYY-MM-DD")
    parser.add_argument("--to", dest="end_date", help="Include records on or before YYYY-MM-DD")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        start_date = _parse_filter_date(args.start_date, "--from") if args.start_date else None
        end_date = _parse_filter_date(args.end_date, "--to") if args.end_date else None
        if start_date and end_date and start_date > end_date:
            raise ActivityDataError("--from date cannot be after --to date")
        records = load_activity(args.input)
        records = filter_activity(records, start_date, end_date)
        summary = summarize_activity(records)
        rendered = render_markdown(summary) if args.format == "markdown" else render_text(summary)
        if args.output:
            destination = Path(args.output)
            destination.write_text(rendered + "\n", encoding="utf-8")
            print(f"Report written to {destination}")
        else:
            print(rendered)
        return 0
    except (ActivityDataError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
