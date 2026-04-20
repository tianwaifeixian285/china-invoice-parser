from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from .models import SignatureStatus


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _parse_signature_refs(data: bytes) -> list[str]:
    refs: list[str] = []
    root = ET.fromstring(data)
    for element in root.iter():
        if _local_name(element.tag) != "Signature":
            continue
        base_loc = element.attrib.get("BaseLoc")
        if base_loc:
            refs.append(base_loc)
        elif element.text and element.text.strip():
            refs.append(element.text.strip())
    return refs


def _parse_signature_metadata(data: bytes) -> dict[str, str]:
    root = ET.fromstring(data)
    metadata: dict[str, str] = {}
    for element in root.iter():
        local_name = _local_name(element.tag)
        text = (element.text or "").strip()
        if not text:
            continue
        if local_name in {"ProviderName", "SignerName"}:
            metadata["signer"] = text
        elif local_name in {"SignDateTime", "SignatureDateTime"}:
            metadata["sign_time"] = text
        elif local_name in {"SignatureMethod", "DigestMethod"}:
            metadata["signature_method"] = text
    return metadata


def verify_ofd_signature(path: Path) -> tuple[SignatureStatus, list[str]]:
    warnings: list[str] = []
    try:
        with ZipFile(path) as archive:
            names = archive.namelist()
            manifest_candidates = [
                name for name in names if name.lower().endswith("signatures.xml")
            ]
            if not manifest_candidates:
                return (
                    SignatureStatus(
                        has_signature=False,
                        signature_format="ofd-sign",
                        verification_status="unsigned",
                    ),
                    warnings,
                )

            manifest_name = manifest_candidates[0]
            refs = _parse_signature_refs(archive.read(manifest_name))
            if not refs:
                warnings.append("OFD 签名清单存在，但未找到有效的签名引用。")
                return (
                    SignatureStatus(
                        has_signature=True,
                        signature_format="ofd-sign",
                        verification_status="invalid",
                    ),
                    warnings,
                )

            manifest_parent = Path(manifest_name).parent
            available = set(names)
            resolved_paths: list[str] = []
            for ref in refs:
                candidate = (manifest_parent / ref).as_posix()
                if candidate in available:
                    resolved_paths.append(candidate)
                elif ref in available:
                    resolved_paths.append(ref)
                else:
                    warnings.append(f"OFD 签名引用缺失: {ref}")

            if not resolved_paths:
                return (
                    SignatureStatus(
                        has_signature=True,
                        signature_format="ofd-sign",
                        verification_status="invalid",
                    ),
                    warnings,
                )

            metadata = _parse_signature_metadata(archive.read(resolved_paths[0]))
            return (
                SignatureStatus(
                    has_signature=True,
                    signature_format="ofd-sign",
                    verification_status="unknown",
                    signer=metadata.get("signer"),
                    sign_time=metadata.get("sign_time"),
                    cert_subject=metadata.get("signer"),
                    reason=(
                        f"已完成 OFD 签名结构校验，检测到 {len(resolved_paths)} 个签名文件；"
                        "密码学验签后续继续增强。"
                    ),
                ),
                warnings,
            )
    except Exception as exc:
        warnings.append(f"Failed to inspect OFD signatures: {exc}")
        return (
            SignatureStatus(
                signature_format="ofd-sign",
                verification_status="verification_error",
            ),
            warnings,
        )
