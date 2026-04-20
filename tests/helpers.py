from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
from pyhanko.sign.signers import PdfSignatureMetadata, PdfSigner


def create_self_signed_material(target_dir: Path) -> tuple[Path, Path]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "China Invoice Parser Test"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Sanitized PDF Signer"),
        ]
    )
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )

    key_path = target_dir / "signer.key.pem"
    cert_path = target_dir / "signer.cert.pem"
    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    return key_path, cert_path


def sign_pdf_fixture(source_pdf: Path, signed_pdf: Path, work_dir: Path) -> Path:
    key_path, cert_path = create_self_signed_material(work_dir)
    signer = signers.SimpleSigner.load(key_file=str(key_path), cert_file=str(cert_path))
    with source_pdf.open("rb") as handle:
        writer = IncrementalPdfFileWriter(handle)
        output = PdfSigner(
            signature_meta=PdfSignatureMetadata(field_name="Signature1"),
            signer=signer,
        ).sign_pdf(writer)
    signed_pdf.write_bytes(output.getbuffer())
    return signed_pdf
