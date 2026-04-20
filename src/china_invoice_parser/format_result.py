from __future__ import annotations

from .models import ParseResult


def build_summary(result: ParseResult) -> str:
    invoice = result.invoice
    signature = result.signature
    parts = [
        f"file_type={result.file_type}",
        f"invoice_type={invoice.invoice_type or 'unknown'}",
        f"invoice_number={invoice.invoice_number or 'unknown'}",
        f"buyer={invoice.buyer_name or 'unknown'}",
        f"seller={invoice.seller_name or 'unknown'}",
        f"total={invoice.amount_with_tax if invoice.amount_with_tax is not None else 'unknown'}",
        f"signature={signature.verification_status}",
    ]
    if result.warnings:
        parts.append(f"warnings={len(result.warnings)}")
    return ", ".join(parts)
