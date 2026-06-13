from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.crypto_service import (
    generate_rsa_keypair, encrypt_private_key, decrypt_private_key,
    sign_document, verify_signature, generate_certificate
)
from app.services.auth_service import log_action
from app.models.models import Certificate, Document, User
from app import db
import datetime
import os

certificates_bp = Blueprint('certificates', __name__)

@certificates_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_cert():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Verificar si ya tiene certificado activo
    existing = Certificate.query.filter_by(
        user_id=user_id, status='active'
    ).first()
    if existing:
        return jsonify({'error': 'Ya tienes un certificado activo'}), 409

    # Generar par de claves RSA-2048
    private_pem, public_pem = generate_rsa_keypair()

    # Cifrar clave privada con AES-256-GCM
    secret = os.getenv('SECRET_KEY')
    encrypted_key, nonce = encrypt_private_key(private_pem, secret)

    # Generar certificado X.509
    cert_pem = generate_certificate(private_pem, public_pem, user.username)

    # Guardar en BD
    certificate = Certificate(
        user_id=user_id,
        public_key=public_pem,
        private_key_enc=f"{encrypted_key}:{nonce}",
        certificate_pem=cert_pem,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=365),
        status='active'
    )
    db.session.add(certificate)
    db.session.commit()

    log_action(user_id, 'GENERATE_CERTIFICATE', request.remote_addr,
               f'Certificado X.509 generado para {user.username}')

    return jsonify({
        'message': 'Certificado generado exitosamente',
        'certificate': certificate.to_dict()
    }), 201


@certificates_bp.route('/sign/<int:doc_id>', methods=['POST'])
@jwt_required()
def sign_doc(doc_id):
    user_id = int(get_jwt_identity())

    certificate = Certificate.query.filter_by(
        user_id=user_id, status='active'
    ).first()
    if not certificate:
        return jsonify({'error': 'No tienes un certificado activo'}), 404

    document = Document.query.filter_by(
        id=doc_id, user_id=user_id
    ).first()
    if not document:
        return jsonify({'error': 'Documento no encontrado'}), 404

    if document.signature:
        return jsonify({'error': 'El documento ya fue firmado'}), 409

    # Descifrar clave privada
    secret = os.getenv('SECRET_KEY')
    encrypted_key, nonce = certificate.private_key_enc.split(':')
    private_pem = decrypt_private_key(encrypted_key, nonce, secret)

    # Firmar el hash del documento con RSA
    signature = sign_document(private_pem, document.file_hash)

    # Guardar firma y vincular certificado
    document.signature = signature
    document.certificate_id = certificate.id
    db.session.commit()

    log_action(user_id, 'SIGN_DOCUMENT', request.remote_addr,
               f'Documento ID: {doc_id} firmado con certificado ID: {certificate.id}')

    return jsonify({
        'message': 'Documento firmado exitosamente',
        'document_id': doc_id,
        'signature': signature,
        'certificate_id': certificate.id
    }), 200


@certificates_bp.route('/verify-signature/<int:doc_id>', methods=['GET'])
@jwt_required()
def verify_doc_signature(doc_id):
    user_id = int(get_jwt_identity())

    document = Document.query.get(doc_id)
    if not document:
        return jsonify({'error': 'Documento no encontrado'}), 404

    if not document.signature:
        return jsonify({'error': 'El documento no tiene firma digital'}), 400

    certificate = Certificate.query.get(document.certificate_id)
    if not certificate:
        return jsonify({'error': 'Certificado no encontrado'}), 404

    is_valid = verify_signature(
        certificate.public_key,
        document.file_hash,
        document.signature
    )

    log_action(user_id, 'VERIFY_SIGNATURE', request.remote_addr,
               f'Documento ID: {doc_id} | Firma: {"VALIDA" if is_valid else "INVALIDA"}')

    return jsonify({
        'document_id': doc_id,
        'filename': document.filename,
        'signature_valid': is_valid,
        'certificate_id': certificate.id,
        'message': 'Firma digital valida' if is_valid else 'ALERTA: Firma invalida'
    }), 200


@certificates_bp.route('/list', methods=['GET'])
@jwt_required()
def list_certificates():
    user_id = int(get_jwt_identity())
    certs = Certificate.query.filter_by(user_id=user_id).all()
    return jsonify({'certificates': [c.to_dict() for c in certs]}), 200


@certificates_bp.route('/revoke/<int:cert_id>', methods=['POST'])
@jwt_required()
def revoke_certificate(cert_id):
    user_id = int(get_jwt_identity())

    certificate = Certificate.query.filter_by(
        id=cert_id, user_id=user_id
    ).first()
    if not certificate:
        return jsonify({'error': 'Certificado no encontrado'}), 404

    certificate.status = 'revoked'
    db.session.commit()

    log_action(user_id, 'REVOKE_CERTIFICATE', request.remote_addr,
               f'Certificado ID: {cert_id} revocado')

    return jsonify({'message': f'Certificado {cert_id} revocado exitosamente'}), 200