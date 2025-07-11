#!/usr/bin/env python3
"""
Script para verificar usuarios existentes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User

def check_users():
    app = create_app()
    with app.app_context():
        print("=== Estado actual de los usuarios ===")
        
        users = User.query.all()
        if not users:
            print("No hay usuarios en la base de datos")
            return
        
        for user in users:
            print(f"Usuario: {user.username}")
            print(f"  - ID: {user.id}")
            print(f"  - Email: {user.email}")
            print(f"  - Nombre completo: {user.full_name}")
            print(f"  - Es admin: {user.is_admin}")
            print(f"  - Es activo: {user.is_active}")
            print(f"  - Debe cambiar contraseña: {user.must_change_password}")
            print("---")
            print(f"  - Es admin: {user.is_admin}")
            print(f"  - Está activo: {user.is_active}")
            print(f"  - Debe cambiar contraseña: {user.must_change_password}")
            print()
        
        print("=== Verificando usuarios por defecto ===")
        
        # Verificar usuario admin
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"Admin encontrado - Debe cambiar contraseña: {admin.must_change_password}")
        else:
            print("Usuario admin no encontrado")
        
        # Verificar usuario raquel
        raquel = User.query.filter_by(username='raquel').first()
        if raquel:
            print(f"Raquel encontrado - Debe cambiar contraseña: {raquel.must_change_password}")
            if not raquel.must_change_password:
                print("Actualizando usuario 'raquel' para que deba cambiar contraseña...")
                raquel.must_change_password = True
                db.session.commit()
                print("Usuario 'raquel' actualizado correctamente")
        else:
            print("Usuario 'raquel' no encontrado")

if __name__ == '__main__':
    check_users()
