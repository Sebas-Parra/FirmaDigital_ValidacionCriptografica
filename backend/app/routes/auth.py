from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import (
    register_user, get_user_by_email,
    verify_password, log_action, hash_password
)
from app import db
import re

auth_bp = Blueprint('auth', __name__)

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _validate_user_fields(username=None, email=None, password=None):
    """Retorna un mensaje de error o None si todo es válido."""
    if username is not None:
        if not (1 <= len(username) <= 50):
            return 'El username debe tener entre 1 y 50 caracteres'
        if not re.match(r'^[\w.\-]+$', username):
            return 'El username solo puede contener letras, números, puntos, guiones y guiones bajos'
    if email is not None:
        if len(email) > 120 or not EMAIL_RE.match(email):
            return 'Email inválido'
    if password is not None:
        if len(password) < 8:
            return 'La contraseña debe tener al menos 8 caracteres'
        if len(password) > 128:
            return 'La contraseña no puede superar 128 caracteres'
    return None


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    err = _validate_user_fields(data['username'], data['email'], data['password'])
    if err:
        return jsonify({'error': err}), 400

    user, error = register_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    if error:
        return jsonify({'error': error}), 409
    
    # Log de auditoría
    log_action(user.id, 'REGISTER', request.remote_addr, f'Usuario {user.username} registrado')
    
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    
    user = get_user_by_email(data['email'])
    
    if not user or not verify_password(data['password'], user.password_hash):
        log_action(None, 'LOGIN_FAILED', request.remote_addr, f'Intento fallido: {data["email"]}')
        return jsonify({'error': 'Credenciales incorrectas'}), 401
    
    # Crear token JWT
    access_token = create_access_token(identity=str(user.id))
    
    # Log de auditoría
    log_action(user.id, 'LOGIN', request.remote_addr, f'Usuario {user.username} inició sesión')
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    from app.models.models import User
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    from app.models.models import User
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400

    err = _validate_user_fields(
        data.get('username'),
        data.get('email'),
        data.get('password')
    )
    if err:
        return jsonify({'error': err}), 400

    if 'username' in data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Username ya existe'}), 409
        user.username = data['username']

    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email ya registrado'}), 409
        user.email = data['email']

    if 'password' in data:
        user.password_hash = hash_password(data['password'])

    db.session.commit()
    log_action(user_id, 'UPDATE_PROFILE', request.remote_addr, 'Perfil actualizado')
    return jsonify({'message': 'Perfil actualizado', 'user': user.to_dict()}), 200


@auth_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_me():
    from app.models.models import User, Certificate, Document, Log
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    Log.query.filter_by(user_id=user_id).delete()
    Document.query.filter_by(user_id=user_id).delete()
    Certificate.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    log_action(None, 'DELETE_ACCOUNT', request.remote_addr, f'Cuenta eliminada: user_id={user_id}')
    return jsonify({'message': 'Cuenta eliminada exitosamente'}), 200