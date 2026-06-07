import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def hash_file(file_bytes: bytes) -> str:
    """Genera hash SHA-256 de un archivo"""
    return hashlib.sha256(file_bytes).hexdigest()

def hash_text(text: str) -> str:
    """Genera hash SHA-256 de un texto"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def verify_file_integrity(file_bytes: bytes, stored_hash: str) -> bool:
    """Verifica si un archivo fue alterado comparando su hash"""
    current_hash = hash_file(file_bytes)
    return current_hash == stored_hash

def encrypt_file(file_bytes: bytes) -> tuple:
    """Cifra un archivo con AES-256-GCM"""
    key = os.urandom(32)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, file_bytes, None)
    return encrypted, key, nonce

def decrypt_file(encrypted_bytes: bytes, key: bytes, nonce: bytes) -> bytes:
    """Descifra un archivo con AES-256-GCM"""
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, encrypted_bytes, None)