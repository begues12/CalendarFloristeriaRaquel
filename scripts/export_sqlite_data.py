#!/usr/bin/env python
"""
Script para exportar datos de SQLite antes de migrar a MySQL
===========================================================

Este script exporta todos los datos de las bases de datos SQLite
a archivos JSON para facilitar la migración a MySQL.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, date
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def serialize_datetime(obj):
    """Serializar objetos datetime para JSON"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def export_sqlite_to_json(db_path, output_dir):
    """Exportar una base de datos SQLite a archivos JSON"""
    if not os.path.exists(db_path):
        print(f"⚠️  Base de datos no encontrada: {db_path}")
        return False
    
    print(f"📤 Exportando: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para obtener diccionarios
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        export_data = {}
        
        for table_name in tables:
            print(f"  📋 Exportando tabla: {table_name}")
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            table_data = []
            for row in rows:
                row_dict = dict(row)
                table_data.append(row_dict)
            
            export_data[table_name] = {
                'count': len(table_data),
                'data': table_data
            }
            
            print(f"    ✅ {len(table_data)} registros exportados")
        
        # Guardar archivo JSON
        db_name = os.path.basename(db_path).replace('.db', '')
        output_file = output_dir / f"{db_name}_export.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=serialize_datetime)
        
        print(f"✅ Exportado a: {output_file}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error exportando {db_path}: {e}")
        return False

def create_import_script(output_dir):
    """Crear script para importar datos a MySQL"""
    import_script = '''#!/usr/bin/env python
"""
Script para importar datos exportados a MySQL
============================================

Ejecutar DESPUÉS de configurar MySQL con setup_mysql.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def import_to_mysql():
    """Importar datos a MySQL"""
    from app import create_app
    from app.models import db, User, TimeEntry, Photo, UserDocument, MaintenanceMode, UpdateLog
    
    app = create_app()
    
    with app.app_context():
        print("🗄️  Importando datos a MySQL...")
        
        # Mapeo de tablas a modelos
        model_mapping = {
            'users': User,
            'time_entries': TimeEntry,
            'photos': Photo,
            'user_documents': UserDocument,
            'maintenance_mode': MaintenanceMode,
            'update_logs': UpdateLog
        }
        
        export_files = list(Path('data_export').glob('*_export.json'))
        
        for export_file in export_files:
            print(f"📁 Procesando: {export_file}")
            
            with open(export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for table_name, table_info in data.items():
                if table_name in model_mapping:
                    model_class = model_mapping[table_name]
                    records = table_info['data']
                    
                    print(f"  📋 Importando {len(records)} registros a {table_name}")
                    
                    for record in records:
                        # Convertir fechas de string a datetime si es necesario
                        for key, value in record.items():
                            if isinstance(value, str) and ('_at' in key or key in ['date', 'hire_date']):
                                try:
                                    if 'T' in value:
                                        record[key] = datetime.fromisoformat(value.replace('T', ' ').replace('Z', ''))
                                    else:
                                        record[key] = datetime.strptime(value, '%Y-%m-%d').date()
                                except:
                                    pass
                        
                        try:
                            # Crear objeto del modelo
                            obj = model_class(**record)
                            db.session.add(obj)
                        except Exception as e:
                            print(f"    ⚠️  Error con registro {record.get('id', '?')}: {e}")
                    
                    try:
                        db.session.commit()
                        print(f"    ✅ {table_name} importado correctamente")
                    except Exception as e:
                        print(f"    ❌ Error importando {table_name}: {e}")
                        db.session.rollback()
        
        print("🎉 Importación completada!")

if __name__ == "__main__":
    import_to_mysql()
'''
    
    script_path = output_dir / 'import_to_mysql.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(import_script)
    
    print(f"📝 Script de importación creado: {script_path}")

def main():
    """Función principal"""
    print("📤 EXPORTADOR DE DATOS SQLITE")
    print("=" * 40)
    
    # Crear directorio de exportación
    output_dir = root_dir / 'data_export'
    output_dir.mkdir(exist_ok=True)
    
    # Bases de datos a exportar
    databases = [
        'instance/floristeria.db',
        'instance/floristeria_dev.db', 
        'instance/floristeria_production.db'
    ]
    
    # Exportar cada base de datos
    exported_any = False
    for db_path in databases:
        full_path = root_dir / db_path
        if export_sqlite_to_json(full_path, output_dir):
            exported_any = True
    
    if exported_any:
        # Crear script de importación
        create_import_script(output_dir)
        
        print("\n✅ EXPORTACIÓN COMPLETADA")
        print("=" * 40)
        print(f"📁 Datos exportados en: {output_dir}")
        print("📝 Script de importación creado")
        print("\n🔄 Pasos siguientes:")
        print("1. Ejecutar: python scripts/setup_mysql.py")
        print("2. Ejecutar: python data_export/import_to_mysql.py")
    else:
        print("\n⚠️  No se encontraron bases de datos SQLite para exportar")
        print("   Esto es normal si es una instalación nueva")

if __name__ == "__main__":
    main()
