#!/usr/bin/env python3
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def init_users():
    with app.app_context():
        # Crear usuario admin si no existe
        admin_exists = User.query.filter_by(username='admin').first()
        if not admin_exists:
            admin = User(
                username='admin',
                email='admin@floristeria.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin user created')
        else:
            print('Admin user already exists')
        
        # Crear usuario regular si no existe
        user_exists = User.query.filter_by(username='usuario').first()
        if not user_exists:
            user = User(
                username='usuario',
                email='usuario@floristeria.com',
                password_hash=generate_password_hash('usuario123'),
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
            print('Regular user created')
        else:
            print('Regular user already exists')
        
        print(f'Total users: {User.query.count()}')

if __name__ == '__main__':
    init_users()
