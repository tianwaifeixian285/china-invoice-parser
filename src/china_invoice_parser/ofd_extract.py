from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

TEXT_SUFFIXES = (".xml", ".ofd", ".txt")


def _extract_xml_text(data: bytes) -> str | None:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None
    chunks = [text.strip() for text in root.itertext() if text and text.strip()]
    if not chunks:
        return None
    return "\n".join(chunks)


def extract_ofd_text(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        chunks: list[str] = []
        with ZipFile(path) as archive:
            for name in archive.namelist():
                lower = name.lower()
                if not lower.endswith(TEXT_SUFFIXES):
                    continue
                try:
                    data = archive.read(name)
                    xml_text = _extract_xml_text(data)
                    if xml_text:
                        chunks.append(xml_text)
                    else:
                        chunks.append(data.decode("utf-8", errors="ignore"))
                except Exception:
                    continue
        if not chunks:
            warnings.append("No readable XML/text payloads were found in the OFD container.")
        return "\n".join(chunks).strip(), warnings
    except Exception as exc:
        warnings.append(f"Failed to read OFD container: {exc}")
        return "", warnings
