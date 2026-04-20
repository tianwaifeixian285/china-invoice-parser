from __future__ import annotations

from pathlib import Path

from china_invoice_parser.parser import parse_invoice


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_sanitized_pdf_fixture() -> None:
    result = parse_invoice(FIXTURES / "pdf" / "sanitized_vat_invoice.pdf")
    assert result.file_type == "pdf"
    assert result.invoice.invoice_type == "增值税电子普通发票"
    assert result.invoice.invoice_number == "12345678"
    assert result.invoice.buyer_name == "杭州示例科技有限公司"
    assert result.invoice.seller_name == "深圳示例服务有限公司"
    assert result.invoice.amount_with_tax == 113.0
    assert len(result.invoice.items) == 1


def test_parse_sanitized_ofd_fixture() -> None:
    result = parse_invoice(FIXTURES / "ofd" / "sanitized_vat_invoice.ofd")
    assert result.file_type == "ofd"
    assert result.invoice.invoice_type == "增值税电子专用发票"
    assert result.invoice.invoice_number == "87654321"
    assert result.signature.has_signature is True
    assert result.signature.verification_status == "unknown"
    assert result.signature.signer == "测试签章服务商"
    assert result.signature.sign_time == "2026-04-20T09:00:00"
    assert len(result.invoice.items) == 1
