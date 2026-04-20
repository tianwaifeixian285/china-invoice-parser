from __future__ import annotations

from pathlib import Path

from china_invoice_parser.models import SignatureStatus
from china_invoice_parser.ocr_extract import IMAGE_SUFFIXES
from china_invoice_parser.parser import detect_file_type, parse_invoice


def test_detect_file_type_recognizes_images() -> None:
    assert ".png" in IMAGE_SUFFIXES
    assert detect_file_type(Path("invoice.png")) == "image"


def test_parse_image_uses_ocr(monkeypatch: object, tmp_path: Path) -> None:
    image_path = tmp_path / "invoice.png"
    image_path.write_bytes(b"fake-image")

    def fake_extract_image_text(path: Path) -> tuple[str, list[str]]:
        assert path == image_path
        return (
            "增值税电子普通发票\n发票号码: 12345678\n开票日期: 2026年04月20日\n价税合计: 100.00",
            [],
        )

    monkeypatch.setattr("china_invoice_parser.parser.extract_image_text", fake_extract_image_text)
    result = parse_invoice(image_path)
    assert result.file_type == "image"
    assert result.invoice.invoice_number == "12345678"
    assert result.signature.verification_status == "unsupported"


def test_parse_pdf_uses_ocr_when_text_quality_is_weak(monkeypatch: object, tmp_path: Path) -> None:
    pdf_path = tmp_path / "invoice.pdf"
    pdf_path.write_bytes(b"fake-pdf")

    monkeypatch.setattr(
        "china_invoice_parser.parser.verify_pdf_signature",
        lambda path: (
            SignatureStatus(
                has_signature=False,
                signature_format="pdf-pkcs7",
                verification_status="unsigned",
            ),
            [],
        ),
    )
    monkeypatch.setattr(
        "china_invoice_parser.parser.extract_pdf_text",
        lambda path: ("发票", []),
    )
    monkeypatch.setattr(
        "china_invoice_parser.parser.extract_pdf_text_with_ocr",
        lambda path: (
            "增值税电子普通发票\n发票号码: 23456789\n开票日期: 2026年04月20日\n"
            "购买方名称: 示例购买方有限公司\n销售方名称: 示例销售方有限公司\n"
            "税额: 10.00\n价税合计: 110.00",
            [],
        ),
    )
    result = parse_invoice(pdf_path)
    assert result.invoice.invoice_number == "23456789"
    assert result.invoice.buyer_name == "示例购买方有限公司"
    assert result.invoice.amount_without_tax == 100.0


def test_parse_pdf_skips_ocr_when_text_is_already_strong(
    monkeypatch: object, tmp_path: Path
) -> None:
    pdf_path = tmp_path / "invoice.pdf"
    pdf_path.write_bytes(b"fake-pdf")

    monkeypatch.setattr(
        "china_invoice_parser.parser.verify_pdf_signature",
        lambda path: (
            SignatureStatus(
                has_signature=False,
                signature_format="pdf-pkcs7",
                verification_status="unsigned",
            ),
            [],
        ),
    )
    strong_text = (
        "增值税电子普通发票\n发票号码: 34567890\n开票日期: 2026年04月20日\n"
        "购买方名称: 已有购买方有限公司\n销售方名称: 已有销售方有限公司\n"
        "税额: 5.00\n价税合计: 55.00"
    )
    monkeypatch.setattr(
        "china_invoice_parser.parser.extract_pdf_text",
        lambda path: (strong_text, []),
    )

    def fail_if_called(path: Path) -> tuple[str, list[str]]:
        raise AssertionError("OCR should not be called for strong PDF text")

    monkeypatch.setattr("china_invoice_parser.parser.extract_pdf_text_with_ocr", fail_if_called)
    result = parse_invoice(pdf_path)
    assert result.invoice.invoice_number == "34567890"
    assert result.invoice.amount_without_tax == 50.0
