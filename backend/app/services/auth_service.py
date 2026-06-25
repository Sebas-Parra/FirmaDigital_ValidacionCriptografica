import bcrypt
from app.models.models import User, Log
from app import db

def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt"""
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )

def register_user(username: str, email: str, password: str, role: str = 'user'):
    """Registra un nuevo usuario"""
    # Verificar si ya existe
    if User.query.filter_by(email=email).first():
        return None, 'Email ya registrado'
    if User.query.filter_by(username=username).first():
        return None, 'Username ya existe'
    
    # Crear usuario
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role
    )
    db.session.add(user)
    db.session.commit()
    return user, None

def get_user_by_email(email: str):
    """Busca usuario por email"""
    return User.query.filter_by(email=email).first()

def log_action(user_id, action: str, ip_address: str, details: str = None):
    """Registra una acción en los logs de auditoría"""
    log = Log(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        details=details
    )
    db.session.add(log)
    db.session.commit()