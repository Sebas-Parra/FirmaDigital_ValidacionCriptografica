from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
jwt = JWTManager()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB máximo por request

    origins = (os.getenv('ALLOWED_ORIGINS') or 'http://localhost:8080').split(',')
    CORS(app, origins=origins, supports_credentials=True)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from app.models.models import User, Certificate, Document, Log
        db.create_all()

    # Registramos los blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.routes.documents import documents_bp
    app.register_blueprint(documents_bp, url_prefix='/api/documents')

    from app.routes.certificates import certificates_bp
    app.register_blueprint(certificates_bp, url_prefix='/api/certificates')

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    return app