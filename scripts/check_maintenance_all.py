#!/usr/bin/env python
"""
Script para verificar el estado de mantenimiento en todas las bases de datos
"""

import sqlite3
import os

dbs = [
    'instance/floristeria.db',
    'instance/floristeria_dev.db', 
    'instance/floristeria_production.db'
]

print("🔍 Verificando estado de mantenimiento en todas las bases de datos:")
print("=" * 60)

for db_path in dbs:
    try:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if maintenance_mode table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='maintenance_mode'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.execute("SELECT is_active, message, started_by FROM maintenance_mode LIMIT 1")
                result = cursor.fetchone()
                if result:
                    is_active, message, started_by = result
                    status = "🟢 ACTIVO" if is_active else "🔴 INACTIVO"
                    print(f"{db_path}: {status}")
                    if is_active:
                        print(f"  Mensaje: {message}")
                        print(f"  Iniciado por: {started_by}")
                else:
                    print(f"{db_path}: ⚪ SIN DATOS")
            else:
                print(f"{db_path}: ❌ SIN TABLA maintenance_mode")
            
            conn.close()
        else:
            print(f"{db_path}: ❌ NO EXISTE")
    except Exception as e:
        print(f"{db_path}: ❌ ERROR - {e}")

print("\n" + "=" * 60)

# Test con Flask app
print("🧪 Verificando con Flask app...")
try:
    import sys
    import os
    
    # Añadir el directorio raíz al path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from app import create_app
    from app.models.user import MaintenanceMode
    
    app = create_app()
    with app.app_context():
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        maintenance = MaintenanceMode.get_current()
        status = "🟢 ACTIVO" if maintenance.is_active else "🔴 INACTIVO"
        print(f"Estado desde Flask: {status}")
        print(f"Mensaje: {maintenance.message}")
        print(f"Iniciado por: {maintenance.started_by}")

except Exception as e:
    print(f"❌ Error verificando con Flask: {e}")
