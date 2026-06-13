from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    certificates = db.relationship('Certificate', backref='user', lazy=True)
    documents = db.relationship('Document', backref='user', lazy=True)
    logs = db.relationship('Log', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    private_key_enc = db.Column(db.Text, nullable=False)
    certificate_pem = db.Column(db.Text, nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'certificate_pem': self.certificate_pem,
            'issued_at': self.issued_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'status': self.status
        }

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    signature = db.Column(db.Text, nullable=True)
    is_encrypted = db.Column(db.Boolean, default=False)
    storage_path = db.Column(db.String(500), nullable=True)  # ← nueva línea
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_hash': self.file_hash,
            'is_encrypted': self.is_encrypted,
            'storage_path': self.storage_path,
            'signature': self.signature,
            'certificate_id': self.certificate_id,
            'uploaded_at': self.uploaded_at.isoformat()
        }

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'ip_address': self.ip_address,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }