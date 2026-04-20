from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _extract(pattern: str, path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text, re.MULTILINE)
    assert match is not None, f"missing pattern in {path}"
    return match.group(1)


def test_version_is_consistent_between_pyproject_and_package() -> None:
    pyproject_version = _extract(r'^version = "([^"]+)"$', ROOT / "pyproject.toml")
    package_version = _extract(r'^__version__ = "([^"]+)"$', ROOT / "src/china_invoice_parser/__init__.py")
    assert pyproject_version == package_version
    assert re.fullmatch(r"\d+\.\d+\.\d+", pyproject_version)


def test_release_specs_exist_for_v0_1_0() -> None:
    assert (ROOT / "specs/README.md").exists()
    assert (ROOT / "specs/result-schema-v1.json").exists()
    assert (ROOT / "specs/release-0.1.0.md").exists()

