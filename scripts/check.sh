#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source .venv/bin/activate
ruff check .
black --check .
python -m json.tool specs/result-schema-v1.json >/dev/null
python tests/fixtures/build_samples.py
pytest -q
python -m build --sdist --wheel >/dev/null
python -m pip install --force-reinstall dist/*.whl >/dev/null
python - <<'PY'
import china_invoice_parser

print(china_invoice_parser.__version__)
PY
