#!/usr/bin/env python3
"""
Script de inicio simplificado para el servidor
Maneja errores comunes automáticamente
"""

import os
import sys
import subprocess
from pathlib import Path

def ensure_environment():
    """Asegura que el entorno esté listo"""
    print("🔧 Preparando entorno...")
    
    # Crear carpetas necesarias
    folders = ['static/uploads', 'static/documents', 'instance', 'backups']
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
    
    # Configurar .env si no existe
    if not os.path.exists('.env') and os.path.exists('.env.production'):
        import shutil
        shutil.copy2('.env.production', '.env')
        print("📋 .env configurado desde .env.production")
    
    return True

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("📦 Verificando dependencias...")
    
    required_modules = ['flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Dependencias faltantes: {', '.join(missing)}")
        print("🔧 Instalando dependencias...")
        
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                          check=True, capture_output=True)
            print("✅ Dependencias instaladas")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando dependencias: {e}")
            return False
    
    return True

def init_database_safe():
    """Inicializa la base de datos de forma segura"""
    print("🗄️  Verificando base de datos...")
    
    db_files = ['instance/floristeria.db', 'instance/floristeria_production.db']
    db_exists = any(os.path.exists(db) for db in db_files)
    
    if db_exists:
        print("✅ Base de datos encontrada")
        return True
    
    print("🔨 Inicializando base de datos...")
    
    try:
        # Configurar entorno Flask
        os.environ['FLASK_APP'] = 'app.py'
        
        # Método 1: Flask migrate
        try:
            subprocess.run([sys.executable, '-m', 'flask', 'db', 'upgrade'], 
                          check=True, capture_output=True)
            print("✅ Base de datos inicializada con migraciones")
            return True
        except subprocess.CalledProcessError:
            pass
        
        # Método 2: Script personalizado
        if os.path.exists('init_database.py'):
            subprocess.run([sys.executable, 'init_database.py'], 
                          input='1\n', text=True, check=True, capture_output=True)
            print("✅ Base de datos inicializada con script personalizado")
            return True
        
        # Método 3: Crear directamente
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Base de datos inicializada directamente")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

def start_application():
    """Inicia la aplicación"""
    print("🚀 Iniciando aplicación...")
    
    try:
        # Verificar que la aplicación se puede importar
        from app import app
        
        # Obtener configuración
        host = os.getenv('FLASK_HOST', '127.0.0.1')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        
        print(f"🌐 Servidor iniciando en http://{host}:{port}")
        print("🛑 Presiona Ctrl+C para detener")
        
        # Ejecutar aplicación
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
        print("\n🔧 Soluciones:")
        print("   1. Verifica que todas las dependencias estén instaladas")
        print("   2. Ejecuta: python check_server.py")
        print("   3. Ejecuta: python deploy.py")
        return False
    
    return True

def main():
    """Función principal"""
    print("🌸 === Floristería Raquel - Inicio Rápido ===")
    print()
    
    # Paso 1: Preparar entorno
    if not ensure_environment():
        return False
    
    # Paso 2: Verificar dependencias
    if not check_dependencies():
        return False
    
    # Paso 3: Inicializar base de datos
    if not init_database_safe():
        return False
    
    # Paso 4: Iniciar aplicación
    start_application()

if __name__ == "__main__":
    main()
