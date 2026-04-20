#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "用法: ./scripts/release.sh <version>" >&2
  exit 1
fi

VERSION="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "工作区不干净，请先提交或清理变更。" >&2
  exit 1
fi

source .venv/bin/activate

python - <<PY
from pathlib import Path
import re

version = "${VERSION}"
pyproject = Path("pyproject.toml")
init_file = Path("src/china_invoice_parser/__init__.py")

pyproject_text = pyproject.read_text(encoding="utf-8")
pyproject_text = re.sub(r'^version = "[^"]+"$', f'version = "{version}"', pyproject_text, flags=re.MULTILINE)
pyproject.write_text(pyproject_text, encoding="utf-8")

init_text = init_file.read_text(encoding="utf-8")
init_text = re.sub(r'^__version__ = "[^"]+"$', f'__version__ = "{version}"', init_text, flags=re.MULTILINE)
init_file.write_text(init_text, encoding="utf-8")
PY

./scripts/check.sh
git add pyproject.toml src/china_invoice_parser/__init__.py
if ! git diff --cached --quiet; then
  git commit -m "release: v${VERSION}"
else
  echo "版本号已是 ${VERSION}，跳过 release 提交，直接基于当前提交打标签。"
fi
git tag "v${VERSION}"

echo "已创建提交和标签 v${VERSION}。"
