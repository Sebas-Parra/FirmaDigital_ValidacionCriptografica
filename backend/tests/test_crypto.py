"""
Tests unitarios de los módulos criptográficos.
Verifican directamente las funciones sin necesidad de Flask.
"""
import os
import pytest
from app.services.hash_service import hash_file, verify_file_integrity, encrypt_file, decrypt_file
from app.services.crypto_service import (
    generate_rsa_keypair, sign_document, verify_signature, generate_certificate,
    encrypt_private_key, decrypt_private_key
)


# --- SHA-256 / Integridad ---

def test_hash_mismo_archivo_mismo_hash():
    """Mismo contenido siempre produce el mismo hash (SHA-256 determinista)."""
    data = b'documento de prueba con contenido fijo'
    assert hash_file(data) == hash_file(data)


def test_hash_archivos_distintos_distinto_hash():
    """Contenidos diferentes producen hashes diferentes."""
    assert hash_file(b'documento original') != hash_file(b'documento modificado')


def test_hash_produce_hex_de_64_chars():
    """SHA-256 produce exactamente 64 caracteres hexadecimales."""
    h = hash_file(b'cualquier contenido')
    assert len(h) == 64
    assert all(c in '0123456789abcdef' for c in h)


def test_integridad_archivo_sin_cambios():
    """Archivo inalterado pasa la verificación de integridad."""
    data = b'contenido original del PDF'
    stored_hash = hash_file(data)
    assert verify_file_integrity(data, stored_hash) is True


def test_integridad_archivo_alterado():
    """Archivo modificado falla la verificación de integridad (detecta alteración)."""
    data = b'contenido original del PDF'
    stored_hash = hash_file(data)
    datos_alterados = b'contenido modificado maliciosamente'
    assert verify_file_integrity(datos_alterados, stored_hash) is False


def test_integridad_un_byte_diferente():
    """Cambiar un solo byte altera el hash completamente."""
    data = bytearray(b'documento integro')
    stored_hash = hash_file(bytes(data))
    data[0] ^= 0x01
    assert verify_file_integrity(bytes(data), stored_hash) is False


# --- AES-256-GCM ---

def test_aes_cifra_y_descifra_correctamente():
    """Cifrar y luego descifrar devuelve los datos originales."""
    data = b'contenido confidencial del documento PDF'
    encrypted, key, nonce = encrypt_file(data)
    decrypted = decrypt_file(encrypted, key, nonce)
    assert decrypted == data


def test_aes_texto_cifrado_distinto_al_original():
    """El texto cifrado es diferente al original."""
    data = b'contenido en claro'
    encrypted, key, nonce = encrypt_file(data)
    assert encrypted != data


def test_aes_clave_incorrecta_lanza_excepcion():
    """Intentar descifrar con clave incorrecta debe fallar."""
    data = b'dato secreto'
    encrypted, _, nonce = encrypt_file(data)
    clave_incorrecta = os.urandom(32)
    with pytest.raises(Exception):
        decrypt_file(encrypted, clave_incorrecta, nonce)


def test_aes_genera_claves_aleatorias():
    """Cada cifrado genera una clave y nonce distintos."""
    data = b'mismo contenido'
    _, key1, nonce1 = encrypt_file(data)
    _, key2, nonce2 = encrypt_file(data)
    assert key1 != key2
    assert nonce1 != nonce2


# --- RSA-2048 / Firma Digital ---

def test_rsa_genera_par_de_claves():
    """Genera clave privada y pública en formato PEM."""
    private_pem, public_pem = generate_rsa_keypair()
    assert '-----BEGIN PRIVATE KEY-----' in private_pem
    assert '-----BEGIN PUBLIC KEY-----' in public_pem


def test_firma_y_verificacion_valida():
    """Firmar con clave privada y verificar con pública debe ser exitoso."""
    private_pem, public_pem = generate_rsa_keypair()
    file_hash = hash_file(b'documento de prueba para firmar')
    signature = sign_document(private_pem, file_hash)
    assert verify_signature(public_pem, file_hash, signature) is True


def test_firma_invalida_si_documento_alterado():
    """Documento modificado invalida la firma digital (detecta manipulación)."""
    private_pem, public_pem = generate_rsa_keypair()
    hash_original = hash_file(b'documento original autentico')
    signature = sign_document(private_pem, hash_original)
    hash_alterado = hash_file(b'documento alterado por atacante')
    assert verify_signature(public_pem, hash_alterado, signature) is False


def test_firma_invalida_con_clave_publica_distinta():
    """La verificación falla si se usa una clave pública diferente."""
    private_pem, _ = generate_rsa_keypair()
    _, public_pem_otro = generate_rsa_keypair()
    file_hash = hash_file(b'documento')
    signature = sign_document(private_pem, file_hash)
    assert verify_signature(public_pem_otro, file_hash, signature) is False


def test_firma_invalida_con_firma_corrupta():
    """Firma base64 modificada debe ser rechazada."""
    import base64
    private_pem, public_pem = generate_rsa_keypair()
    file_hash = hash_file(b'documento')
    signature = sign_document(private_pem, file_hash)
    firma_corrupta = base64.b64encode(b'firma_falsa_manipulada').decode()
    assert verify_signature(public_pem, file_hash, firma_corrupta) is False


# --- Certificados X.509 ---

def test_genera_certificado_x509():
    """Genera un certificado X.509 válido en formato PEM."""
    private_pem, public_pem = generate_rsa_keypair()
    cert_pem = generate_certificate(private_pem, public_pem, 'usuario_test')
    assert '-----BEGIN CERTIFICATE-----' in cert_pem
    assert '-----END CERTIFICATE-----' in cert_pem


def test_certificado_contiene_datos_del_usuario():
    """El certificado X.509 incluye el CN del usuario."""
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    private_pem, public_pem = generate_rsa_keypair()
    cert_pem = generate_certificate(private_pem, public_pem, 'juan_prueba')
    cert = x509.load_pem_x509_certificate(cert_pem.encode())
    cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
    assert cn == 'juan_prueba'


def test_cifrado_clave_privada():
    """La clave privada cifrada con AES puede recuperarse correctamente."""
    private_pem, _ = generate_rsa_keypair()
    secret = 'clave-de-prueba-del-sistema-test'
    encrypted_b64, nonce_b64 = encrypt_private_key(private_pem, secret)
    recovered = decrypt_private_key(encrypted_b64, nonce_b64, secret)
    assert recovered == private_pem
