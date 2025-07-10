#!/usr/bin/env python3
"""
Script de verificación rápida para el servidor
Verifica que todo esté listo para ejecutar la aplicación
"""

import os
import sys
import subprocess
from pathlib import Path

def quick_check():
    """Verificación rápida del estado del sistema"""
    print("⚡ === Verificación Rápida del Sistema ===")
    print()
    
    issues = []
    warnings = []
    
    # 1. Verificar Python
    try:
        version = sys.version_info
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            warnings.append("Python versión recomendada: 3.8 o superior")
    except Exception as e:
        issues.append(f"Error verificando Python: {e}")
    
    # 2. Verificar archivos esenciales
    essential_files = ['app.py', 'models.py', 'requirements.txt']
    for file in essential_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            issues.append(f"Archivo faltante: {file}")
    
    # 3. Verificar carpetas
    essential_folders = ['templates', 'static', 'instance']
    for folder in essential_folders:
        if os.path.exists(folder):
            print(f"✅ {folder}/")
        else:
            Path(folder).mkdir(parents=True, exist_ok=True)
            print(f"📁 {folder}/ (creada)")
    
    # 4. Verificar .env
    if os.path.exists('.env'):
        print("✅ .env")
    elif os.path.exists('.env.production'):
        print("⚠️  .env.production existe, pero falta .env")
        warnings.append("Ejecuta: copy .env.production .env (Windows) o cp .env.production .env (Linux)")
    else:
        issues.append("Falta archivo .env y .env.production")
    
    # 5. Verificar dependencias
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        issues.append("Flask no instalado")
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy")
    except ImportError:
        issues.append("Flask-SQLAlchemy no instalado")
    
    try:
        import flask_migrate
        print("✅ Flask-Migrate")
    except ImportError:
        warnings.append("Flask-Migrate no instalado (necesario para migraciones)")
    
    # 6. Verificar base de datos
    db_files = ['instance/floristeria.db', 'instance/floristeria_production.db']
    db_found = False
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"✅ {db_file} ({size} bytes)")
            db_found = True
            break
    
    if not db_found:
        warnings.append("Base de datos no encontrada (se creará al ejecutar)")
    
    # 7. Resumen
    print("\n" + "="*50)
    if issues:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n🔧 ACCIONES REQUERIDAS:")
        print("   1. Instalar dependencias: pip install -r requirements.txt")
        print("   2. Configurar .env desde .env.production")
        print("   3. Ejecutar: python deploy.py")
        return False
    
    elif warnings:
        print("⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"   • {warning}")
        print("\n✅ Sistema funcional con advertencias menores")
        print("🚀 Puedes ejecutar: python app.py")
        return True
    
    else:
        print("✅ SISTEMA COMPLETAMENTE LISTO")
        print("🚀 Ejecutar: python app.py")
        return True

def test_import():
    """Prueba importar la aplicación"""
    print("\n🧪 === Prueba de Importación ===")
    
    try:
        # Configurar entorno
        if not os.path.exists('.env') and os.path.exists('.env.production'):
            import shutil
            shutil.copy2('.env.production', '.env')
            print("📋 .env creado desde .env.production")
        
        # Intentar importar
        from app import app
        print("✅ Aplicación importada correctamente")
        
        # Verificar configuración
        print(f"✅ Debug: {app.debug}")
        print(f"✅ Secret Key configurada: {'Sí' if app.secret_key else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importando aplicación: {e}")
        print("\n🔧 Soluciones posibles:")
        print("   1. pip install -r requirements.txt")
        print("   2. Verificar .env")
        print("   3. python deploy.py")
        return False

def main():
    """Función principal"""
    success = quick_check()
    
    if success:
        print("\n¿Deseas probar la importación de la aplicación? (s/n): ", end="")
        if input().lower().startswith('s'):
            test_import()

if __name__ == "__main__":
    main()
