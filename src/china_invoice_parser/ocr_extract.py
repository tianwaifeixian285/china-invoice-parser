from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
DEFAULT_OCR_LANG = "chi_sim+eng"


def _get_ocr_lang() -> str:
    return os.getenv("CHINA_INVOICE_PARSER_OCR_LANG", DEFAULT_OCR_LANG)


def _load_ocr_dependencies() -> tuple[object | None, object | None, list[str]]:
    warnings: list[str] = []
    if shutil.which("tesseract") is None:
        warnings.append("tesseract is not installed; OCR is unavailable.")
        return None, None, warnings

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        warnings.append("Pillow or pytesseract is not installed; OCR is unavailable.")
        return None, None, warnings

    return Image, pytesseract, warnings


def extract_image_text(path: Path) -> tuple[str, list[str]]:
    image_module, pytesseract_module, warnings = _load_ocr_dependencies()
    if image_module is None or pytesseract_module is None:
        return "", warnings

    try:
        with image_module.open(path) as image:
            text = pytesseract_module.image_to_string(image, lang=_get_ocr_lang())
        return text.strip(), warnings
    except Exception as exc:
        warnings.append(f"Failed to OCR image: {exc}")
        return "", warnings


def extract_pdf_text_with_ocr(path: Path) -> tuple[str, list[str]]:
    image_module, pytesseract_module, warnings = _load_ocr_dependencies()
    if image_module is None or pytesseract_module is None:
        return "", warnings

    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        warnings.append("pdftoppm is not installed; PDF OCR is unavailable.")
        return "", warnings

    try:
        with tempfile.TemporaryDirectory(prefix="china-invoice-parser-ocr-") as tmpdir:
            output_prefix = Path(tmpdir) / "page"
            subprocess.run(
                [pdftoppm, "-r", "200", "-png", str(path), str(output_prefix)],
                check=True,
                capture_output=True,
                text=True,
            )
            image_paths = sorted(Path(tmpdir).glob("page-*.png"))
            if not image_paths:
                warnings.append("pdftoppm did not produce any page images for OCR.")
                return "", warnings

            text_chunks: list[str] = []
            for image_path in image_paths:
                with image_module.open(image_path) as image:
                    page_text = pytesseract_module.image_to_string(image, lang=_get_ocr_lang())
                if page_text.strip():
                    text_chunks.append(page_text.strip())
            return "\n".join(text_chunks).strip(), warnings
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        warnings.append(f"Failed to rasterize PDF for OCR: {detail}")
        return "", warnings
    except Exception as exc:
        warnings.append(f"Failed to OCR PDF: {exc}")
        return "", warnings
