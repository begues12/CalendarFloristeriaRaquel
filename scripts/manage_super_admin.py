#!/usr/bin/env python3
"""
Script para asignar permisos de super administrador a un usuario
"""

import sys
from flask import Flask
from models import db, User

def create_app():
    """Crear instancia de la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///floristeria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'temp-key-for-script'
    
    db.init_app(app)
    return app

def make_super_admin(username):
    """Convertir un usuario en super administrador"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ Usuario '{username}' no encontrado")
            return False
            
        if user.is_super_admin:
            print(f"✅ El usuario '{username}' ya es super administrador")
            return True
            
        # Asignar permisos de super admin
        user.is_super_admin = True
        user.is_admin = True  # Un super admin también debe ser admin
        
        try:
            db.session.commit()
            print(f"✅ Usuario '{username}' convertido en super administrador exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error al actualizar el usuario: {str(e)}")
            db.session.rollback()
            return False

def remove_super_admin(username):
    """Remover permisos de super administrador de un usuario"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ Usuario '{username}' no encontrado")
            return False
            
        if not user.is_super_admin:
            print(f"ℹ️ El usuario '{username}' no es super administrador")
            return True
            
        # Remover permisos de super admin
        user.is_super_admin = False
        
        try:
            db.session.commit()
            print(f"✅ Permisos de super administrador removidos del usuario '{username}'")
            return True
        except Exception as e:
            print(f"❌ Error al actualizar el usuario: {str(e)}")
            db.session.rollback()
            return False

def list_super_admins():
    """Listar todos los super administradores"""
    app = create_app()
    
    with app.app_context():
        super_admins = User.query.filter_by(is_super_admin=True).all()
        
        if not super_admins:
            print("ℹ️ No hay super administradores configurados")
            return
            
        print("👑 Super Administradores:")
        for user in super_admins:
            status = "Activo" if user.is_active else "Inactivo"
            print(f"  - {user.username} ({user.full_name or 'Sin nombre'}) - {status}")

def create_emergency_super_admin():
    """Crear un super administrador de emergencia"""
    app = create_app()
    
    with app.app_context():
        emergency_username = "superadmin"
        emergency_password = "emergency2025!"
        
        # Verificar si ya existe
        existing = User.query.filter_by(username=emergency_username).first()
        if existing:
            print(f"ℹ️ El usuario de emergencia '{emergency_username}' ya existe")
            if not existing.is_super_admin:
                existing.is_super_admin = True
                existing.is_admin = True
                db.session.commit()
                print(f"✅ Permisos de super admin actualizados para '{emergency_username}'")
            return
        
        # Crear nuevo usuario de emergencia
        emergency_user = User(
            username=emergency_username,
            full_name="Super Administrador de Emergencia",
            email="emergency@floristeria.local",
            is_admin=True,
            is_super_admin=True,
            is_active=True,
            must_change_password=False
        )
        emergency_user.set_password(emergency_password)
        
        try:
            db.session.add(emergency_user)
            db.session.commit()
            print(f"✅ Usuario de emergencia '{emergency_username}' creado exitosamente")
            print(f"🔑 Credenciales: {emergency_username} / {emergency_password}")
            print("⚠️ IMPORTANTE: Este usuario está diseñado solo para emergencias")
            print("   No aparecerá en la gestión normal de usuarios")
        except Exception as e:
            print(f"❌ Error al crear usuario de emergencia: {str(e)}")
            db.session.rollback()

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python manage_super_admin.py add <username>")
        print("  python manage_super_admin.py remove <username>")
        print("  python manage_super_admin.py list")
        print("  python manage_super_admin.py create-emergency")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "add":
        if len(sys.argv) != 3:
            print("❌ Especifica el nombre de usuario")
            print("Uso: python manage_super_admin.py add <username>")
            sys.exit(1)
        username = sys.argv[2]
        make_super_admin(username)
        
    elif action == "remove":
        if len(sys.argv) != 3:
            print("❌ Especifica el nombre de usuario")
            print("Uso: python manage_super_admin.py remove <username>")
            sys.exit(1)
        username = sys.argv[2]
        remove_super_admin(username)
        
    elif action == "list":
        list_super_admins()
        
    elif action == "create-emergency":
        create_emergency_super_admin()
        
    else:
        print(f"❌ Acción '{action}' no reconocida")
        print("Acciones disponibles: add, remove, list, create-emergency")
        sys.exit(1)

if __name__ == "__main__":
    main()
