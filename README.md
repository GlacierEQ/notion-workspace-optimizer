# Notion Workspace Optimizer

**Local page-metadata scoring, recommendation labeling, and title-prefix grouping.**

This repository is an independent portfolio project. It is not affiliated with Notion and it does not connect to, read from, mutate, archive, restructure, or otherwise control a live Notion workspace.

## Implemented mechanisms

### Page-policy scoring

`src/optimizer.py` accepts caller-supplied `Page` metadata and computes a bounded local policy score from:

- days stale;
- nesting depth;
- outgoing-link count; and
- child-page count.

The score is a deterministic heuristic used to rank items for review. It is **not** a probability, confidence estimate, semantic similarity score, measured workspace-health metric, or learned model output.

### Recommendation labels

The optimizer maps ranked page metadata to local suggestion labels:

- `ARCHIVE_CANDIDATE` for sufficiently stale leaf pages;
- `COLLAPSE_NESTING` for deeply nested pages;
- `SPLIT_HUB` for highly linked pages; and
- `REVIEW` otherwise.

These labels do not perform any external action. They are recommendations returned in a Python data structure with `operational_authority=false`.

### Title-prefix grouping

`src/cluster.py` groups caller-supplied page references by the lower-cased text before the first `-` in the title. This is literal deterministic prefix grouping. It is **not semantic hashing, embedding similarity, natural-language clustering, or duplicate detection**.

## Input boundary

The scoring and grouping functions reject malformed control parameters and impossible negative page metrics. A caller may also supply a timezone-aware observation timestamp to reproduce the complete optimizer envelope deterministically.

## What this repository does not establish

- No Notion affiliation, endorsement, employment, or proprietary access.
- No live Notion API, database, page, block, user, or workspace access.
- No automatic archiving, relation rewrites, database-index tuning, or workspace mutation.
- No semantic hashing, embeddings, duplicate-page detection, or learned clustering.
- No live MCP, APEX, Mastermind, or provider-mesh integration.
- No production operational authority, scale, reliability, latency, throughput, or security guarantee.

## Verification

Repository CI preserves the existing repository-owned verifier and adds a bounded Python contract matrix. The relevant local checks are:

```bash
python -m pytest -q
python scripts/verify_public_truth.py
```

The public-truth gate fails closed if live-provider claims, semantic/duplicate-detection claims, stale `hyper-scaling` metadata, or stale promotion authority reappear.

## Example

```python
from datetime import datetime, timezone
from src.optimizer import Page, optimize

pages = [
    Page("old", "old-note", depth=3, links=1, days_stale=120, children=0),
    Page("hub", "ops-hub", depth=1, links=30, days_stale=10, children=12),
]

result = optimize(
    pages,
    top_k=2,
    observed_at=datetime(2026, 8, 14, tzinfo=timezone.utc),
)
print(result["actions"])
```

The example uses only local caller-supplied metadata and emits recommendation labels, not workspace mutations.
