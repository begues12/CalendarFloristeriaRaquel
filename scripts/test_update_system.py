#!/usr/bin/env python3
"""
Script para probar el sistema de actualización
============================================

Este script permite probar las funciones de actualización sin riesgos.
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_update_log_creation():
    """Probar creación de logs de actualización"""
    print("🧪 === PROBANDO CREACIÓN DE UPDATE LOG ===\n")
    
    try:
        from app import create_app
        from app.models import db, UpdateLog
        
        app = create_app()
        with app.app_context():
            # Limpiar cualquier transacción pendiente
            try:
                db.session.rollback()
            except:
                pass
            
            # Intentar crear un log de prueba
            test_log = UpdateLog(
                started_by='test_user',
                git_commit_before='test_commit_123'
            )
            
            db.session.add(test_log)
            db.session.commit()
            
            print("✅ Log de actualización creado exitosamente")
            print(f"   ID: {test_log.id}")
            print(f"   Usuario: {test_log.started_by}")
            print(f"   Fecha: {test_log.started_at}")
            
            # Probar actualización del log
            test_log.mark_completed('test_commit_456')
            db.session.commit()
            
            print("✅ Log actualizado exitosamente")
            print(f"   Estado: {test_log.status}")
            print(f"   Commit final: {test_log.git_commit_after}")
            
            # Limpiar - eliminar log de prueba
            db.session.delete(test_log)
            db.session.commit()
            
            print("✅ Log de prueba eliminado")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False

def test_maintenance_mode():
    """Probar activación/desactivación de modo mantenimiento"""
    print("\n🔧 === PROBANDO MODO MANTENIMIENTO ===\n")
    
    try:
        from app import create_app
        from app.models import db, MaintenanceMode, User
        
        app = create_app()
        with app.app_context():
            # Limpiar sesión
            try:
                db.session.rollback()
            except:
                pass
            
            # Obtener o crear modo mantenimiento
            maintenance = MaintenanceMode.get_current()
            print(f"Estado inicial: {'Activo' if maintenance.is_active else 'Inactivo'}")
            
            # Obtener un usuario de prueba
            test_user = User.query.first()
            if not test_user:
                print("❌ No hay usuarios disponibles para prueba")
                return False
            
            # Probar activación
            if not maintenance.is_active:
                maintenance.activate(test_user, 'Prueba de mantenimiento', 5)
                print("✅ Modo mantenimiento activado")
            
            # Verificar estado
            maintenance = MaintenanceMode.get_current()
            print(f"Estado después de activar: {'Activo' if maintenance.is_active else 'Inactivo'}")
            
            # Probar desactivación
            if maintenance.is_active:
                maintenance.deactivate()
                print("✅ Modo mantenimiento desactivado")
            
            # Verificar estado final
            maintenance = MaintenanceMode.get_current()
            print(f"Estado final: {'Activo' if maintenance.is_active else 'Inactivo'}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False

def test_system_update_script():
    """Probar script de actualización del sistema"""
    print("\n🚀 === PROBANDO SCRIPT DE ACTUALIZACIÓN ===\n")
    
    import subprocess
    import json
    
    try:
        python_executable = sys.executable
        script_path = os.path.join(os.getcwd(), 'scripts', 'system_update.py')
        
        # Probar solo migraciones
        result = subprocess.run(
            [python_executable, script_path, '--migrate-only', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            script_result = json.loads(result.stdout)
            print("✅ Script de actualización funcionando")
            print(f"   Éxito: {script_result.get('success', False)}")
            print(f"   Mensaje: {script_result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Script falló: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando script: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBAS DEL SISTEMA DE ACTUALIZACIÓN")
    print("=" * 50)
    
    tests = [
        ("Creación de Update Log", test_update_log_creation),
        ("Modo Mantenimiento", test_maintenance_mode),
        ("Script de Actualización", test_system_update_script)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + ("🎉 TODAS LAS PRUEBAS PASARON" if all_passed else "⚠️  ALGUNAS PRUEBAS FALLARON"))

if __name__ == "__main__":
    main()
