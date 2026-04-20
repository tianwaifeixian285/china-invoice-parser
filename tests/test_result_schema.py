from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from china_invoice_parser.parser import parse_invoice

from .helpers import sign_pdf_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


def _load_validator() -> Draft202012Validator:
    schema = json.loads((ROOT / "specs/result-schema-v1.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_schema_accepts_pdf_fixture_result() -> None:
    validator = _load_validator()
    result = parse_invoice(FIXTURES / "pdf" / "sanitized_vat_invoice.pdf")
    validator.validate(result.to_dict())


def test_schema_accepts_ofd_fixture_result() -> None:
    validator = _load_validator()
    result = parse_invoice(FIXTURES / "ofd" / "sanitized_vat_invoice.ofd")
    validator.validate(result.to_dict())


def test_schema_accepts_signed_pdf_result(tmp_path: Path) -> None:
    validator = _load_validator()
    signed_pdf = sign_pdf_fixture(
        FIXTURES / "pdf" / "sanitized_vat_invoice.pdf",
        tmp_path / "signed.pdf",
        tmp_path,
    )
    result = parse_invoice(signed_pdf)
    validator.validate(result.to_dict())
