"""
Análisis estadístico de operaciones criptográficas - FirmaDigital
Ejecutar: python analisis_estadistico.py
"""
import time
import statistics
import os
import bcrypt

from app.services.hash_service import hash_file, verify_file_integrity, encrypt_file, decrypt_file
from app.services.crypto_service import (
    generate_rsa_keypair, sign_document, verify_signature, generate_certificate
)

ITERACIONES = 50
ARCHIVO_1KB  = os.urandom(1_024)
ARCHIVO_10KB = os.urandom(10_240)
ARCHIVO_100KB = os.urandom(102_400)


def medir(fn, n=ITERACIONES):
    tiempos = []
    for _ in range(n):
        t0 = time.perf_counter()
        resultado = fn()
        tiempos.append((time.perf_counter() - t0) * 1000)
    return tiempos, resultado


def tabla(titulo, tiempos, unidad="ms"):
    print(f"\n{'─'*50}")
    print(f"  {titulo}")
    print(f"{'─'*50}")
    print(f"  n={len(tiempos)} iteraciones")
    print(f"  Media:    {statistics.mean(tiempos):.3f} {unidad}")
    print(f"  Mediana:  {statistics.median(tiempos):.3f} {unidad}")
    print(f"  Mín:      {min(tiempos):.3f} {unidad}")
    print(f"  Máx:      {max(tiempos):.3f} {unidad}")
    print(f"  Desv.Est: {statistics.stdev(tiempos):.3f} {unidad}")


def main():
    print("=" * 50)
    print("  ANÁLISIS ESTADÍSTICO — FirmaDigital")
    print("=" * 50)

    # 1. SHA-256 por tamaño de archivo
    for label, data in [("SHA-256 (1 KB)", ARCHIVO_1KB),
                         ("SHA-256 (10 KB)", ARCHIVO_10KB),
                         ("SHA-256 (100 KB)", ARCHIVO_100KB)]:
        t, _ = medir(lambda d=data: hash_file(d))
        tabla(label, t)

    # 2. AES-256-GCM cifrado
    for label, data in [("AES-256-GCM cifrado (1 KB)", ARCHIVO_1KB),
                         ("AES-256-GCM cifrado (10 KB)", ARCHIVO_10KB),
                         ("AES-256-GCM cifrado (100 KB)", ARCHIVO_100KB)]:
        t, (enc, key, nonce) = medir(lambda d=data: encrypt_file(d))
        tabla(label, t)

    # 3. AES-256-GCM descifrado (100 KB)
    enc100, key100, nonce100 = encrypt_file(ARCHIVO_100KB)
    t, _ = medir(lambda: decrypt_file(enc100, key100, nonce100))
    tabla("AES-256-GCM descifrado (100 KB)", t)

    # 4. RSA-2048 generación de claves
    t, (priv, pub) = medir(generate_rsa_keypair, n=10)
    tabla("RSA-2048 generación de claves", t, "ms")

    # 5. RSA firma digital
    file_hash = hash_file(ARCHIVO_10KB)
    priv_pem, pub_pem = generate_rsa_keypair()
    t, sig = medir(lambda: sign_document(priv_pem, file_hash))
    tabla("RSA-2048 firma digital", t)

    # 6. RSA verificación de firma (válida)
    signature = sign_document(priv_pem, file_hash)
    exitos = 0
    tiempos_ver = []
    for _ in range(ITERACIONES):
        t0 = time.perf_counter()
        ok = verify_signature(pub_pem, file_hash, signature)
        tiempos_ver.append((time.perf_counter() - t0) * 1000)
        if ok:
            exitos += 1
    tabla("RSA-2048 verificación de firma", tiempos_ver)
    print(f"  Tasa de éxito: {exitos}/{ITERACIONES} ({exitos/ITERACIONES*100:.1f}%)")

    # 7. Detección de alteraciones (firma inválida)
    alterados = 0
    for _ in range(ITERACIONES):
        hash_alterado = hash_file(os.urandom(len(ARCHIVO_10KB)))
        if not verify_signature(pub_pem, hash_alterado, signature):
            alterados += 1
    print(f"\n{'─'*50}")
    print(f"  Detección de alteraciones de firma")
    print(f"{'─'*50}")
    print(f"  Documentos alterados detectados: {alterados}/{ITERACIONES} ({alterados/ITERACIONES*100:.1f}%)")

    # 8. Integridad SHA-256 — detección de alteraciones
    original_hash = hash_file(ARCHIVO_10KB)
    detectados = sum(
        1 for _ in range(ITERACIONES)
        if not verify_file_integrity(os.urandom(len(ARCHIVO_10KB)), original_hash)
    )
    print(f"\n{'─'*50}")
    print(f"  Detección de alteraciones (hash SHA-256)")
    print(f"{'─'*50}")
    print(f"  Archivos alterados detectados: {detectados}/{ITERACIONES} ({detectados/ITERACIONES*100:.1f}%)")

    # 9. Generación de certificado X.509
    t, _ = medir(lambda: generate_certificate(priv_pem, pub_pem, "usuario_test"), n=10)
    tabla("Generación certificado X.509", t)

    # 10. bcrypt verificación de contraseña (simula login)
    password = b"contrasena_segura_123"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=10))
    t, _ = medir(lambda: bcrypt.checkpw(password, hashed), n=10)
    tabla("bcrypt verificación (login)", t)

    print(f"\n{'='*50}")
    print("  Análisis completado")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    # Necesita contexto Flask para importar los servicios correctamente
    import sys
    sys.path.insert(0, ".")
    main()
