from __future__ import annotations

from pathlib import Path


def _score_text(text: str) -> tuple[int, int]:
    markers = ("发票号码", "开票日期", "价税合计", "税额", "购买方", "销售方", "名称")
    marker_hits = sum(marker in text for marker in markers)
    return marker_hits, len("".join(text.split()))


def extract_pdf_text(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        from pypdf import PdfReader
    except ImportError:
        warnings.append("pypdf is not installed; PDF text extraction is unavailable.")
        return "", warnings

    try:
        reader = PdfReader(str(path))
        plain_parts = [page.extract_text() or "" for page in reader.pages]
        plain_text = "\n".join(plain_parts).strip()

        try:
            layout_parts = [
                page.extract_text(extraction_mode="layout") or "" for page in reader.pages
            ]
            layout_text = "\n".join(layout_parts).strip()
        except TypeError:
            layout_text = ""

        if _score_text(layout_text) > _score_text(plain_text):
            return layout_text, warnings
        return plain_text, warnings
    except Exception as exc:
        warnings.append(f"Failed to extract PDF text: {exc}")
        return "", warnings
