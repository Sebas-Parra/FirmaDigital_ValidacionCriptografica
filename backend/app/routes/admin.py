from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.models.models import User, Certificate, Document, Log
from app.services.auth_service import log_action
from app.routes.auth import _validate_user_fields
from app import db

admin_bp = Blueprint('admin', __name__)


def require_role(*roles):
    """Decorator que valida JWT y verifica que el usuario tenga uno de los roles permitidos."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = db.session.get(User, user_id)
            if not user or user.role not in roles:
                return jsonify({'error': 'Acceso denegado'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


@admin_bp.route('/users', methods=['GET'])
@require_role('admin', 'superuser')
def list_users():
    users = User.query.order_by(User.created_at.asc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


@admin_bp.route('/users', methods=['POST'])
@require_role('admin', 'superuser')
def create_user():
    from app.services.auth_service import hash_password
    current_id = int(get_jwt_identity())
    current = db.session.get(User, current_id)

    data = request.get_json() or {}
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Faltan campos: username, email, password'}), 400

    err = _validate_user_fields(data['username'], data['email'], data['password'])
    if err:
        return jsonify({'error': err}), 400

    role = data.get('role', 'user')
    if role not in ('user', 'admin', 'superuser'):
        return jsonify({'error': 'Rol inválido'}), 400

    # Admin solo puede crear usuarios con rol 'user'
    if current.role == 'admin' and role != 'user':
        return jsonify({'error': 'No tienes permiso para crear usuarios con ese rol'}), 403

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username ya existe'}), 409

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password']),
        role=role
    )
    db.session.add(user)
    db.session.commit()

    log_action(current_id, 'ADMIN_CREATE_USER', request.remote_addr,
               f'Admin creó usuario: {user.username} con rol {role}')
    return jsonify({'message': 'Usuario creado', 'user': user.to_dict()}), 201


@admin_bp.route('/users/<int:target_id>', methods=['PUT'])
@require_role('admin', 'superuser')
def update_user(target_id):
    current_id = int(get_jwt_identity())
    target = db.session.get(User, target_id)
    if not target:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}

    err = _validate_user_fields(data.get('username'), data.get('email'))
    if err:
        return jsonify({'error': err}), 400

    if 'username' in data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != target_id:
            return jsonify({'error': 'Username ya existe'}), 409
        target.username = data['username']

    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != target_id:
            return jsonify({'error': 'Email ya registrado'}), 409
        target.email = data['email']

    db.session.commit()
    log_action(current_id, 'ADMIN_UPDATE_USER', request.remote_addr,
               f'Admin actualizó usuario ID: {target_id}')
    return jsonify({'message': 'Usuario actualizado', 'user': target.to_dict()}), 200


@admin_bp.route('/users/<int:target_id>', methods=['DELETE'])
@require_role('admin', 'superuser')
def delete_user(target_id):
    current_id = int(get_jwt_identity())
    current = db.session.get(User, current_id)

    if target_id == current_id:
        return jsonify({'error': 'No puedes eliminar tu propia cuenta desde aquí'}), 400

    target = db.session.get(User, target_id)
    if not target:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Admin solo puede eliminar usuarios con rol 'user'
    if current.role == 'admin' and target.role in ('admin', 'superuser'):
        return jsonify({'error': 'No tienes permiso para eliminar este usuario'}), 403

    Log.query.filter_by(user_id=target_id).delete()
    Document.query.filter_by(user_id=target_id).delete()
    Certificate.query.filter_by(user_id=target_id).delete()
    db.session.delete(target)
    db.session.commit()

    log_action(current_id, 'ADMIN_DELETE_USER', request.remote_addr,
               f'Admin eliminó usuario ID: {target_id}')
    return jsonify({'message': 'Usuario eliminado'}), 200


@admin_bp.route('/users/<int:target_id>/role', methods=['PUT'])
@require_role('superuser')
def change_role(target_id):
    current_id = int(get_jwt_identity())

    if target_id == current_id:
        return jsonify({'error': 'No puedes cambiar tu propio rol'}), 400

    target = db.session.get(User, target_id)
    if not target:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}
    new_role = data.get('role')
    if new_role not in ('user', 'admin', 'superuser'):
        return jsonify({'error': 'Rol inválido. Opciones: user, admin, superuser'}), 400

    old_role = target.role
    target.role = new_role
    db.session.commit()

    log_action(current_id, 'CHANGE_ROLE', request.remote_addr,
               f'Usuario ID {target_id}: {old_role} → {new_role}')
    return jsonify({'message': f'Rol actualizado a {new_role}', 'user': target.to_dict()}), 200
