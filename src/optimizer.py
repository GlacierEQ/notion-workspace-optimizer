#!/usr/bin/env python3
"""Local workspace page-policy scoring and recommendation labels.

The module operates only on caller-supplied page metadata. It does not read,
write, archive, or otherwise control a live Notion workspace.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

SCORE_FLOOR = 0.31415


@dataclass(frozen=True)
class Page:
    id: str
    title: str
    depth: int
    links: int
    days_stale: int
    children: int


def _validate_page(page: Page) -> None:
    if not page.id:
        raise ValueError("page id is required")
    for name in ("depth", "links", "days_stale", "children"):
        value = getattr(page, name)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if value < 0:
            raise ValueError(f"{name} must be non-negative")


def score_page(page: Page) -> float:
    """Return a bounded local policy score, not a probability/confidence value."""

    _validate_page(page)
    score = 0.35 * min(page.days_stale / 90.0, 1.5)
    score += 0.25 * min(page.depth / 6.0, 1.0)
    score += 0.20 * min(page.links / 20.0, 1.0)
    score += 0.20 * min(page.children / 15.0, 1.0)
    return max(SCORE_FLOOR, min(1.5, score))


def optimize(
    pages: list[Page],
    top_k: int = 5,
    *,
    observed_at: datetime | None = None,
) -> dict:
    """Rank caller-supplied pages and emit recommendation labels.

    The output labels are suggestions only. No external side effect occurs.
    ``observed_at`` may be supplied to make the complete result reproducible.
    """

    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise TypeError("top_k must be an integer")
    if top_k < 0:
        raise ValueError("top_k must be non-negative")

    ranked = sorted(
        ((score_page(page), page) for page in pages),
        key=lambda item: (-item[0], item[1].id),
    )
    actions = []
    for score, page in ranked[:top_k]:
        if page.days_stale > 60 and page.children == 0:
            action = "ARCHIVE_CANDIDATE"
        elif page.depth >= 5:
            action = "COLLAPSE_NESTING"
        elif page.links > 15:
            action = "SPLIT_HUB"
        else:
            action = "REVIEW"
        actions.append(
            {
                "id": page.id,
                "title": page.title,
                "score": round(score, 4),
                "action": action,
            }
        )

    timestamp = observed_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("observed_at must be timezone-aware")
    return {
        "actions": actions,
        "n": len(pages),
        "observed_at": timestamp.astimezone(timezone.utc).isoformat(),
        "operational_authority": False,
    }


if __name__ == "__main__":
    demo = [
        Page("1", "hub", 1, 30, 10, 40),
        Page("2", "old-note", 3, 1, 120, 0),
        Page("3", "deep", 7, 5, 20, 2),
    ]
    print(optimize(demo))
