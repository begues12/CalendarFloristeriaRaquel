#!/usr/bin/env python
"""
Test script para simular condiciones de database lock y verificar robustez
"""

import sys
import os
import threading
import time

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import db, UpdateLog, MaintenanceMode, User

def simulate_concurrent_access():
    """Simular acceso concurrente que puede causar database lock"""
    
    def worker(worker_id):
        """Worker que intenta escribir a la BD simultáneamente"""
        app = create_app()
        with app.app_context():
            try:
                # Simular lo que hace el route update_system
                user = User.query.first()
                
                # Crear log
                update_log = UpdateLog(
                    started_by=f"test_user_{worker_id}",
                    git_commit_before=f"test_commit_{worker_id}"
                )
                db.session.add(update_log)
                db.session.commit()
                
                # Activar mantenimiento
                maintenance = MaintenanceMode.get_current()
                if not maintenance.is_active:
                    maintenance.activate(user, f"Test desde worker {worker_id}", 1)
                
                # Completar log
                update_log.mark_completed(f"test_commit_after_{worker_id}")
                
                # Desactivar mantenimiento
                maintenance.deactivate()
                
                print(f"✅ Worker {worker_id}: Todo OK")
                return True
                
            except Exception as e:
                print(f"❌ Worker {worker_id}: Error {e}")
                return False
    
    print("🔄 === TEST DE CONCURRENCIA ===")
    print("Simulando 5 workers accediendo simultáneamente...")
    
    threads = []
    results = []
    
    def worker_wrapper(worker_id, results_list):
        """Wrapper para capturar resultados"""
        result = worker(worker_id)
        results_list.append(result)
    
    # Crear y lanzar threads
    for i in range(5):
        thread = threading.Thread(target=worker_wrapper, args=(i, results))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Pequeño delay para aumentar probabilidad de conflicto
    
    # Esperar a todos los threads
    for thread in threads:
        thread.join()
    
    successful = sum(1 for r in results if r)
    print(f"📊 Resultados: {successful}/{len(results)} workers exitosos")
    
    return successful >= 3  # Al menos 3 de 5 deben ser exitosos

def test_database_stress():
    """Test de stress de la base de datos"""
    print("\n🏋️  === TEST DE STRESS ===")
    
    app = create_app()
    with app.app_context():
        try:
            user = User.query.first()
            
            # Crear muchos logs rápidamente
            for i in range(10):
                update_log = UpdateLog(
                    started_by=f"stress_test_{i}",
                    git_commit_before=f"stress_commit_{i}"
                )
                db.session.add(update_log)
                db.session.commit()
                
                # Simular activar/desactivar mantenimiento rápidamente
                maintenance = MaintenanceMode.get_current()
                maintenance.activate(user, f"Stress test {i}", 1)
                maintenance.deactivate()
                
                update_log.mark_completed(f"stress_commit_after_{i}")
            
            print("✅ Test de stress completado")
            return True
            
        except Exception as e:
            print(f"❌ Error en test de stress: {e}")
            return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE ROBUSTEZ")
    print("=" * 50)
    
    # Test básico primero
    app = create_app()
    with app.app_context():
        initial_logs = UpdateLog.query.count()
        print(f"📊 Logs iniciales: {initial_logs}")
    
    # Tests de robustez
    success1 = simulate_concurrent_access()
    success2 = test_database_stress()
    
    # Verificar estado final
    with app.app_context():
        final_logs = UpdateLog.query.count()
        print(f"📊 Logs finales: {final_logs}")
        print(f"📊 Logs añadidos: {final_logs - initial_logs}")
    
    print("\n📋 === RESUMEN FINAL ===")
    print(f"Test Concurrencia: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Test Stress: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 Sistema robusto ante condiciones adversas!")
    else:
        print("\n⚠️  Algunos tests fallaron. El sistema podría tener problemas bajo carga.")
