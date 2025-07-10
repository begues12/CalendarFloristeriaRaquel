#!/usr/bin/env python
"""
Test script para verificar la funcionalidad de UpdateLog y detectar problemas de escritura
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import db, UpdateLog, MaintenanceMode, User

def test_update_log_creation():
    """Test de creación de UpdateLog"""
    app = create_app()
    
    with app.app_context():
        print("🧪 === TEST DE UPDATE LOG ===")
        
        # 1. Verificar estado inicial
        print(f"Logs existentes: {UpdateLog.query.count()}")
        
        # 2. Limpiar sesión
        try:
            db.session.rollback()
            print("✅ Sesión limpiada")
        except Exception as e:
            print(f"⚠️  Warning limpiando sesión: {e}")
        
        # 3. Intentar crear un nuevo log
        try:
            # Obtener un usuario para el test
            user = User.query.filter_by(is_super_admin=True).first()
            if not user:
                user = User.query.first()
            
            if not user:
                print("❌ No hay usuarios en la base de datos")
                return False
            
            # Crear el log
            update_log = UpdateLog(
                started_by=user.username,
                git_commit_before="test_commit_123"
            )
            
            db.session.add(update_log)
            db.session.commit()
            
            print(f"✅ Log creado exitosamente: ID {update_log.id}")
            
            # 4. Intentar actualizarlo
            update_log.mark_completed("test_commit_456")
            print("✅ Log actualizado exitosamente")
            
            # 5. Verificar count actualizado
            print(f"Logs totales ahora: {UpdateLog.query.count()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando/actualizando log: {e}")
            print(f"Tipo de error: {type(e).__name__}")
            
            # Intentar rollback
            try:
                db.session.rollback()
                print("✅ Rollback realizado")
            except Exception as rb_error:
                print(f"❌ Error en rollback: {rb_error}")
            
            return False

def test_maintenance_mode():
    """Test de MaintenanceMode"""
    app = create_app()
    
    with app.app_context():
        print("\n🧪 === TEST DE MAINTENANCE MODE ===")
        
        try:
            # Obtener estado actual
            maintenance = MaintenanceMode.get_current()
            print(f"Estado actual: {'Activo' if maintenance.is_active else 'Inactivo'}")
            
            # Obtener un usuario
            user = User.query.filter_by(is_super_admin=True).first()
            if not user:
                user = User.query.first()
            
            if user:
                # Test activar
                if not maintenance.is_active:
                    maintenance.activate(user, "Test de mantenimiento", 5)
                    print("✅ Mantenimiento activado")
                
                # Test desactivar
                maintenance.deactivate()
                print("✅ Mantenimiento desactivado")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en maintenance mode: {e}")
            try:
                db.session.rollback()
            except:
                pass
            return False

if __name__ == "__main__":
    print("🔍 INICIANDO TESTS DE UPDATE SYSTEM")
    print("=" * 50)
    
    success1 = test_update_log_creation()
    success2 = test_maintenance_mode()
    
    print("\n📊 === RESUMEN ===")
    print(f"Update Log Test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Maintenance Mode Test: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 Todos los tests pasaron. El sistema de update debería funcionar.")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar la configuración de la base de datos.")
