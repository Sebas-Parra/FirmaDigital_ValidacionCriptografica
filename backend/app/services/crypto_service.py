from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.x509 import NameAttribute, CertificateBuilder, random_serial_number
from cryptography.x509.oid import NameOID
from cryptography import x509
import datetime
import base64
import os

def generate_rsa_keypair():
    """Genera par de claves RSA-2048"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_pem, public_pem

def encrypt_private_key(private_pem: str, secret: str) -> tuple:
    """Cifra la clave privada con AES-256-GCM"""
    key = secret.encode('utf-8')[:32].ljust(32, b'0')
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, private_pem.encode('utf-8'), None)
    return (
        base64.b64encode(encrypted).decode('utf-8'),
        base64.b64encode(nonce).decode('utf-8')
    )

def decrypt_private_key(encrypted_b64: str, nonce_b64: str, secret: str) -> str:
    """Descifra la clave privada"""
    key = secret.encode('utf-8')[:32].ljust(32, b'0')
    aesgcm = AESGCM(key)
    encrypted = base64.b64decode(encrypted_b64)
    nonce = base64.b64decode(nonce_b64)
    decrypted = aesgcm.decrypt(nonce, encrypted, None)
    return decrypted.decode('utf-8')

def sign_document(private_pem: str, file_hash: str) -> str:
    """Firma el hash de un documento con RSA"""
    private_key = serialization.load_pem_private_key(
        private_pem.encode('utf-8'), password=None
    )
    signature = private_key.sign(
        file_hash.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(public_pem: str, file_hash: str, signature_b64: str) -> bool:
    """Verifica la firma digital de un documento"""
    try:
        public_key = serialization.load_pem_public_key(public_pem.encode('utf-8'))
        signature = base64.b64decode(signature_b64)
        public_key.verify(
            signature,
            file_hash.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def generate_certificate(private_pem: str, public_pem: str, username: str, days: int = 365):
    """Genera un certificado X.509 autofirmado (CA simulada)"""
    private_key = serialization.load_pem_private_key(
        private_pem.encode('utf-8'), password=None
    )
    public_key = serialization.load_pem_public_key(public_pem.encode('utf-8'))

    subject = issuer = x509.Name([
        NameAttribute(NameOID.COUNTRY_NAME, "EC"),
        NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Pichincha"),
        NameAttribute(NameOID.LOCALITY_NAME, "Quito"),
        NameAttribute(NameOID.ORGANIZATION_NAME, "FirmaDigital CA"),
        NameAttribute(NameOID.COMMON_NAME, username),
    ])

    cert = (
        CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=days))
        .sign(private_key, hashes.SHA256())
    )

    return cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')