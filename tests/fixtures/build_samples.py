from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

FIXTURE_ROOT = Path(__file__).resolve().parent

PDF_TEXT = "\n".join(
    [
        "增值税电子普通发票",
        "发票代码: 012345678901",
        "发票号码: 12345678",
        "开票日期: 2026年04月20日",
        "购买方名称: 杭州示例科技有限公司",
        "购买方纳税人识别号: 91330100TEST00001",
        "销售方名称: 深圳示例服务有限公司",
        "销售方纳税人识别号: 91440300TEST00002",
        "项目名称|规格型号|单位|数量|单价|金额|税率|税额",
        "*信息技术服务*软件服务|标准版|次|1|100.00|100.00|13%|13.00",
        "税额: 13.00",
        "价税合计: 113.00",
    ]
)

OFD_DOCUMENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Document>
  <Line>增值税电子专用发票</Line>
  <Line>发票代码: 098765432109</Line>
  <Line>发票号码: 87654321</Line>
  <Line>开票日期: 2026年04月20日</Line>
  <Line>购买方名称: 北京示例采购有限公司</Line>
  <Line>购买方纳税人识别号: 91110000TEST00003</Line>
  <Line>销售方名称: 上海示例供应有限公司</Line>
  <Line>销售方纳税人识别号: 91310000TEST00004</Line>
  <Line>项目名称|规格型号|单位|数量|单价|金额|税率|税额</Line>
  <Line>*技术服务*实施服务|企业版|项|1|200.00|200.00|6%|12.00</Line>
  <Line>税额: 12.00</Line>
  <Line>价税合计: 212.00</Line>
</Document>
"""

OFD_SIGNATURES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Signatures>
  <Signature BaseLoc="Sign_0/Signature.xml" />
</Signatures>
"""

OFD_SIGNATURE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Signature>
  <SignedInfo>
    <ProviderName>测试签章服务商</ProviderName>
    <SignatureMethod>SM2-SM3</SignatureMethod>
    <SignDateTime>2026-04-20T09:00:00</SignDateTime>
  </SignedInfo>
</Signature>
"""


def _build_cjk_pdf(text: str, destination: Path) -> None:
    hex_text = text.encode("utf-16-be").hex().upper()
    content = f"BT\n/F1 12 Tf\n72 760 Td\n<{hex_text}> Tj\nET".encode()
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        ),
        (
            b"4 0 obj\n<< /Length "
            + str(len(content)).encode()
            + b" >>\nstream\n"
            + content
            + b"\nendstream\nendobj\n"
        ),
        (
            b"5 0 obj\n<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light "
            b"/Encoding /UniGB-UCS2-H /DescendantFonts [6 0 R] >>\nendobj\n"
        ),
        (
            b"6 0 obj\n<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light "
            b"/CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 4 >> "
            b"/DW 1000 >>\nendobj\n"
        ),
    ]
    parts = [b"%PDF-1.4\n"]
    offsets: list[int] = []
    total_length = len(parts[0])
    for obj in objects:
        offsets.append(total_length)
        parts.append(obj)
        total_length += len(obj)

    xref_start = total_length
    xref_parts = [b"xref\n0 7\n", b"0000000000 65535 f \n"]
    for offset in offsets:
        xref_parts.append(f"{offset:010d} 00000 n \n".encode())
    trailer = [
        b"trailer\n<< /Root 1 0 R /Size 7 >>\nstartxref\n",
        str(xref_start).encode() + b"\n%%EOF\n",
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"".join(parts + xref_parts + trailer))


def _build_ofd(destination: Path) -> None:
    def write_deterministic(archive: ZipFile, name: str, content: str) -> None:
        info = ZipInfo(filename=name, date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = ZIP_DEFLATED
        archive.writestr(info, content)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w") as archive:
        write_deterministic(archive, "OFD.xml", "<?xml version='1.0' encoding='UTF-8'?><OFD />")
        write_deterministic(archive, "Doc_0/Document.xml", OFD_DOCUMENT_XML)
        write_deterministic(archive, "Doc_0/Signs/Signatures.xml", OFD_SIGNATURES_XML)
        write_deterministic(archive, "Doc_0/Signs/Sign_0/Signature.xml", OFD_SIGNATURE_XML)


def main() -> None:
    _build_cjk_pdf(PDF_TEXT, FIXTURE_ROOT / "pdf" / "sanitized_vat_invoice.pdf")
    _build_ofd(FIXTURE_ROOT / "ofd" / "sanitized_vat_invoice.ofd")


if __name__ == "__main__":
    main()
