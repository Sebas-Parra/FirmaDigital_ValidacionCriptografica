"""
Tests de integración para subida, verificación de integridad y descifrado de documentos.
"""
import io
import base64
from tests.conftest import register, login, fake_pdf
from app.services.hash_service import hash_file, encrypt_file


def _upload(client, headers, content=b'%PDF-1.4 test', filename='doc.pdf', encrypt=False):
    data = {
        'file': (io.BytesIO(content), filename),
        'encrypt': str(encrypt).lower()
    }
    return client.post('/api/documents/upload', data=data,
                       content_type='multipart/form-data', headers=headers)


def test_subir_pdf_exitoso(client):
    register(client)
    headers = login(client)
    res = _upload(client, headers)
    assert res.status_code == 201
    data = res.get_json()
    assert 'file_hash' in data
    assert len(data['file_hash']) == 64


def test_subir_no_pdf_rechazado(client):
    register(client)
    headers = login(client)
    data = {'file': (io.BytesIO(b'contenido'), 'archivo.txt')}
    res = client.post('/api/documents/upload', data=data,
                      content_type='multipart/form-data', headers=headers)
    assert res.status_code == 400


def test_subir_sin_archivo(client):
    register(client)
    headers = login(client)
    res = client.post('/api/documents/upload', json={}, headers=headers)
    assert res.status_code == 400


def test_subir_sin_token(client):
    res = _upload(client, {})
    assert res.status_code == 401


def test_listar_documentos_vacio(client):
    register(client)
    headers = login(client)
    res = client.get('/api/documents/list', headers=headers)
    assert res.status_code == 200
    assert res.get_json()['documents'] == []


def test_listar_documentos_despues_de_subir(client):
    register(client)
    headers = login(client)
    _upload(client, headers)
    res = client.get('/api/documents/list', headers=headers)
    assert res.status_code == 200
    assert len(res.get_json()['documents']) == 1


def test_hash_documento_es_sha256_del_contenido(client):
    """El hash almacenado debe corresponder al SHA-256 del archivo subido."""
    register(client)
    headers = login(client)
    contenido = b'%PDF-1.4 contenido verificable del documento'
    res = _upload(client, headers, content=contenido)
    assert res.status_code == 201
    hash_esperado = hash_file(contenido)
    assert res.get_json()['file_hash'] == hash_esperado


def test_verificar_integridad_archivo_intacto(client):
    """Mismo archivo → integridad válida."""
    register(client)
    headers = login(client)
    contenido = b'%PDF-1.4 documento de prueba de integridad'
    _upload(client, headers, content=contenido)
    docs = client.get('/api/documents/list', headers=headers).get_json()['documents']
    doc_id = docs[0]['id']

    data = {
        'file': (io.BytesIO(contenido), 'doc.pdf'),
        'document_id': str(doc_id)
    }
    res = client.post('/api/documents/verify', data=data,
                      content_type='multipart/form-data', headers=headers)
    assert res.status_code == 200
    assert res.get_json()['is_valid'] is True


def test_verificar_integridad_archivo_alterado(client):
    """Archivo modificado → integridad inválida (detecta alteración)."""
    register(client)
    headers = login(client)
    contenido_original = b'%PDF-1.4 contenido original autentico'
    _upload(client, headers, content=contenido_original)
    docs = client.get('/api/documents/list', headers=headers).get_json()['documents']
    doc_id = docs[0]['id']

    contenido_alterado = b'%PDF-1.4 contenido manipulado maliciosamente'
    data = {
        'file': (io.BytesIO(contenido_alterado), 'doc.pdf'),
        'document_id': str(doc_id)
    }
    res = client.post('/api/documents/verify', data=data,
                      content_type='multipart/form-data', headers=headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body['is_valid'] is False
    assert body['stored_hash'] != body['current_hash']


def test_subir_con_cifrado_devuelve_clave(client):
    """Subir con encrypt=true devuelve la clave y nonce AES."""
    register(client)
    headers = login(client)
    res = _upload(client, headers, encrypt=True)
    assert res.status_code == 201
    data = res.get_json()
    assert 'encryption_key' in data
    assert 'encryption_nonce' in data


def test_descifrar_archivo_correcto(client):
    """Descifrar con la clave correcta devuelve los datos originales."""
    register(client)
    headers = login(client)
    contenido = b'%PDF-1.4 contenido a cifrar y descifrar'
    encrypted, key, nonce = encrypt_file(contenido)
    payload = {
        'encrypted_data': base64.b64encode(encrypted).decode(),
        'key': base64.b64encode(key).decode(),
        'nonce': base64.b64encode(nonce).decode()
    }
    res = client.post('/api/documents/decrypt', json=payload, headers=headers)
    assert res.status_code == 200
    decrypted = base64.b64decode(res.get_json()['decrypted_data'])
    assert decrypted == contenido


def test_descifrar_clave_incorrecta_falla(client):
    """Descifrar con clave incorrecta debe retornar error 400."""
    register(client)
    headers = login(client)
    import os
    contenido = b'%PDF-1.4 dato secreto'
    encrypted, _, nonce = encrypt_file(contenido)
    payload = {
        'encrypted_data': base64.b64encode(encrypted).decode(),
        'key': base64.b64encode(os.urandom(32)).decode(),
        'nonce': base64.b64encode(nonce).decode()
    }
    res = client.post('/api/documents/decrypt', json=payload, headers=headers)
    assert res.status_code == 400


def test_eliminar_documento(client):
    register(client)
    headers = login(client)
    _upload(client, headers)
    docs = client.get('/api/documents/list', headers=headers).get_json()['documents']
    doc_id = docs[0]['id']
    res = client.delete(f'/api/documents/{doc_id}', headers=headers)
    assert res.status_code == 200
    docs_despues = client.get('/api/documents/list', headers=headers).get_json()['documents']
    assert len(docs_despues) == 0
