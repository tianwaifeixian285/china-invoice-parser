from __future__ import annotations

from pathlib import Path


def extract_pdf_text(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        from pypdf import PdfReader
    except ImportError:
        warnings.append("pypdf is not installed; PDF text extraction is unavailable.")
        return "", warnings

    try:
        reader = PdfReader(str(path))
        text_parts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(text_parts).strip(), warnings
    except Exception as exc:
        warnings.append(f"Failed to extract PDF text: {exc}")
        return "", warnings

