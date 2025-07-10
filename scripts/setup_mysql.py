#!/usr/bin/env python
"""
Script para configurar MySQL y migrar desde SQLite
=====================================================

Este script:
1. Instala las dependencias necesarias para MySQL
2. Crea las bases de datos MySQL necesarias
3. Migra los datos desde SQLite (opcional)
4. Ejecuta las migraciones de Flask-Migrate
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def install_mysql_dependencies():
    """Instalar dependencias de MySQL"""
    print("📦 Instalando dependencias de MySQL...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'PyMySQL==1.1.1', 
            'cryptography==42.0.5'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente")
            return True
        else:
            print(f"❌ Error instalando dependencias: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_mysql_connection():
    """Verificar conexión a MySQL"""
    print("🔌 Verificando conexión a MySQL...")
    
    try:
        import pymysql
        
        # Configuración por defecto
        config = {
            'host': input("Host MySQL (localhost): ").strip() or 'localhost',
            'port': int(input("Puerto MySQL (3306): ").strip() or '3306'),
            'user': input("Usuario MySQL (root): ").strip() or 'root',
            'password': input("Contraseña MySQL: ").strip()
        }
        
        # Probar conexión
        connection = pymysql.connect(**config)
        connection.close()
        
        print("✅ Conexión MySQL exitosa")
        return config
        
    except ImportError:
        print("❌ PyMySQL no está instalado")
        return None
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def create_databases(mysql_config):
    """Crear bases de datos necesarias"""
    print("🗄️  Creando bases de datos...")
    
    databases = [
        'floristeria',
        'floristeria_dev', 
        'floristeria_production',
        'floristeria_test'
    ]
    
    try:
        import pymysql
        
        connection = pymysql.connect(**mysql_config)
        cursor = connection.cursor()
        
        for db_name in databases:
            try:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ Base de datos '{db_name}' creada/verificada")
            except Exception as e:
                print(f"⚠️  Error creando '{db_name}': {e}")
        
        connection.commit()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando bases de datos: {e}")
        return False

def create_env_file(mysql_config):
    """Crear archivo .env con configuración de MySQL"""
    print("📝 Creando archivo .env...")
    
    env_content = f"""# Configuración de Base de Datos MySQL
DATABASE_URL=mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/floristeria
DEV_DATABASE_URL=mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/floristeria_dev
TEST_DATABASE_URL=mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/floristeria_test

# Configuración de la aplicación
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=tu_clave_secreta_muy_segura_cambiar_en_produccion

# Configuración de archivos
UPLOAD_FOLDER=app/static/uploads
DOCUMENTS_FOLDER=app/static/documents
MAX_FILE_SIZE=16777216

# Usuarios por defecto
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASS=admin123
DEFAULT_USER_USER=raquel
DEFAULT_USER_PASS=floreria2025
"""
    
    try:
        with open(root_dir / '.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Archivo .env creado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return False

def migrate_from_sqlite():
    """Migrar datos desde SQLite a MySQL (opcional)"""
    print("\n🔄 ¿Deseas migrar datos desde SQLite existente?")
    migrate = input("Migrar datos (s/N): ").lower().strip() == 's'
    
    if not migrate:
        print("⏭️  Omitiendo migración de datos")
        return True
    
    sqlite_files = [
        'instance/floristeria.db',
        'instance/floristeria_dev.db',
        'instance/floristeria_production.db'
    ]
    
    existing_files = [f for f in sqlite_files if os.path.exists(root_dir / f)]
    
    if not existing_files:
        print("ℹ️  No se encontraron archivos SQLite para migrar")
        return True
    
    print(f"📁 Archivos SQLite encontrados: {existing_files}")
    
    # Aquí se podría implementar una migración de datos más compleja
    # Por ahora, recomendamos exportar/importar manualmente
    print("ℹ️  Para migrar datos, usa el script de exportación y luego importa a MySQL")
    print("ℹ️  Ejecuta: python scripts/export_data.py antes de cambiar a MySQL")
    
    return True

def run_flask_migrations():
    """Ejecutar migraciones de Flask-Migrate"""
    print("🔧 Ejecutando migraciones de Flask-Migrate...")
    
    try:
        os.chdir(root_dir)
        
        # Inicializar migraciones si no existen
        if not os.path.exists('migrations'):
            print("📝 Inicializando Flask-Migrate...")
            result = subprocess.run([sys.executable, '-m', 'flask', 'db', 'init'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Error inicializando migraciones: {result.stderr}")
                return False
        
        # Crear migración inicial
        print("📝 Creando migración inicial...")
        result = subprocess.run([sys.executable, '-m', 'flask', 'db', 'migrate', '-m', 'Initial migration to MySQL'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️  Aviso en migración: {result.stderr}")
        
        # Aplicar migraciones
        print("🚀 Aplicando migraciones...")
        result = subprocess.run([sys.executable, '-m', 'flask', 'db', 'upgrade'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migraciones aplicadas correctamente")
            return True
        else:
            print(f"❌ Error aplicando migraciones: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def initialize_data():
    """Inicializar datos básicos"""
    print("👤 Inicializando usuarios y datos básicos...")
    
    try:
        # Ejecutar script de inicialización
        result = subprocess.run([sys.executable, 'scripts/init_database.py'], 
                              capture_output=True, text=True, cwd=root_dir)
        
        if result.returncode == 0:
            print("✅ Datos iniciales creados correctamente")
            return True
        else:
            print(f"❌ Error inicializando datos: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN DE MYSQL PARA FLORISTERÍA RAQUEL")
    print("=" * 50)
    
    # 1. Instalar dependencias
    if not install_mysql_dependencies():
        return
    
    # 2. Verificar conexión MySQL
    mysql_config = check_mysql_connection()
    if not mysql_config:
        return
    
    # 3. Crear bases de datos
    if not create_databases(mysql_config):
        return
    
    # 4. Crear archivo .env
    if not create_env_file(mysql_config):
        return
    
    # 5. Migrar datos (opcional)
    if not migrate_from_sqlite():
        return
    
    # 6. Ejecutar migraciones
    if not run_flask_migrations():
        return
    
    # 7. Inicializar datos
    if not initialize_data():
        return
    
    print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("=" * 50)
    print("✅ MySQL configurado correctamente")
    print("✅ Bases de datos creadas")
    print("✅ Archivo .env configurado")
    print("✅ Migraciones aplicadas")
    print("✅ Datos iniciales creados")
    print("\n🚀 Puedes ejecutar la aplicación con: python run.py")
    print("📚 Documentación: docs/DEPLOY.md")

if __name__ == "__main__":
    main()
