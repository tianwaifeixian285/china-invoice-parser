#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${CHINA_INVOICE_PARSER_REPO_URL:-https://github.com/tianwaifeixian285/china-invoice-parser.git}"
INSTALL_DIR="${HERMES_SKILL_INSTALL_DIR:-$HOME/.hermes/skills/china-invoice-parser}"
WITH_OCR="${WITH_OCR:-0}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

usage() {
  cat <<'EOF'
用法:
  ./scripts/install_hermes_skill.sh [--with-ocr] [--install-dir PATH] [--repo URL] [--python PYTHON]

示例:
  ./scripts/install_hermes_skill.sh
  ./scripts/install_hermes_skill.sh --with-ocr
  ./scripts/install_hermes_skill.sh --install-dir ~/.hermes/skills/china-invoice-parser

说明:
  - 默认安装到 ~/.hermes/skills/china-invoice-parser
  - 默认安装依赖: .[pdf,sign]
  - --with-ocr 会额外安装 .[ocr]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-ocr)
      WITH_OCR=1
      shift
      ;;
    --install-dir)
      INSTALL_DIR="$2"
      shift 2
      ;;
    --repo)
      REPO_URL="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "缺少 git，请先安装 git。" >&2
  exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "缺少 Python: $PYTHON_BIN" >&2
  exit 1
fi

mkdir -p "$(dirname "$INSTALL_DIR")"

if [[ -d "$INSTALL_DIR/.git" ]]; then
  echo "更新现有仓库: $INSTALL_DIR"
  git -C "$INSTALL_DIR" fetch origin
  git -C "$INSTALL_DIR" checkout main
  git -C "$INSTALL_DIR" pull --ff-only origin main
else
  if [[ -e "$INSTALL_DIR" ]]; then
    echo "目标路径已存在但不是 git 仓库: $INSTALL_DIR" >&2
    exit 1
  fi
  echo "克隆仓库到: $INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

echo "创建虚拟环境"
"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate

echo "升级 pip"
python -m pip install --upgrade pip

extras=".[pdf,sign]"
if [[ "$WITH_OCR" == "1" ]]; then
  extras=".[pdf,sign,ocr]"
fi

echo "安装项目依赖: $extras"
pip install -e "$extras"

if [[ "$WITH_OCR" == "1" ]]; then
  if ! command -v tesseract >/dev/null 2>&1; then
    echo "警告: 已安装 OCR Python 依赖，但系统缺少 tesseract。" >&2
    echo "macOS: brew install tesseract" >&2
    echo "Ubuntu/Debian: sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim" >&2
  fi
fi

echo
echo "安装完成。"
echo "Skill 目录: $INSTALL_DIR"
echo "验证命令:"
echo "  $INSTALL_DIR/.venv/bin/python $INSTALL_DIR/scripts/parse_invoice.py /绝对路径/发票.pdf --pretty"

