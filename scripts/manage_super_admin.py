#!/usr/bin/env python3
"""
Script para gestión de super administradores
============================================

Este script permite crear, listar y gestionar super administradores
en el sistema de Floristería Raquel.

Uso:
    python scripts/manage_super_admin.py add <username>
    python scripts/manage_super_admin.py remove <username>
    python scripts/manage_super_admin.py list
    python scripts/manage_super_admin.py create-emergency
    python scripts/manage_super_admin.py create <username> [password]
"""

import sys
import os
from getpass import getpass

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, User
from config.settings import config

def get_app():
    """Obtener instancia configurada de la aplicación"""
    # Usar configuración de desarrollo por defecto
    config_name = os.environ.get('FLASK_CONFIG') or 'development'
    app = create_app(config[config_name])
    return app


def create_new_super_admin(username, password=None, full_name=None, email=None):
    """Crear un nuevo usuario con permisos de super administrador"""
    app = get_app()
    
    with app.app_context():
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ El usuario '{username}' ya existe")
            return False
        
        # Solicitar contraseña si no se proporciona
        if not password:
            password = getpass(f"🔑 Contraseña para '{username}': ")
            if not password:
                print("❌ La contraseña no puede estar vacía")
                return False
        
        # Solicitar nombre completo si no se proporciona
        if not full_name:
            full_name = input(f"👤 Nombre completo para '{username}' (opcional): ").strip()
            if not full_name:
                full_name = f"Super Admin {username}"
        
        # Solicitar email si no se proporciona
        if not email:
            email = input(f"📧 Email para '{username}' (opcional): ").strip()
            if not email:
                email = None
        
        # Crear el nuevo usuario
        new_user = User(
            username=username,
            full_name=full_name,
            email=email,
            is_admin=True,
            is_super_admin=True,
            is_active=True,
            must_change_password=False
        )
        new_user.set_password(password)
        new_user.set_default_privileges()  # Establecer todos los privilegios
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"✅ Super administrador '{username}' creado exitosamente")
            print(f"👤 Nombre: {full_name}")
            if email:
                print(f"📧 Email: {email}")
            print(f"🔑 Contraseña: ********")
            return True
        except Exception as e:
            print(f"❌ Error al crear el usuario: {str(e)}")
            db.session.rollback()
            return False


def make_super_admin(username):
    """Convertir un usuario existente en super administrador"""
    app = get_app()
    
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
        user.set_default_privileges()  # Asegurar que tenga todos los privilegios
        
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
    app = get_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ Usuario '{username}' no encontrado")
            return False
            
        if not user.is_super_admin:
            print(f"ℹ️ El usuario '{username}' no es super administrador")
            return True
            
        # Confirmar acción
        confirm = input(f"⚠️ ¿Está seguro de remover permisos de super admin de '{username}'? (s/N): ")
        if confirm.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada")
            return False
        
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
    app = get_app()
    
    with app.app_context():
        super_admins = User.query.filter_by(is_super_admin=True).all()
        
        if not super_admins:
            print("ℹ️ No hay super administradores configurados")
            return
            
        print("👑 Super Administradores:")
        print("-" * 60)
        for user in super_admins:
            status = "🟢 Activo" if user.is_active else "🔴 Inactivo"
            admin_status = "👨‍💼 Admin" if user.is_admin else ""
            created_date = user.created_at.strftime("%Y-%m-%d") if hasattr(user, 'created_at') and user.created_at else "N/A"
            
            print(f"  🔹 {user.username}")
            print(f"     Nombre: {user.full_name or 'Sin nombre'}")
            print(f"     Email: {user.email or 'Sin email'}")
            print(f"     Estado: {status} {admin_status}")
            print(f"     Creado: {created_date}")
            print()


def list_all_users():
    """Listar todos los usuarios del sistema"""
    app = get_app()
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("ℹ️ No hay usuarios en el sistema")
            return
            
        print("👥 Todos los usuarios:")
        print("-" * 80)
        for user in users:
            status = "🟢 Activo" if user.is_active else "🔴 Inactivo"
            role = ""
            if user.is_super_admin:
                role = "👑 Super Admin"
            elif user.is_admin:
                role = "👨‍💼 Admin"
            else:
                role = "👤 Usuario"
            
            print(f"  🔹 {user.username:15} | {role:15} | {status:10} | {user.full_name or 'Sin nombre'}")
        print()

