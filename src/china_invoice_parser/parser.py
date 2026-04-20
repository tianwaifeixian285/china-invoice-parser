from __future__ import annotations

from pathlib import Path

from .fields import extract_invoice_fields
from .format_result import build_summary
from .models import ParseResult, SignatureStatus
from .ofd_extract import extract_ofd_text
from .ofd_verify import verify_ofd_signature
from .pdf_extract import extract_pdf_text
from .pdf_verify import verify_pdf_signature


def detect_file_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".ofd":
        return "ofd"
    if suffix in {".txt", ".text"}:
        return "text"
    if suffix == ".xml":
        return "xml"
    return "unknown"


def parse_invoice(path: Path) -> ParseResult:
    file_type = detect_file_type(path)
    warnings: list[str] = []

    if file_type == "pdf":
        signature, sig_warnings = verify_pdf_signature(path)
        raw_text, text_warnings = extract_pdf_text(path)
    elif file_type == "ofd":
        signature, sig_warnings = verify_ofd_signature(path)
        raw_text, text_warnings = extract_ofd_text(path)
    elif file_type in {"text", "xml"}:
        signature = SignatureStatus(
            has_signature=False,
            signature_format=None,
            verification_status="unsupported",
            reason="Signature verification is not implemented for plain text or XML input in this version.",
        )
        sig_warnings = ["Signature verification is not implemented for plain text or XML input."]
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
        text_warnings = []
    else:
        signature = SignatureStatus(
            has_signature=False,
            signature_format=None,
            verification_status="unsupported",
            reason=f"Unsupported file type: {path.suffix or 'no suffix'}",
        )
        sig_warnings = [f"Unsupported file type: {path.suffix or 'no suffix'}"]
        raw_text = ""
        text_warnings = []

    warnings.extend(sig_warnings)
    warnings.extend(text_warnings)

    invoice = extract_invoice_fields(raw_text)
    result = ParseResult(
        engine="python",
        file_type=file_type,
        invoice=invoice,
        signature=signature,
        warnings=warnings,
        raw_text=raw_text,
    )
    result.summary = build_summary(result)
    return result
