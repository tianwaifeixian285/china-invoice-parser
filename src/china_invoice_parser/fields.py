from __future__ import annotations

import re

from .models import InvoiceFields, InvoiceItem

INVOICE_TYPE_PATTERNS: tuple[str, ...] = (
    r"(增值税电子专用发票)",
    r"(增值税电子普通发票)",
    r"(电子发票[（(]普通发票[）)])",
    r"(全电发票[（(]专用发票[）)])",
    r"(全电发票[（(]普通发票[）)])",
    r"(全电发票)",
    r"(增值税专用发票)",
    r"(普通发票)",
)

FIELD_PATTERNS: dict[str, tuple[str, ...]] = {
    "invoice_code": (r"(?:发票代码|票据代码)[：:\s]*([0-9]{10,20})",),
    "invoice_number": (r"(?:发票号码|票据号码)[：:\s]*([0-9]{6,20})",),
    "issue_date": (
        r"(?:开票日期|日期)[：:\s]*([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日)",
        r"(?:开票日期|日期)[：:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2})",
    ),
    "check_code": (r"(?:校验码)[：:\s]*([0-9]{6,20})",),
}

BUYER_NAME_PATTERNS: tuple[str, ...] = (
    r"(?:购买方名称|购方名称)[：:\s]*([^\n]+)",
    r"购买方信息[\s\S]{0,120}?名称[：:\s]*([^\n]+)",
)

BUYER_TAX_ID_PATTERNS: tuple[str, ...] = (
    r"(?:购买方纳税人识别号|购方税号|购买方税号)[：:\s]*([0-9A-Z]{8,25})",
    r"购买方信息[\s\S]{0,120}?(?:纳税人识别号|税号)[：:\s]*([0-9A-Z]{8,25})",
)

SELLER_NAME_PATTERNS: tuple[str, ...] = (
    r"(?:销售方名称|销方名称)[：:\s]*([^\n]+)",
    r"销售方信息[\s\S]{0,120}?名称[：:\s]*([^\n]+)",
)

SELLER_TAX_ID_PATTERNS: tuple[str, ...] = (
    r"(?:销售方纳税人识别号|销方税号|销售方税号)[：:\s]*([0-9A-Z]{8,25})",
    r"销售方信息[\s\S]{0,120}?(?:纳税人识别号|税号)[：:\s]*([0-9A-Z]{8,25})",
)


def _search(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def _search_any(patterns: tuple[str, ...], text: str) -> str | None:
    for pattern in patterns:
        result = _search(pattern, text)
        if result:
            return result
    return None


def _extract_amount(label: str, text: str) -> float | None:
    value = _search(rf"{label}[：:\s]*([0-9]+(?:\.[0-9]+)?)", text)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.replace(",", "").replace("，", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_tax_rate(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.strip().replace("%", "")
    parsed = _parse_float(cleaned)
    if parsed is None:
        return None
    if parsed > 1:
        return round(parsed / 100, 4)
    return parsed


def _split_item_line(line: str) -> list[str]:
    if "|" in line:
        return [part.strip() for part in line.split("|") if part.strip()]
    return [part.strip() for part in re.split(r"\t+|\s{2,}", line) if part.strip()]


def extract_invoice_items(text: str) -> list[InvoiceItem]:
    items: list[InvoiceItem] = []
    header_keywords = (
        "项目名称",
        "规格型号",
        "税率",
        "金额合计",
        "价税合计",
        "购买方",
        "销售方",
    )
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(keyword in line for keyword in header_keywords):
            continue
        parts = _split_item_line(line)
        if len(parts) < 6:
            continue
        if len(parts) >= 8:
            name, model, unit, count, price, amount, tax_rate, tax_amount = parts[:8]
        else:
            name = parts[0]
            model = parts[1] if len(parts) > 1 else None
            unit = parts[2] if len(parts) > 2 else None
            count = parts[3] if len(parts) > 3 else None
            price = parts[4] if len(parts) > 4 else None
            amount = parts[5] if len(parts) > 5 else None
            tax_rate = parts[6] if len(parts) > 6 else None
            tax_amount = parts[7] if len(parts) > 7 else None

        parsed_item = InvoiceItem(
            name=name,
            model=model,
            unit=unit,
            count=_parse_float(count),
            price=_parse_float(price),
            amount=_parse_float(amount),
            tax_rate=_parse_tax_rate(tax_rate),
            tax_amount=_parse_float(tax_amount),
        )
        numeric_fields = [
            parsed_item.count,
            parsed_item.price,
            parsed_item.amount,
            parsed_item.tax_amount,
        ]
        if parsed_item.name and any(value is not None for value in numeric_fields):
            items.append(parsed_item)
    return items


def extract_invoice_fields(text: str) -> InvoiceFields:
    normalized = text.replace("￥", "").replace("¥", "")
    fields = InvoiceFields()
    fields.invoice_type = _search_any(INVOICE_TYPE_PATTERNS, normalized)
    fields.invoice_code = _search_any(FIELD_PATTERNS["invoice_code"], normalized)
    fields.invoice_number = _search_any(FIELD_PATTERNS["invoice_number"], normalized)
    fields.issue_date = _search_any(FIELD_PATTERNS["issue_date"], normalized)
    fields.check_code = _search_any(FIELD_PATTERNS["check_code"], normalized)
    fields.buyer_name = _search_any(BUYER_NAME_PATTERNS, normalized)
    fields.buyer_tax_id = _search_any(BUYER_TAX_ID_PATTERNS, normalized)
    fields.seller_name = _search_any(SELLER_NAME_PATTERNS, normalized)
    fields.seller_tax_id = _search_any(SELLER_TAX_ID_PATTERNS, normalized)

    amount_without_tax = _search(
        r"(?:^|[\r\n])(?:金额合计|合计)[：:\s]*([0-9]+(?:\.[0-9]+)?)",
        normalized,
    )
    if amount_without_tax is not None:
        fields.amount_without_tax = _parse_float(amount_without_tax)
    else:
        fields.amount_without_tax = _extract_amount("不含税金额", normalized)

    fields.tax_amount = _extract_amount("税额", normalized)
    fields.amount_with_tax = _extract_amount("价税合计", normalized)
    if (
        fields.amount_without_tax is None
        and fields.amount_with_tax is not None
        and fields.tax_amount is not None
    ):
        fields.amount_without_tax = round(fields.amount_with_tax - fields.tax_amount, 2)
    fields.items = extract_invoice_items(normalized)
    return fields