def create_emergency_super_admin():
    """Crear un super administrador de emergencia"""
    app = get_app()
    
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
                existing.set_default_privileges()
                db.session.commit()
                print(f"✅ Permisos de super admin actualizados para '{emergency_username}'")
            else:
                print("✅ El usuario de emergencia ya tiene permisos de super admin")
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
        emergency_user.set_default_privileges()
        
        try:
            db.session.add(emergency_user)
            db.session.commit()
            print("=" * 60)
            print("✅ Usuario de emergencia creado exitosamente")
            print("=" * 60)
            print(f"� Usuario: {emergency_username}")
            print(f"🔑 Contraseña: {emergency_password}")
            print(f"📧 Email: emergency@floristeria.local")
            print("=" * 60)
            print("⚠️ IMPORTANTE:")
            print("  - Este usuario está diseñado solo para emergencias")
            print("  - Cambie la contraseña después del primer uso")
            print("  - No aparecerá en la gestión normal de usuarios")
            print("=" * 60)
        except Exception as e:
            print(f"❌ Error al crear usuario de emergencia: {str(e)}")
            db.session.rollback()

def show_help():
    """Mostrar ayuda del script"""
    print("=" * 70)
    print("🛠️  SCRIPT DE GESTIÓN DE SUPER ADMINISTRADORES")
    print("=" * 70)
    print("Este script permite gestionar super administradores en Floristería Raquel")
    print()
    print("📋 Comandos disponibles:")
    print()
    print("  🆕 CREAR NUEVO SUPER ADMIN:")
    print("     python scripts/manage_super_admin.py create <username> [password]")
    print("     - Crea un nuevo usuario con permisos de super administrador")
    print("     - Si no se proporciona contraseña, se solicitará")
    print()
    print("  ⬆️  PROMOVER USUARIO EXISTENTE:")
    print("     python scripts/manage_super_admin.py add <username>")
    print("     - Convierte un usuario existente en super administrador")
    print()
    print("  ⬇️  REMOVER PERMISOS:")
    print("     python scripts/manage_super_admin.py remove <username>")
    print("     - Remueve permisos de super administrador (requiere confirmación)")
    print()
    print("  📋 LISTAR:")
    print("     python scripts/manage_super_admin.py list")
    print("     python scripts/manage_super_admin.py list-all")
    print("     - Lista super administradores o todos los usuarios")
    print()
    print("  🚨 EMERGENCIA:")
    print("     python scripts/manage_super_admin.py create-emergency")
    print("     - Crea usuario de emergencia: superadmin/emergency2025!")
    print()
    print("  ❓ AYUDA:")
    print("     python scripts/manage_super_admin.py help")
    print("     - Muestra esta ayuda")
    print()
    print("=" * 70)
    print("💡 Ejemplos de uso:")
    print("   python scripts/manage_super_admin.py create admin_raquel")
    print("   python scripts/manage_super_admin.py add raquel")
    print("   python scripts/manage_super_admin.py list")
    print("=" * 70)


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action in ["help", "-h", "--help"]:
        show_help()
        
    elif action == "create":
        if len(sys.argv) < 3:
            print("❌ Especifica el nombre de usuario")
            print("Uso: python scripts/manage_super_admin.py create <username> [password]")
            sys.exit(1)
        username = sys.argv[2]
        password = sys.argv[3] if len(sys.argv) > 3 else None
        create_new_super_admin(username, password)
        
    elif action == "add":
        if len(sys.argv) != 3:
            print("❌ Especifica el nombre de usuario")
            print("Uso: python scripts/manage_super_admin.py add <username>")
            sys.exit(1)
        username = sys.argv[2]
        make_super_admin(username)
        
    elif action == "remove":
        if len(sys.argv) != 3:
            print("❌ Especifica el nombre de usuario")
            print("Uso: python scripts/manage_super_admin.py remove <username>")
            sys.exit(1)
        username = sys.argv[2]
        remove_super_admin(username)
        
    elif action == "list":
        list_super_admins()
        
    elif action == "list-all":
        list_all_users()
        
    elif action == "create-emergency":
        create_emergency_super_admin()
        
    else:
        print(f"❌ Acción '{action}' no reconocida")
        print("Usa 'python scripts/manage_super_admin.py help' para ver comandos disponibles")
        sys.exit(1)

if __name__ == "__main__":
    main()
