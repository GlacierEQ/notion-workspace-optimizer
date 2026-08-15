from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.cluster import PageRef, cluster
from src.optimizer import Page, optimize, score_page


def test_policy_score_is_bounded_and_ranks_stale_leaf() -> None:
    fresh = Page("fresh", "fresh", depth=1, links=1, days_stale=1, children=0)
    stale = Page("stale", "old-note", depth=2, links=0, days_stale=200, children=0)

    assert 0.0 < score_page(fresh) <= 1.5
    assert score_page(stale) > score_page(fresh)

    result = optimize(
        [fresh, stale],
        top_k=2,
        observed_at=datetime(2026, 8, 14, tzinfo=timezone.utc),
    )
    assert result["actions"][0]["id"] == "stale"
    assert result["actions"][0]["action"] == "ARCHIVE_CANDIDATE"
    assert result["operational_authority"] is False


def test_policy_recommendation_labels_cover_bounded_rules() -> None:
    pages = [
        Page("archive", "archive", depth=1, links=1, days_stale=90, children=0),
        Page("collapse", "collapse", depth=6, links=1, days_stale=1, children=2),
        Page("split", "split", depth=1, links=30, days_stale=1, children=2),
        Page("review", "review", depth=1, links=1, days_stale=1, children=2),
    ]
    result = optimize(
        pages,
        top_k=4,
        observed_at=datetime(2026, 8, 14, tzinfo=timezone.utc),
    )
    by_id = {row["id"]: row["action"] for row in result["actions"]}
    assert by_id == {
        "archive": "ARCHIVE_CANDIDATE",
        "collapse": "COLLAPSE_NESTING",
        "split": "SPLIT_HUB",
        "review": "REVIEW",
    }


def test_complete_optimizer_envelope_can_be_reproduced() -> None:
    pages = [
        Page("b", "ops-b", depth=2, links=5, days_stale=20, children=1),
        Page("a", "ops-a", depth=2, links=5, days_stale=20, children=1),
    ]
    observed_at = datetime(2026, 8, 14, 12, 0, tzinfo=timezone.utc)

    first = optimize(pages, top_k=2, observed_at=observed_at)
    second = optimize(list(reversed(pages)), top_k=2, observed_at=observed_at)

    assert first == second
    assert [row["id"] for row in first["actions"]] == ["a", "b"]
    assert first["observed_at"] == "2026-08-14T12:00:00+00:00"


@pytest.mark.parametrize(
    "field",
    ["depth", "links", "days_stale", "children"],
)
def test_negative_page_metrics_fail_closed(field: str) -> None:
    kwargs = {
        "id": "x",
        "title": "x",
        "depth": 1,
        "links": 1,
        "days_stale": 1,
        "children": 1,
    }
    kwargs[field] = -1
    with pytest.raises(ValueError, match="non-negative"):
        score_page(Page(**kwargs))


def test_invalid_control_parameters_fail_closed() -> None:
    page = Page("x", "x", depth=1, links=1, days_stale=1, children=1)
    with pytest.raises(ValueError, match="top_k"):
        optimize([page], top_k=-1)
    with pytest.raises(TypeError, match="top_k"):
        optimize([page], top_k=True)
    with pytest.raises(ValueError, match="timezone-aware"):
        optimize([page], observed_at=datetime(2026, 8, 14))


def test_title_grouping_is_literal_prefix_not_semantic_similarity() -> None:
    result = cluster(
        [
            PageRef("1", "ops-a"),
            PageRef("2", "ops-b"),
            PageRef("3", "operations-c"),
            PageRef("4", ""),
        ]
    )
    assert result["clusters"] == {"ops": ("1", "2")}
    assert result["singleton_n"] == 2
    assert result["operational_authority"] is False


def test_cluster_validation_fails_closed() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        cluster([], min_size=0)
    with pytest.raises(TypeError, match="integer"):
        cluster([], min_size=True)
    with pytest.raises(ValueError, match="page id"):
        cluster([PageRef("", "ops-a")])
