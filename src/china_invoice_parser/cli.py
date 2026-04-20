from __future__ import annotations

import argparse
import json
from pathlib import Path

from .parser import parse_invoice


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse Chinese invoice files and emit normalized JSON.")
    parser.add_argument("input", help="Path to a PDF, OFD, XML, or text file.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--summary-only", action="store_true", help="Print only the short summary line.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = Path(args.input).expanduser().resolve()

    if not path.exists():
        parser.error(f"Input path does not exist: {path}")

    result = parse_invoice(path)
    if args.summary_only:
        print(result.summary)
        return 0

    payload = result.to_dict()
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))
    return 0
