"""
Tests de integración para certificados X.509, firma digital y verificación.
"""
import io
from tests.conftest import register, login


def _upload_doc(client, headers, content=b'%PDF-1.4 doc'):
    data = {'file': (io.BytesIO(content), 'doc.pdf'), 'encrypt': 'false'}
    res = client.post('/api/documents/upload', data=data,
                      content_type='multipart/form-data', headers=headers)
    return res.get_json()['document']['id']


def test_generar_certificado_exitoso(client):
    register(client)
    headers = login(client)
    res = client.post('/api/certificates/generate', headers=headers)
    assert res.status_code == 201
    data = res.get_json()
    assert 'certificate' in data
    assert data['certificate']['status'] == 'active'


def test_no_dos_certificados_activos(client):
    """Un usuario no puede tener dos certificados activos simultáneamente."""
    register(client)
    headers = login(client)
    client.post('/api/certificates/generate', headers=headers)
    res = client.post('/api/certificates/generate', headers=headers)
    assert res.status_code == 409


def test_listar_certificados(client):
    register(client)
    headers = login(client)
    client.post('/api/certificates/generate', headers=headers)
    res = client.get('/api/certificates/list', headers=headers)
    assert res.status_code == 200
    assert len(res.get_json()['certificates']) == 1


def test_revocar_certificado(client):
    register(client)
    headers = login(client)
    client.post('/api/certificates/generate', headers=headers)
    cert_id = client.get('/api/certificates/list', headers=headers)\
                    .get_json()['certificates'][0]['id']
    res = client.post(f'/api/certificates/revoke/{cert_id}', headers=headers)
    assert res.status_code == 200
    cert = client.get('/api/certificates/list', headers=headers)\
                 .get_json()['certificates'][0]
    assert cert['status'] == 'revoked'


def test_firmar_documento(client):
    register(client)
    headers = login(client)
    client.post('/api/certificates/generate', headers=headers)
    doc_id = _upload_doc(client, headers)
    res = client.post(f'/api/certificates/sign/{doc_id}', headers=headers)
    assert res.status_code == 200
    assert 'signature' in res.get_json()


def test_no_firmar_dos_veces(client):
    register(client)
    headers = login(client)
    client.post('/api/certificates/generate', headers=headers)
    doc_id = _upload_doc(client, headers)
    client.post(f'/api/certificates/sign/{doc_id}', headers=headers)
    res = client.post(f'/api/certificates/sign/{doc_id}', headers=headers)
    assert res.status_code == 409


def test_verificar_firma_valida(client):
    """Firma digital válida: documento no modificado → firma auténtica."""
    register(client)
    headers = login(client)
    client.post('/api/certificates/generate', headers=headers)
    doc_id = _upload_doc(client, headers)
    client.post(f'/api/certificates/sign/{doc_id}', headers=headers)
    res = client.get(f'/api/certificates/verify-signature/{doc_id}', headers=headers)
    assert res.status_code == 200
    assert res.get_json()['signature_valid'] is True


def test_verificar_firma_invalida_tras_alteracion(client):
    """Documento alterado → firma inválida (el hash no coincide con la firma original)."""
    register(client)
    headers = login(client)
    client.post('/api/certificates/generate', headers=headers)
    doc_id = _upload_doc(client, headers)
    client.post(f'/api/certificates/sign/{doc_id}', headers=headers)

    # Simular alteración: cambiar el file_hash en la BD directamente
    from app import db
    from app.models.models import Document
    from flask import current_app
    with client.application.app_context():
        doc = Document.query.get(doc_id)
        doc.file_hash = 'a' * 64
        db.session.commit()

    res = client.get(f'/api/certificates/verify-signature/{doc_id}', headers=headers)
    assert res.status_code == 200
    assert res.get_json()['signature_valid'] is False


def test_certificado_tiene_fecha_expiracion(client):
    """Los certificados emitidos tienen fecha de vencimiento a un año."""
    from datetime import datetime
    register(client)
    headers = login(client)
    res = client.post('/api/certificates/generate', headers=headers)
    cert = res.get_json()['certificate']
    issued = datetime.fromisoformat(cert['issued_at'])
    expires = datetime.fromisoformat(cert['expires_at'])
    delta_days = (expires - issued).days
    assert 364 <= delta_days <= 366


def test_firmar_sin_certificado_activo(client):
    """Sin certificado activo no se puede firmar."""
    register(client)
    headers = login(client)
    doc_id = _upload_doc(client, headers)
    res = client.post(f'/api/certificates/sign/{doc_id}', headers=headers)
    assert res.status_code == 404
