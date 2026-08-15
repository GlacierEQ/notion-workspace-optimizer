#!/usr/bin/env python3
"""Fail-closed public truth checks for the workspace optimizer surface."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PUBLIC_TRUTH_FAIL: {message}")


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    caps = json.loads((ROOT / "machine/capabilities.json").read_text(encoding="utf-8"))
    state = json.loads((ROOT / "machine/excellence-state.json").read_text(encoding="utf-8"))

    forbidden = (
        "src/workspace_optimizer.py",
        "semantic text hashing",
        "MCP Tool",
        "Mastermind Sidecar",
        "database index tuning",
        "Automated Notion workspace optimization",
    )
    for phrase in forbidden:
        require(phrase not in readme, f"README contains unsupported claim/path: {phrase}")

    require("does not connect to" in readme, "live Notion nonclaim missing")
    require("not a probability" in readme, "policy-score semantic boundary missing")
    require("do not perform any external action" in readme, "recommendation-only boundary missing")
    require("not semantic hashing" in readme, "literal grouping boundary missing")

    allowed = {
        "deterministic-page-metadata-policy-scoring",
        "bounded-workspace-review-recommendation-labeling",
        "deterministic-title-prefix-grouping",
        "validated-local-workspace-metadata-processing",
    }
    require(set(caps.get("capabilities", [])) == allowed, "machine capability allowlist drift")
    require(caps.get("operational_authority") is False, "operational authority must be false")
    require(caps.get("live_notion_api_integration") is False, "live Notion claim must be false")
    require(caps.get("workspace_mutation") is False, "workspace mutation claim must be false")
    require(
        caps.get("semantic_hashing_or_embedding_similarity") is False,
        "semantic similarity claim must be false",
    )
    require(
        caps.get("live_mcp_apex_mastermind_integration") is False,
        "live mesh claim must be false",
    )

    require(state.get("principal_state") == "FUNCTIONAL_CANDIDATE", "stale promotion restored")
    require(state.get("operational_authority") is False, "state grants operational authority")
    proof = state.get("gates", {}).get("DETERMINISTIC_PROOF_GREEN", {})
    require(proof.get("status") == "PENDING_CANONICAL_CI", "fresh exact-head proof gate missing")

    print("PUBLIC_TRUTH_PASS")


if __name__ == "__main__":
    main()
