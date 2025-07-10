#!/usr/bin/env python3
"""
Script de inicialización de base de datos
Alternativa cuando flask db no funciona
"""

import os
import sys
from pathlib import Path

def init_database():
    """Inicializa la base de datos"""
    print("🗄️  === Inicializando Base de Datos ===")
    
    # Asegurar que tenemos la carpeta instance
    Path('instance').mkdir(exist_ok=True)
    
    try:
        # Configurar Flask app
        os.environ['FLASK_APP'] = 'app.py'
        
        # Importar la aplicación y base de datos
        from app import app, db
        
        print("📱 Aplicación Flask importada correctamente")
        
        # Verificar si hay migraciones
        if os.path.exists('migrations'):
            print("📁 Directorio de migraciones encontrado")
            
            try:
                from flask_migrate import upgrade
                with app.app_context():
                    upgrade()
                print("✅ Migraciones aplicadas correctamente")
                return True
                
            except Exception as e:
                print(f"⚠️  Error aplicando migraciones: {e}")
                print("💡 Intentando crear tablas directamente...")
        
        # Método alternativo: crear todas las tablas
        with app.app_context():
            db.create_all()
            print("✅ Tablas de base de datos creadas")
            
        return True
        
    except ImportError as e:
        print(f"❌ Error importando la aplicación: {e}")
        print("🔧 Verifica que todas las dependencias estén instaladas:")
        print("   pip install Flask Flask-SQLAlchemy Flask-Migrate")
        return False
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

def check_database():
    """Verifica el estado de la base de datos"""
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
        from app import app, db
        
        with app.app_context():
            # Verificar si podemos hacer una consulta simple
            result = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in result]
            
            if tables:
                print(f"📋 Tablas encontradas: {', '.join(tables)}")
                return True
            else:
                print("⚠️  No se encontraron tablas en la base de datos")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def main():
    """Función principal"""
    print("🗄️  === Gestión de Base de Datos ===")
    print()
    print("1. Inicializar base de datos")
    print("2. Verificar estado de base de datos")
    print("3. Salir")
    print()
    
    while True:
        choice = input("Selecciona una opción (1-3): ").strip()
        
        if choice == "1":
            init_database()
            break
            
        elif choice == "2":
            check_database()
            break
            
        elif choice == "3":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida. Por favor selecciona 1, 2 o 3.")

if __name__ == "__main__":
    main()
