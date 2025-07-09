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
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencias instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False
    
    # Inicializar base de datos
    print("\n🗄️  Inicializando base de datos...")
    try:
        subprocess.run([sys.executable, '-m', 'flask', 'db', 'upgrade'], 
                      check=True, capture_output=True)
        print("✅ Base de datos inicializada")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error inicializando BD: {e}")
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
    print("2. Listar archivos de despliegue")
    print("3. Crear paquete de despliegue")
    print("4. Salir")
    print()
    
    while True:
        choice = input("Selecciona una opción (1-4): ").strip()
        
        if choice == "1":
            setup_production()
            break
            
        elif choice == "2":
            deploy_files()
            break
            
        elif choice == "3":
            from datetime import datetime
            create_deployment_package()
            break
            
        elif choice == "4":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida. Por favor selecciona 1, 2, 3 o 4.")

if __name__ == "__main__":
    main()
