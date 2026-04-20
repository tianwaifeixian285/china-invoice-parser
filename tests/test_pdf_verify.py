from __future__ import annotations

from pathlib import Path

from china_invoice_parser.pdf_verify import verify_pdf_signature

from .helpers import sign_pdf_fixture


FIXTURES = Path(__file__).parent / "fixtures"


def test_verify_unsigned_pdf_fixture() -> None:
    status, warnings = verify_pdf_signature(FIXTURES / "pdf" / "sanitized_vat_invoice.pdf")
    assert warnings == []
    assert status.verification_status == "unsigned"


def test_verify_signed_pdf_fixture(tmp_path: Path) -> None:
    signed_pdf = sign_pdf_fixture(
        FIXTURES / "pdf" / "sanitized_vat_invoice.pdf",
        tmp_path / "signed.pdf",
        tmp_path,
    )
    status, warnings = verify_pdf_signature(signed_pdf)
    assert warnings == []
    assert status.has_signature is True
    assert status.signature_format == "pdf-pkcs7"
    assert status.verification_status in {"valid", "unknown"}
    assert status.cert_subject is not None
