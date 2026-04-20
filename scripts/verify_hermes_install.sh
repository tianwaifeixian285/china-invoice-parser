#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${HERMES_SKILL_INSTALL_DIR:-$HOME/.hermes/skills/china-invoice-parser}"

if [[ ! -f "$INSTALL_DIR/SKILL.md" ]]; then
  echo "未发现 SKILL.md: $INSTALL_DIR/SKILL.md" >&2
  exit 1
fi

if [[ ! -x "$INSTALL_DIR/.venv/bin/python" ]]; then
  echo "未发现虚拟环境 Python: $INSTALL_DIR/.venv/bin/python" >&2
  exit 1
fi

echo "检测到 skill 目录: $INSTALL_DIR"
echo "检测到虚拟环境。"

if command -v hermes >/dev/null 2>&1; then
  echo
  echo "Hermes skills list 中的相关项:"
  hermes skills list | grep -i "invoice\|china-invoice-parser" || true
fi

echo
echo "建议手工验证:"
echo "  $INSTALL_DIR/.venv/bin/python $INSTALL_DIR/scripts/parse_invoice.py /绝对路径/发票.pdf --pretty"

