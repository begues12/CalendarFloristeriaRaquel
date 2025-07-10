#!/usr/bin/env python3
"""
Script de despliegue para servidor
Automatiza la configuración inicial y sincronización
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def diagnose_environment():
    """Diagnostica el entorno del servidor"""
    print("🔍 === Diagnóstico del Entorno ===")
    print()
    
    # Verificar Python
    try:
        python_version = subprocess.run([sys.executable, '--version'], 
                                      capture_output=True, text=True, check=True)
        print(f"✅ Python: {python_version.stdout.strip()}")
    except Exception as e:
        print(f"❌ Python no encontrado: {e}")
        return False
    
    # Verificar pip
    try:
        pip_version = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                   capture_output=True, text=True, check=True)
        print(f"✅ Pip: {pip_version.stdout.strip()}")
    except Exception as e:
        print(f"❌ Pip no encontrado: {e}")
        return False
    
    # Verificar archivos necesarios
    required_files = ['app.py', 'models.py', 'requirements.txt']
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ Archivo: {file}")
        else:
            print(f"❌ Archivo faltante: {file}")
            missing_files.append(file)
    
    # Verificar Flask si está instalado
    try:
        flask_check = subprocess.run([sys.executable, '-c', 'import flask; print(flask.__version__)'], 
                                   capture_output=True, text=True, check=True)
        print(f"✅ Flask instalado: {flask_check.stdout.strip()}")
        
        # Verificar comando flask
        try:
            flask_cmd = subprocess.run([sys.executable, '-m', 'flask', '--version'], 
                                     capture_output=True, text=True, check=True)
            print(f"✅ Comando flask: {flask_cmd.stdout.strip()}")
        except Exception:
            print("⚠️  Comando 'flask' no disponible (pero módulo sí)")
            
    except Exception:
        print("❌ Flask no instalado")
    
    # Verificar base de datos
    if os.path.exists('instance/floristeria.db'):
        print("✅ Base de datos encontrada")
    else:
        print("⚠️  Base de datos no encontrada (se creará)")
    
    print("\n📋 Resumen:")
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Todos los archivos necesarios están presentes")
        return True

def setup_production():
    """Configura el entorno de producción"""
    print("🚀 === Configuración de Producción - Floristería Raquel ===")
    print()
    
    # Verificar si existe .env.production
    if not os.path.exists('.env.production'):
        print("❌ No se encontró .env.production")
        print("   Asegúrate de tener el archivo .env.production configurado")
        return False
    
    # Crear .env desde .env.production
    print("📝 Configurando variables de entorno...")
    shutil.copy2('.env.production', '.env')
    print("✅ Archivo .env configurado para producción")
    
    # Crear carpetas necesarias
    folders = ['static/uploads', 'static/documents', 'backups', 'instance']
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"📁 Carpeta creada: {folder}")
    
    # Instalar dependencias
    print("\n📦 Instalando dependencias...")
    try:
        # Verificar si pip funciona
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      check=True, capture_output=True)
        
        # Actualizar pip primero
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Instalar dependencias
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencias instaladas")
        
        # Verificar instalación de Flask
        try:
            subprocess.run([sys.executable, '-c', 'import flask; print("Flask instalado correctamente")'], 
                          check=True, capture_output=True)
            print("✅ Flask verificado")
        except subprocess.CalledProcessError:
            print("⚠️  Flask no se pudo verificar")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        print("🔧 Solución manual:")
        print("   1. Verifica que Python esté instalado: python --version")
        print("   2. Verifica que pip esté disponible: pip --version")
        print("   3. Instala manualmente: pip install -r requirements.txt")
        return False
    
    # Inicializar base de datos
    print("\n🗄️  Inicializando base de datos...")
    try:
        # Intentar con flask directamente
        result = subprocess.run([sys.executable, '-m', 'flask', 'db', 'upgrade'], 
                      check=True, capture_output=True, text=True)
        print("✅ Base de datos inicializada")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error con flask db upgrade: {e}")
        print("💡 Intentando método alternativo...")
        
        # Método alternativo: usar la aplicación directamente
        try:
            print("💡 Usando script de inicialización alternativo...")
            subprocess.run([sys.executable, 'init_database.py'], 
                          input='1\n', text=True, check=True, capture_output=True)
            print("✅ Base de datos inicializada (método alternativo)")
            
        except Exception as e2:
            print(f"❌ Error inicializando BD (ambos métodos): {e2}")
            print("🔧 Solución manual requerida:")
            print("   1. Instala Flask: pip install Flask Flask-Migrate")
            print("   2. Ejecuta: flask db upgrade")
            print("   3. O ejecuta: python init_database.py")
            print("   4. O ejecuta: python -c \"from app import app,db; db.create_all()\"")
            return False
    
    # Crear usuarios iniciales
    print("\n👥 Creando usuarios iniciales...")
    try:
        subprocess.run([sys.executable, 'init_users.py'], 
                      check=True, capture_output=True)
        print("✅ Usuarios iniciales creados")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando usuarios: {e}")
        return False
    
    print("\n🎉 ¡Configuración de producción completada!")
    print("\n📋 Próximos pasos:")
    print("   1. Revisa el archivo .env y cambia SECRET_KEY y contraseñas")
    print("   2. Para sincronizar datos: python sync_data.py")
    print("   3. Para ejecutar: python app.py")
    
    return True

def deploy_files():
    """Lista archivos necesarios para el despliegue"""
    print("📦 === Archivos necesarios para despliegue ===")
    print()
    
    required_files = [
        'app.py',
        'models.py',
        'requirements.txt',
        '.env.production',
        'sync_data.py',
        'init_users.py',
        'deploy.py'
    ]
    
    required_folders = [
        'templates/',
        'static/css/',
        'migrations/'
    ]
    
    print("📄 Archivos principales:")
    for file in required_files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"   {exists} {file}")
    
    print("\n📁 Carpetas principales:")
    for folder in required_folders:
        exists = "✅" if os.path.exists(folder) else "❌"
        print(f"   {exists} {folder}")
    
    print("\n💡 Instrucciones de despliegue:")
    print("   1. Sube todos los archivos ✅ al servidor")
    print("   2. En el servidor ejecuta: python deploy.py")
    print("   3. Selecciona 'Configurar producción'")
    print("   4. Modifica .env con tus configuraciones seguras")
    print("   5. Para sincronizar datos usa sync_data.py")

def create_deployment_package():
    """Crea un paquete con todos los archivos necesarios"""
    print("📦 Creando paquete de despliegue...")
    
    import zipfile
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"floristeria_deploy_{timestamp}.zip"
    
    files_to_include = [
        'app.py',
        'models.py', 
        'requirements.txt',
        '.env.production',
        'sync_data.py',
        'init_users.py',
        'deploy.py',
        'README.md'
    ]
    
    folders_to_include = [
        'templates',
        'static',
        'migrations'
    ]
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Agregar archivos
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file)
                print(f"   ➕ {file}")
        
        # Agregar carpetas
        for folder in folders_to_include:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
                        print(f"   ➕ {file_path}")
    
    print(f"\n✅ Paquete creado: {package_name}")
    print("\n📋 Para desplegar:")
    print(f"   1. Sube {package_name} al servidor")
    print("   2. Descomprime el archivo")
    print("   3. Ejecuta: python deploy.py")
    
    return package_name

def main():
    """Función principal"""
    print("🌸 === Deploy Floristería Raquel ===")
    print()
    print("Opciones disponibles:")
    print("1. Configurar producción (ejecutar en servidor)")
    print("2. Diagnosticar entorno del servidor")
    print("3. Listar archivos de despliegue")
    print("4. Crear paquete de despliegue")
    print("5. Salir")
    print()
    
    while True:
        choice = input("Selecciona una opción (1-5): ").strip()
        
        if choice == "1":
            setup_production()
            break
            
        elif choice == "2":
            diagnose_environment()
            break
            
        elif choice == "3":
            deploy_files()
            break
            
        elif choice == "4":
            from datetime import datetime
            create_deployment_package()
            break
            
        elif choice == "5":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida. Por favor selecciona 1, 2, 3, 4 o 5.")

if __name__ == "__main__":
    main()
