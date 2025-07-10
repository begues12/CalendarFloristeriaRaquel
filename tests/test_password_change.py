#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de cambio de contraseña obligatorio
"""

from models import db, User
from app import app

def test_password_change_functionality():
    with app.app_context():
        # Buscar el usuario "raquel"
        user = User.query.filter_by(username='raquel').first()
        
        if user:
            print(f"Usuario encontrado: {user.username}")
            print(f"Debe cambiar contraseña: {user.must_change_password}")
            
            # Si no debe cambiar contraseña, establecer el flag para testing
            if not user.must_change_password:
                print("Estableciendo flag must_change_password=True para testing...")
                user.must_change_password = True
                db.session.commit()
                print("Flag establecido. El usuario ahora debe cambiar su contraseña.")
            else:
                print("El usuario ya tiene el flag de cambio obligatorio activado.")
        else:
            print("Usuario 'raquel' no encontrado. Creando usuario de prueba...")
            
            # Crear usuario de prueba
            test_user = User(
                username='test_user',
                full_name='Usuario de Prueba',
                is_admin=False,
                must_change_password=True
            )
            test_user.set_password('test123')
            
            db.session.add(test_user)
            db.session.commit()
            
            print("Usuario de prueba creado:")
            print(f"- Username: {test_user.username}")
            print(f"- Debe cambiar contraseña: {test_user.must_change_password}")

if __name__ == '__main__':
    test_password_change_functionality()
