#!/usr/bin/env python3
"""
Script para inicializar la base de datos
========================================

Este script inicializa la base de datos y crea usuarios por defecto.
Se puede usar como alternativa a las migraciones de Flask-Migrate.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, User, MaintenanceMode
from config.settings import Config

def init_database():
    """Inicializar la base de datos y crear tablas"""
    app = create_app()
    
    print("🗄️  === Inicializando Base de Datos ===")
    
    with app.app_context():
        print("🗄️  Creando tablas de la base de datos...")
        
        # Intentar usar migraciones primero
        if os.path.exists('migrations'):
            print("📁 Directorio de migraciones encontrado")
            try:
                from flask_migrate import upgrade
                upgrade()
                print("✅ Migraciones aplicadas correctamente")
            except Exception as e:
                print(f"⚠️  Error aplicando migraciones: {e}")
                print("💡 Creando tablas directamente...")
                db.create_all()
        else:
            # Crear todas las tablas directamente
            db.create_all()
            print("✅ Tablas creadas directamente")
        
        # Crear usuarios por defecto si no existen
        create_default_users()
        
        # Crear registro de modo mantenimiento
        create_maintenance_mode()
        
        print("✅ Base de datos inicializada correctamente")
        return True


def create_default_users():
    """Crear usuarios por defecto si no existen"""
    if User.query.first():
        print("👥 Los usuarios ya existen, saltando creación por defecto")
        return
    
    print("👥 Creando usuarios por defecto...")
    
    # Crear admin
    admin = User(
        username=Config.DEFAULT_ADMIN_USER,
        full_name='Administrador',
        is_admin=True,
        is_super_admin=True,  # El admin por defecto es super admin
        must_change_password=False
    )
    admin.set_password(Config.DEFAULT_ADMIN_PASS)
    admin.set_default_privileges()
    
    # Crear usuario regular
    user = User(
        username=Config.DEFAULT_USER_USER,
        full_name='Raquel',
        is_admin=False,
        must_change_password=True
    )
    user.set_password(Config.DEFAULT_USER_PASS)
    user.set_default_privileges()
    
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()
    
    print(f"✅ Usuario admin creado: {Config.DEFAULT_ADMIN_USER}")
    print(f"✅ Usuario regular creado: {Config.DEFAULT_USER_USER}")


def create_maintenance_mode():
    """Crear registro de modo mantenimiento si no existe"""
    if not MaintenanceMode.query.first():
        print("🔧 Creando registro de modo mantenimiento...")
        maintenance = MaintenanceMode(
            is_active=False,
            message="Mantenimiento programado"
        )
        db.session.add(maintenance)
        db.session.commit()
        print("✅ Registro de modo mantenimiento creado")

def check_database():
    """Verifica el estado de la base de datos"""
    app = create_app()
    
    print("🔍 === Verificando Base de Datos ===")
    
    db_path = 'instance/floristeria.db'
    
    if os.path.exists(db_path):
        print(f"✅ Base de datos encontrada: {db_path}")
        
        # Verificar tamaño
        size = os.path.getsize(db_path)
        print(f"📊 Tamaño: {size} bytes")
        
        if size > 1024:  # Más de 1KB indica que probablemente tiene contenido
            print("✅ La base de datos parece tener contenido")
        else:
            print("⚠️  La base de datos parece estar vacía")
            
    else:
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        # Intentar conectar y verificar tablas
        with app.app_context():
            # Verificar si podemos hacer una consulta simple
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"📋 Tablas encontradas: {', '.join(tables)}")
                
                # Verificar usuarios
                user_count = User.query.count()
                print(f"👥 Usuarios en la base de datos: {user_count}")
                
                return True
            else:
                print("⚠️  No se encontraron tablas en la base de datos")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False


def reset_database():
    """Resetear completamente la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  ATENCIÓN: Esto eliminará TODOS los datos existentes")
        confirm = input("¿Está seguro? Escriba 'CONFIRMAR' para continuar: ")
        
        if confirm != "CONFIRMAR":
            print("❌ Operación cancelada")
            return
        
        print("🗑️  Eliminando todas las tablas...")
        db.drop_all()
        
        print("🗄️  Recreando tablas...")
        db.create_all()
        
        # Crear usuarios por defecto
        create_default_users()
        create_maintenance_mode()
        
        print("✅ Base de datos reseteada completamente")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestión de base de datos')
    parser.add_argument('--init', action='store_true', 
                       help='Inicializar base de datos')
    parser.add_argument('--check', action='store_true',
                       help='Verificar estado de base de datos')
    parser.add_argument('--reset', action='store_true', 
                       help='Resetear completamente la base de datos')
    
    args = parser.parse_args()
    
    if args.init:
        init_database()
    elif args.check:
        check_database()
    elif args.reset:
        reset_database()
    else:
        # Menú interactivo
        print("🗄️  === Gestión de Base de Datos ===")
        print()
        print("1. Inicializar base de datos")
        print("2. Verificar estado de base de datos")
        print("3. Resetear base de datos (¡PELIGROSO!)")
        print("4. Salir")
        print()
        
        while True:
            choice = input("Selecciona una opción (1-4): ").strip()
            
            if choice == "1":
                init_database()
                break
                
            elif choice == "2":
                check_database()
                break
                
            elif choice == "3":
                reset_database()
                break
                
            elif choice == "4":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Por favor selecciona 1, 2, 3 o 4.")

if __name__ == "__main__":
    main()
