#!/usr/bin/env bash
set -euo pipefail

python -m pip install --disable-pip-version-check ruff pytest

# Correctness-focused lint on shipped source and tests. Legacy/generated
# fleet surfaces remain outside this repository's proof boundary.
python -m ruff check --select E9,F63,F7,F82 src tests scripts/verify_public_truth.py
python -m compileall -q src tests scripts
python -m pytest -q
python scripts/verify_public_truth.py

install -d -m 700 .verification-artifacts
python scripts/operate.py > .verification-artifacts/operate.json

python - <<'PY'
import json
import os
from pathlib import Path

operate_path = Path('.verification-artifacts/operate.json')
operate = json.loads(operate_path.read_text(encoding='utf-8'))
smoke = operate.get('smoke') or {}
if operate.get('ok') is not True:
    raise SystemExit('operate.py did not report ok=true')
if smoke.get('invoked') is not True:
    raise SystemExit('operate.py did not invoke a repository mechanism')
if smoke.get('content_checked') is not True:
    raise SystemExit('operate.py did not content-check the mechanism result')

receipt = {
    'schema': 'glaciereq.repository-verification.v1',
    'repository': os.environ['GITHUB_REPOSITORY'],
    'head_sha': os.environ['GITHUB_SHA'],
    'verification': {
        'critical_lint': 'PASS',
        'compileall': 'PASS',
        'pytest': 'PASS',
        'public_truth': 'PASS',
        'operate_content_check': 'PASS',
    },
    'scope': 'bounded-src-tests-truth-and-content-checked-operation',
}
Path('.verification-artifacts/verification.json').write_text(
    json.dumps(receipt, sort_keys=True, indent=2) + '\n',
    encoding='utf-8',
)
PY
