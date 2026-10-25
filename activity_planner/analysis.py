"""Pure analysis functions for activity records."""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any


def filter_activity(
    records: list[dict[str, Any]],
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict[str, Any]]:
    """Return records whose dates fall within an inclusive optional range."""
    return [
        record
        for record in records
        if (start_date is None or date.fromisoformat(record["date"]) >= start_date)
        and (end_date is None or date.fromisoformat(record["date"]) <= end_date)
    ]


def summarize_activity(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate validated records into report-friendly statistics."""
    daily: Counter[str] = Counter()
    repositories: Counter[str] = Counter()
    event_types: Counter[str] = Counter()
    for record in records:
        count = record["count"]
        daily[record["date"]] += count
        repositories[record["repository"]] += count
        event_types[record["type"]] += count

    active_dates = sorted(day for day, count in daily.items() if count > 0)
    longest_gap = 0
    for previous, current in zip(active_dates, active_dates[1:]):
        gap = (date.fromisoformat(current) - date.fromisoformat(previous)).days - 1
        longest_gap = max(longest_gap, gap)

    return {
        "record_count": len(records),
        "total_activity": sum(daily.values()),
        "active_days": len(active_dates),
        "first_activity_date": active_dates[0] if active_dates else None,
        "last_activity_date": active_dates[-1] if active_dates else None,
        "longest_gap_days": longest_gap,
        "daily_activity": dict(sorted(daily.items())),
        "repositories": dict(repositories.most_common()),
        "event_types": dict(event_types.most_common()),
    }


def suggest_next_steps(summary: dict[str, Any]) -> list[str]:
    """Generate suggestions grounded only in the supplied summary."""
    suggestions: list[str] = []
    repositories = summary.get("repositories", {})
    event_types = summary.get("event_types", {})

    if summary.get("record_count", 0) == 0 or summary.get("total_activity", 0) == 0:
        return [
            "Choose one small project task and record the outcome after completing it."
        ]

    if summary.get("longest_gap_days", 0) >= 7:
        suggestions.append(
            "The dataset contains a gap of at least a week. Pick one small, concrete issue for your next session."
        )
    if repositories:
        top_repository = next(iter(repositories))
        suggestions.append(
            f"Review the next milestone in '{top_repository}', the most active repository in this dataset."
        )
    if not any(kind in event_types for kind in ("pull_request", "review")):
        suggestions.append(
            "Consider opening a focused pull request or reviewing a teammate's change when you have a useful improvement."
        )
    if len(suggestions) < 3:
        suggestions.append(
            "Keep activity tied to shipped work: write a test, improve documentation, or fix a reproducible issue."
        )
    return suggestions[:3]
