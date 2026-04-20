from __future__ import annotations

from pathlib import Path

from .models import SignatureStatus


def _safe_name(value: object) -> str | None:
    if value is None:
        return None
    string_value = str(value).strip()
    return string_value or None


def verify_pdf_signature(path: Path) -> tuple[SignatureStatus, list[str]]:
    warnings: list[str] = []
    try:
        from pyhanko.pdf_utils.reader import PdfFileReader
        from pyhanko.sign.validation import validate_pdf_signature
        from pyhanko_certvalidator import ValidationContext
    except ImportError:
        warnings.append("pyHanko is not installed; PDF signature validation is unavailable.")
        return SignatureStatus(signature_format="pdf-pkcs7", verification_status="unknown"), warnings

    try:
        with path.open("rb") as handle:
            reader = PdfFileReader(handle)
            embedded = list(reader.embedded_signatures)
            if not embedded:
                return SignatureStatus(has_signature=False, signature_format="pdf-pkcs7", verification_status="unsigned"), warnings

            sig = embedded[0]
            signer_cert = getattr(sig, "signer_cert", None)
            cert_subject = _safe_name(getattr(getattr(signer_cert, "subject", None), "human_friendly", None))
            cert_issuer = _safe_name(getattr(getattr(signer_cert, "issuer", None), "human_friendly", None))
            sign_time = getattr(sig, "self_reported_timestamp", None)
            validation_status = validate_pdf_signature(
                sig,
                signer_validation_context=ValidationContext(allow_fetching=False),
            )
            if validation_status.bottom_line:
                verification_status = "valid"
                reason = validation_status.summary()
            elif validation_status.intact and validation_status.valid:
                verification_status = "unknown"
                reason = "签名完整且密码学校验通过，但当前环境无法建立完整信任链。"
            else:
                verification_status = "invalid"
                reason = validation_status.summary()

            status = SignatureStatus(
                has_signature=True,
                signature_format="pdf-pkcs7",
                verification_status=verification_status,
                signer=cert_subject,
                sign_time=sign_time.isoformat() if sign_time else None,
                cert_subject=cert_subject,
                cert_issuer=cert_issuer,
                reason=reason,
            )
            return status, warnings
    except Exception as exc:
        warnings.append(f"Failed to inspect PDF signatures: {exc}")
        return SignatureStatus(signature_format="pdf-pkcs7", verification_status="verification_error"), warnings
