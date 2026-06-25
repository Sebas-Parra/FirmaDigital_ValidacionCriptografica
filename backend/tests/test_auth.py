"""
Tests de integración para autenticación y gestión de usuarios (CRUD).
"""
from tests.conftest import register, login


def test_registro_exitoso(client):
    res = register(client)
    assert res.status_code == 201
    data = res.get_json()
    assert 'user' in data
    assert data['user']['username'] == 'usuario'


def test_registro_email_duplicado(client):
    register(client)
    res = register(client, username='otro')
    assert res.status_code == 409
    assert 'Email' in res.get_json()['error']


def test_registro_username_duplicado(client):
    register(client)
    res = register(client, email='otro@test.com')
    assert res.status_code == 409


def test_registro_contrasena_corta(client):
    res = register(client, password='abc')
    assert res.status_code == 400
    assert 'contraseña' in res.get_json()['error'].lower()


def test_registro_campos_faltantes(client):
    res = client.post('/api/auth/register', json={'username': 'solo_username'})
    assert res.status_code == 400


def test_login_exitoso(client):
    register(client)
    res = client.post('/api/auth/login', json={
        'email': 'usuario@test.com',
        'password': 'password123'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'access_token' in data
    assert 'user' in data


def test_login_contrasena_incorrecta(client):
    register(client)
    res = client.post('/api/auth/login', json={
        'email': 'usuario@test.com',
        'password': 'incorrecta'
    })
    assert res.status_code == 401


def test_login_email_inexistente(client):
    res = client.post('/api/auth/login', json={
        'email': 'noexiste@test.com',
        'password': 'password123'
    })
    assert res.status_code == 401


def test_me_autenticado(client):
    register(client)
    headers = login(client)
    res = client.get('/api/auth/me', headers=headers)
    assert res.status_code == 200
    assert res.get_json()['user']['email'] == 'usuario@test.com'


def test_me_sin_token(client):
    res = client.get('/api/auth/me')
    assert res.status_code == 401


# --- Actualizar perfil (CRUD Update) ---

def test_actualizar_username(client):
    register(client)
    headers = login(client)
    res = client.put('/api/auth/me', json={'username': 'nuevo_nombre'}, headers=headers)
    assert res.status_code == 200
    assert res.get_json()['user']['username'] == 'nuevo_nombre'


def test_actualizar_email(client):
    register(client)
    headers = login(client)
    res = client.put('/api/auth/me', json={'email': 'nuevo@test.com'}, headers=headers)
    assert res.status_code == 200
    assert res.get_json()['user']['email'] == 'nuevo@test.com'


def test_actualizar_contrasena(client):
    register(client)
    headers = login(client)
    res = client.put('/api/auth/me', json={'password': 'nueva_password123'}, headers=headers)
    assert res.status_code == 200
    # Verificar que el nuevo password funciona para login
    res2 = client.post('/api/auth/login', json={
        'email': 'usuario@test.com',
        'password': 'nueva_password123'
    })
    assert res2.status_code == 200


def test_actualizar_username_duplicado_falla(client):
    register(client, username='usuario_a', email='a@test.com')
    register(client, username='usuario_b', email='b@test.com')
    headers = login(client, email='a@test.com')
    res = client.put('/api/auth/me', json={'username': 'usuario_b'}, headers=headers)
    assert res.status_code == 409


def test_actualizar_sin_token(client):
    res = client.put('/api/auth/me', json={'username': 'x'})
    assert res.status_code == 401


# --- Eliminar cuenta (CRUD Delete) ---

def test_eliminar_cuenta(client):
    register(client)
    headers = login(client)
    res = client.delete('/api/auth/me', headers=headers)
    assert res.status_code == 200
    # Verificar que ya no puede loguearse
    res2 = client.post('/api/auth/login', json={
        'email': 'usuario@test.com',
        'password': 'password123'
    })
    assert res2.status_code == 401


def test_eliminar_sin_token(client):
    res = client.delete('/api/auth/me')
    assert res.status_code == 401
