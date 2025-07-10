#!/usr/bin/env python3
"""
Script para verificar y actualizar usuarios existentes con el campo must_change_password
"""

from models import db, User
from app import app

def check_users():
    with app.app_context():
        print("=== Estado actual de los usuarios ===")
        
        users = User.query.all()
        if not users:
            print("No hay usuarios en la base de datos")
            return
        
        for user in users:
            print(f"Usuario: {user.username}")
            print(f"  - Nombre completo: {user.full_name}")
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
