#!/usr/bin/env python3
"""
Script para verificar y agregar la columna can_manage_notes a la tabla users
"""

import sqlite3
import os
from app import create_app, db
from sqlalchemy import inspect

def fix_can_manage_notes_column():
    """Verificar y agregar la columna can_manage_notes si no existe"""
    app = create_app()
    
    # Ruta a la base de datos
    db_path = os.path.join(app.instance_path, 'floristeria.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en: {db_path}")
        print("🔄 Creando nueva base de datos...")
        with app.app_context():
            db.create_all()
            print("✅ Base de datos creada")
        return
    
    print(f"📍 Base de datos encontrada en: {db_path}")
    
    with app.app_context():
        # Verificar si la columna existe
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        print("📋 Columnas actuales en la tabla users:")
        for col in columns:
            print(f"   - {col}")
        
        if 'can_manage_notes' in columns:
            print("\n✅ La columna can_manage_notes ya existe")
            
            # Verificar que los usuarios tengan el valor correcto
            from app.models.user import User
            users = User.query.all()
            updated = 0
            for user in users:
                if user.can_manage_notes is None:
                    user.can_manage_notes = True
                    updated += 1
            
            if updated > 0:
                db.session.commit()
                print(f"✅ {updated} usuarios actualizados con can_manage_notes=True")
            else:
                print("ℹ️  Todos los usuarios ya tienen can_manage_notes configurado")
                
        else:
            print("\n❌ La columna can_manage_notes NO existe")
            print("🔄 Intentando agregar la columna...")
            
            try:
                # Usar SQLite directamente para agregar la columna
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("ALTER TABLE users ADD COLUMN can_manage_notes BOOLEAN DEFAULT 1")
                conn.commit()
                conn.close()
                
                print("✅ Columna can_manage_notes agregada exitosamente")
                
                # Actualizar usuarios existentes
                from app.models.user import User
                users = User.query.all()
                for user in users:
                    if not hasattr(user, 'can_manage_notes') or user.can_manage_notes is None:
                        user.can_manage_notes = True
                
                db.session.commit()
                print(f"✅ {len(users)} usuarios actualizados con can_manage_notes=True")
                
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("ℹ️  La columna ya existe (SQLite error)")
                else:
                    print(f"❌ Error SQLite: {e}")
            except Exception as e:
                print(f"❌ Error al agregar columna: {e}")
        
        # Verificación final
        print("\n🔍 Verificación final:")
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'can_manage_notes' in columns:
            print("✅ can_manage_notes está presente en la base de datos")
            
            # Verificar algunos usuarios
            from app.models.user import User
            users = User.query.limit(3).all()
            print("👥 Estado de usuarios:")
            for user in users:
                notes_perm = getattr(user, 'can_manage_notes', 'NO DEFINIDO')
                print(f"   - {user.username}: can_manage_notes = {notes_perm}")
        else:
            print("❌ can_manage_notes AÚN NO está presente")

if __name__ == '__main__':
    fix_can_manage_notes_column()
