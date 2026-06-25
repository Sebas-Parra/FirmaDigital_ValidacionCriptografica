import click
from app import create_app, db

app = create_app()


@app.cli.command('create-superuser')
@click.argument('email')
@click.option('--username', prompt='Username', help='Nombre de usuario')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Contraseña')
def create_superuser(email, username, password):
    """Crea un superusuario o promueve uno existente. Uso: flask create-superuser email@ejemplo.com"""
    from app.models.models import User
    from app.services.auth_service import hash_password

    user = User.query.filter_by(email=email).first()
    if user:
        user.role = 'superuser'
        db.session.commit()
        click.echo(f'[OK] {user.username} ({email}) promovido a superuser')
    else:
        if len(password) < 8:
            click.echo('[ERROR] La contraseña debe tener al menos 8 caracteres')
            return
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role='superuser'
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f'[OK] Superusuario creado: {username} ({email})')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
