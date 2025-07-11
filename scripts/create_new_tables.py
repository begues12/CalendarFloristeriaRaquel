#!/usr/bin/env python3
"""
Script para crear las nuevas tablas de API y notas
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import db, ApiIntegration, ApiData, CalendarNote

def create_new_tables():
    app = create_app()
    
    with app.app_context():
        print("Creando nuevas tablas...")
        
        # Verificar si las tablas ya existen
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        tables_to_create = []
        
        if 'api_integrations' not in existing_tables:
            tables_to_create.append('api_integrations')
        if 'api_data' not in existing_tables:
            tables_to_create.append('api_data')
        if 'calendar_notes' not in existing_tables:
            tables_to_create.append('calendar_notes')
        
        if not tables_to_create:
            print("✅ Todas las tablas ya existen")
            return
        
        print(f"Creando tablas: {', '.join(tables_to_create)}")
        
        # Crear las tablas específicas
        for table_name in tables_to_create:
            if table_name == 'api_integrations':
                ApiIntegration.__table__.create(db.engine, checkfirst=True)
                print(f"✅ Tabla {table_name} creada")
            elif table_name == 'api_data':
                ApiData.__table__.create(db.engine, checkfirst=True)
                print(f"✅ Tabla {table_name} creada")
            elif table_name == 'calendar_notes':
                CalendarNote.__table__.create(db.engine, checkfirst=True)
                print(f"✅ Tabla {table_name} creada")
        
        print("✅ Todas las nuevas tablas han sido creadas")

if __name__ == '__main__':
    create_new_tables()
