from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class InvoiceItem:
    name: str | None = None
    model: str | None = None
    unit: str | None = None
    count: float | None = None
    price: float | None = None
    amount: float | None = None
    tax_rate: float | None = None
    tax_amount: float | None = None


@dataclass
class InvoiceFields:
    invoice_type: str | None = None
    invoice_code: str | None = None
    invoice_number: str | None = None
    issue_date: str | None = None
    check_code: str | None = None
    buyer_name: str | None = None
    buyer_tax_id: str | None = None
    seller_name: str | None = None
    seller_tax_id: str | None = None
    amount_without_tax: float | None = None
    tax_amount: float | None = None
    amount_with_tax: float | None = None
    currency: str = "CNY"
    items: list[InvoiceItem] = field(default_factory=list)


@dataclass
class SignatureStatus:
    has_signature: bool = False
    signature_format: str | None = None
    verification_status: str = "unknown"
    signer: str | None = None
    sign_time: str | None = None
    cert_subject: str | None = None
    cert_issuer: str | None = None
    reason: str | None = None


@dataclass
class ParseResult:
    engine: str
    file_type: str
    invoice: InvoiceFields
    signature: SignatureStatus
    warnings: list[str] = field(default_factory=list)
    raw_text: str = ""
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

