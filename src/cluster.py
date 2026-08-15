#!/usr/bin/env python3
"""Cluster caller-supplied page references by deterministic title prefix."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class PageRef:
    id: str
    title: str


def cluster(pages: list[PageRef], min_size: int = 2) -> dict:
    """Group pages by the lower-cased token before the first ``-``.

    This is literal prefix grouping, not semantic similarity or embedding-based
    clustering.
    """

    if isinstance(min_size, bool) or not isinstance(min_size, int):
        raise TypeError("min_size must be an integer")
    if min_size < 1:
        raise ValueError("min_size must be at least 1")

    buckets: dict[str, list[str]] = defaultdict(list)
    for page in pages:
        if not page.id:
            raise ValueError("page id is required")
        token = (page.title.split("-")[0] if page.title else "misc").strip().lower()
        token = token or "misc"
        buckets[token].append(page.id)

    groups = {
        key: tuple(sorted(ids))
        for key, ids in sorted(buckets.items())
        if len(ids) >= min_size
    }
    return {
        "clusters": groups,
        "singleton_n": sum(1 for ids in buckets.values() if len(ids) < min_size),
        "operational_authority": False,
    }


if __name__ == "__main__":
    print(
        cluster(
            [
                PageRef("1", "ops-a"),
                PageRef("2", "ops-b"),
                PageRef("3", "misc"),
            ]
        )
    )
