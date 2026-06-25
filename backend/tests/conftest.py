import os

# Override env vars before any app import so load_dotenv() doesn't override them
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test-secret-key-32chars-minimum!!'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-testing!!'
os.environ['ALLOWED_ORIGINS'] = 'http://localhost:3000'
os.environ['SUPABASE_URL'] = 'https://placeholder.supabase.co'
os.environ['SERVICE_ROLE_KEY'] = 'placeholder-service-role-key'

import io
import pytest
from unittest.mock import patch
from app import create_app, db as _db


@pytest.fixture
def app():
    application = create_app()
    application.config['TESTING'] = True
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_storage():
    with patch('app.routes.documents.upload_file'), \
         patch('app.routes.documents.get_signed_url', return_value='http://fake.url/file.pdf'), \
         patch('app.routes.documents.delete_file'):
        yield


def register(client, username='usuario', email='usuario@test.com', password='password123'):
    return client.post('/api/auth/register', json={
        'username': username,
        'email': email,
        'password': password
    })


def login(client, email='usuario@test.com', password='password123'):
    res = client.post('/api/auth/login', json={'email': email, 'password': password})
    token = res.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def fake_pdf():
    return (io.BytesIO(b'%PDF-1.4 test document content'), 'test.pdf')
