#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source .venv/bin/activate
python -m json.tool specs/result-schema-v1.json >/dev/null
python tests/fixtures/build_samples.py
pytest -q
