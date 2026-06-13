from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.hash_service import hash_file, verify_file_integrity, encrypt_file, decrypt_file
from app.services.auth_service import log_action
from app.models.models import Document
from app import db
import base64

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    user_id = int(get_jwt_identity())

    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Solo se permiten archivos PDF'}), 400

    file_bytes = file.read()
    file_hash = hash_file(file_bytes)
    encrypt = request.form.get('encrypt', 'false').lower() == 'true'

    storage_path = None
    encryption_key = None
    encryption_nonce = None

    if encrypt:
        encrypted_bytes, key, nonce = encrypt_file(file_bytes)
        storage_path = f"documentos/{user_id}/{file.filename}.enc"
        encryption_key = base64.b64encode(key).decode('utf-8')
        encryption_nonce = base64.b64encode(nonce).decode('utf-8')
    else:
        storage_path = f"documentos/{user_id}/{file.filename}"

    document = Document(
        user_id=user_id,
        filename=file.filename,
        file_hash=file_hash,
        is_encrypted=encrypt,
        storage_path=storage_path
    )
    db.session.add(document)
    db.session.commit()

    log_action(user_id, 'UPLOAD_DOCUMENT', request.remote_addr,
               f'Archivo: {file.filename} | Hash: {file_hash} | Cifrado: {encrypt}')

    response = {
        'message': 'Documento subido exitosamente',
        'document': document.to_dict(),
        'file_hash': file_hash
    }

    if encrypt:
        response['encryption_key'] = encryption_key
        response['encryption_nonce'] = encryption_nonce
        response['warning'] = 'Guarda la clave y nonce — son necesarios para descifrar'

    return jsonify(response), 201


@documents_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_document():
    user_id = int(get_jwt_identity())

    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    data = request.form
    if 'document_id' not in data:
        return jsonify({'error': 'Falta el document_id'}), 400

    file = request.files['file']
    file_bytes = file.read()

    document = Document.query.filter_by(
        id=int(data['document_id']),
        user_id=user_id
    ).first()

    if not document:
        return jsonify({'error': 'Documento no encontrado'}), 404

    is_valid = verify_file_integrity(file_bytes, document.file_hash)

    log_action(user_id, 'VERIFY_DOCUMENT', request.remote_addr,
               f'Documento ID: {document.id} | Integridad: {"OK" if is_valid else "ALTERADO"}')

    return jsonify({
        'document_id': document.id,
        'filename': document.filename,
        'stored_hash': document.file_hash,
        'current_hash': hash_file(file_bytes),
        'is_valid': is_valid,
        'message': 'El documento es autentico' if is_valid else 'ALERTA: El documento fue alterado'
    }), 200


@documents_bp.route('/decrypt', methods=['POST'])
@jwt_required()
def decrypt_document():
    user_id = int(get_jwt_identity())

    data = request.get_json()
    if not all(k in data for k in ['encrypted_data', 'key', 'nonce']):
        return jsonify({'error': 'Faltan campos: encrypted_data, key, nonce'}), 400

    try:
        encrypted_bytes = base64.b64decode(data['encrypted_data'])
        key = base64.b64decode(data['key'])
        nonce = base64.b64decode(data['nonce'])

        decrypted_bytes = decrypt_file(encrypted_bytes, key, nonce)

        log_action(user_id, 'DECRYPT_DOCUMENT', request.remote_addr, 'Archivo descifrado exitosamente')

        return jsonify({
            'message': 'Archivo descifrado exitosamente',
            'decrypted_data': base64.b64encode(decrypted_bytes).decode('utf-8')
        }), 200

    except Exception:
        log_action(user_id, 'DECRYPT_FAILED', request.remote_addr, 'Fallo al descifrar — clave incorrecta o archivo alterado')
        return jsonify({'error': 'No se pudo descifrar — clave incorrecta o archivo manipulado'}), 400


@documents_bp.route('/list', methods=['GET'])
@jwt_required()
def list_documents():
    user_id = int(get_jwt_identity())
    documents = Document.query.filter_by(user_id=user_id).all()
    return jsonify({'documents': [d.to_dict() for d in documents]}), 200


@documents_bp.route('/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    user_id = int(get_jwt_identity())
    document = Document.query.filter_by(id=doc_id, user_id=user_id).first()

    if not document:
        return jsonify({'error': 'Documento no encontrado'}), 404

    db.session.delete(document)
    db.session.commit()

    log_action(user_id, 'DELETE_DOCUMENT', request.remote_addr, f'Documento ID: {doc_id} eliminado')

    return jsonify({'message': 'Documento eliminado'}), 200