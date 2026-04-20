from china_invoice_parser.fields import extract_invoice_fields


def test_extract_amounts_prefers_tax_exclusive_total() -> None:
    text = """增值税电子普通发票
金额合计: 100.00
税额: 13.00
价税合计: 113.00
"""
    fields = extract_invoice_fields(text)
    assert fields.amount_without_tax == 100.00
    assert fields.tax_amount == 13.00
    assert fields.amount_with_tax == 113.00


def test_extract_amounts_can_backfill_tax_exclusive_total() -> None:
    text = """增值税电子普通发票
税额: 0.50
价税合计: 100.50
"""
    fields = extract_invoice_fields(text)
    assert fields.amount_without_tax == 100.00
    assert fields.tax_amount == 0.50
    assert fields.amount_with_tax == 100.50


def test_extract_invoice_items_from_pipe_separated_lines() -> None:
    text = """增值税电子普通发票
项目名称|规格型号|单位|数量|单价|金额|税率|税额
*信息技术服务*软件服务|标准版|次|2|50.00|100.00|13%|13.00
"""
    fields = extract_invoice_fields(text)
    assert len(fields.items) == 1
    item = fields.items[0]
    assert item.name == "*信息技术服务*软件服务"
    assert item.model == "标准版"
    assert item.unit == "次"
    assert item.count == 2.0
    assert item.price == 50.0
    assert item.amount == 100.0
    assert item.tax_rate == 0.13
    assert item.tax_amount == 13.0
