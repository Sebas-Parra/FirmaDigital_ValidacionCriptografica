from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import (
    register_user, get_user_by_email, 
    verify_password, log_action
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validar campos obligatorios
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    
    # Validar longitud de contraseña
    if len(data['password']) < 8:
        return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
    
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
    """Retorna el usuario autenticado actual"""
    from app.models.models import User
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'user': user.to_dict()}), 200