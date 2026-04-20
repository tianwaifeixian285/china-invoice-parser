from __future__ import annotations

from pathlib import Path

from .fields import extract_invoice_fields
from .format_result import build_summary
from .models import ParseResult, SignatureStatus
from .ocr_extract import IMAGE_SUFFIXES, extract_image_text, extract_pdf_text_with_ocr
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
    if suffix in IMAGE_SUFFIXES:
        return "image"
    if suffix in {".txt", ".text"}:
        return "text"
    if suffix == ".xml":
        return "xml"
    return "unknown"


def _count_invoice_signals(raw_text: str) -> int:
    markers = ("发票号码", "开票日期", "价税合计", "税额", "购买方", "销售方", "名称")
    return sum(marker in raw_text for marker in markers)


def _invoice_score(invoice) -> int:
    values = [
        invoice.invoice_type,
        invoice.invoice_code,
        invoice.invoice_number,
        invoice.issue_date,
        invoice.buyer_name,
        invoice.buyer_tax_id,
        invoice.seller_name,
        invoice.seller_tax_id,
        invoice.amount_without_tax,
        invoice.tax_amount,
        invoice.amount_with_tax,
    ]
    score = sum(value is not None for value in values)
    if invoice.items:
        score += 2
    return score


def _should_try_pdf_ocr(raw_text: str, invoice) -> bool:
    normalized_length = len("".join(raw_text.split()))
    if normalized_length == 0:
        return True
    if _invoice_score(invoice) >= 7:
        return False
    if normalized_length < 80:
        return True
    return _count_invoice_signals(raw_text) < 3


def _select_better_invoice_text(current_text: str, current_invoice, candidate_text: str):
    if not candidate_text:
        return current_text, current_invoice
    candidate_invoice = extract_invoice_fields(candidate_text)
    if _invoice_score(candidate_invoice) > _invoice_score(current_invoice):
        return candidate_text, candidate_invoice
    merged_text = current_text
    if candidate_text not in current_text:
        merged_text = "\n".join(part for part in [current_text, candidate_text] if part)
    merged_invoice = extract_invoice_fields(merged_text)
    if _invoice_score(merged_invoice) > _invoice_score(current_invoice):
        return merged_text, merged_invoice
    return current_text, current_invoice


def parse_invoice(path: Path) -> ParseResult:
    file_type = detect_file_type(path)
    warnings: list[str] = []

    if file_type == "pdf":
        signature, sig_warnings = verify_pdf_signature(path)
        raw_text, text_warnings = extract_pdf_text(path)
        invoice = extract_invoice_fields(raw_text)
        if _should_try_pdf_ocr(raw_text, invoice):
            ocr_text, ocr_warnings = extract_pdf_text_with_ocr(path)
            warnings.extend(ocr_warnings)
            raw_text, invoice = _select_better_invoice_text(raw_text, invoice, ocr_text)
    elif file_type == "ofd":
        signature, sig_warnings = verify_ofd_signature(path)
        raw_text, text_warnings = extract_ofd_text(path)
        invoice = extract_invoice_fields(raw_text)
    elif file_type == "image":
        signature = SignatureStatus(
            has_signature=False,
            signature_format=None,
            verification_status="unsupported",
            reason="Signature verification is not supported for image input.",
        )
        sig_warnings = ["Signature verification is not supported for image input."]
        raw_text, text_warnings = extract_image_text(path)
        invoice = extract_invoice_fields(raw_text)
    elif file_type in {"text", "xml"}:
        signature = SignatureStatus(
            has_signature=False,
            signature_format=None,
            verification_status="unsupported",
            reason=(
                "Signature verification is not implemented for plain text or XML input "
                "in this version."
            ),
        )
        sig_warnings = ["Signature verification is not implemented for plain text or XML input."]
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
        text_warnings = []
        invoice = extract_invoice_fields(raw_text)
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
        invoice = extract_invoice_fields(raw_text)

    warnings.extend(sig_warnings)
    warnings.extend(text_warnings)
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
