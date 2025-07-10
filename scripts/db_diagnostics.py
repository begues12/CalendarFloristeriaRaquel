#!/usr/bin/env python3
"""
Script para diagnosticar y solucionar problemas de base de datos
==============================================================

Este script ayuda a diagnosticar y resolver problemas comunes de base de datos,
especialmente permisos de escritura y problemas de SQLite.
"""

import os
import sys
import stat
import sqlite3
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_database_permissions():
    """Verificar permisos de base de datos"""
    print("🔍 === DIAGNÓSTICO DE BASE DE DATOS ===\n")
    
    # Rutas de bases de datos comunes
    db_paths = [
        'instance/floristeria.db',
        'instance/floristeria_dev.db', 
        'instance/floristeria_production.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"📁 Verificando: {db_path}")
            
            # Verificar permisos del archivo
            file_stat = os.stat(db_path)
            file_mode = stat.filemode(file_stat.st_mode)
            print(f"   Permisos: {file_mode}")
            print(f"   Tamaño: {file_stat.st_size} bytes")
            
            # Verificar si es escribible
            if os.access(db_path, os.W_OK):
                print("   ✅ Archivo escribible")
            else:
                print("   ❌ Archivo NO escribible")
                
            # Verificar permisos del directorio
            dir_path = os.path.dirname(db_path)
            if os.access(dir_path, os.W_OK):
                print("   ✅ Directorio escribible")
            else:
                print("   ❌ Directorio NO escribible")
            
            # Intentar conexión SQLite
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Intentar una operación de escritura simple
                cursor.execute("PRAGMA journal_mode")
                journal_mode = cursor.fetchone()[0]
                print(f"   Journal mode: {journal_mode}")
                
                # Verificar WAL files
                wal_file = db_path + '-wal'
                shm_file = db_path + '-shm'
                
                if os.path.exists(wal_file):
                    print(f"   WAL file existe: {wal_file}")
                    if not os.access(wal_file, os.W_OK):
                        print("   ❌ WAL file NO escribible")
                
                if os.path.exists(shm_file):
                    print(f"   SHM file existe: {shm_file}")
                    if not os.access(shm_file, os.W_OK):
                        print("   ❌ SHM file NO escribible")
                
                conn.close()
                print("   ✅ Conexión SQLite exitosa")
                
            except Exception as e:
                print(f"   ❌ Error de SQLite: {str(e)}")
            
            print()
    
    # Verificar directorio instance
    instance_dir = 'instance'
    if os.path.exists(instance_dir):
        print(f"📁 Verificando directorio: {instance_dir}")
        if os.access(instance_dir, os.W_OK):
            print("   ✅ Directorio instance escribible")
        else:
            print("   ❌ Directorio instance NO escribible")
    else:
        print("❌ Directorio instance no existe")

def fix_database_permissions():
    """Intentar corregir permisos de base de datos"""
    print("\n🔧 === CORRIGIENDO PERMISOS ===\n")
    
    # Crear directorio instance si no existe
    instance_dir = 'instance'
    if not os.path.exists(instance_dir):
        try:
            os.makedirs(instance_dir, mode=0o755)
            print(f"✅ Directorio {instance_dir} creado")
        except Exception as e:
            print(f"❌ No se pudo crear {instance_dir}: {str(e)}")
            return False
    
    # Corregir permisos del directorio
    try:
        os.chmod(instance_dir, 0o755)
        print(f"✅ Permisos de {instance_dir} corregidos")
    except Exception as e:
        print(f"❌ No se pudieron cambiar permisos de {instance_dir}: {str(e)}")
    
    # Corregir permisos de archivos de BD
    db_paths = [
        'instance/floristeria.db',
        'instance/floristeria_dev.db', 
        'instance/floristeria_production.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                os.chmod(db_path, 0o644)
                print(f"✅ Permisos de {db_path} corregidos")
                
                # Corregir permisos de archivos WAL/SHM si existen
                for suffix in ['-wal', '-shm']:
                    aux_file = db_path + suffix
                    if os.path.exists(aux_file):
                        os.chmod(aux_file, 0o644)
                        print(f"✅ Permisos de {aux_file} corregidos")
                        
            except Exception as e:
                print(f"❌ No se pudieron cambiar permisos de {db_path}: {str(e)}")
    
    return True

def test_database_write():
    """Probar escritura en base de datos"""
    print("\n✏️  === PROBANDO ESCRITURA ===\n")
    
    try:
        from app import create_app
        from app.models import db, User
        
        app = create_app()
        with app.app_context():
            # Intentar una consulta simple
            user_count = User.query.count()
            print(f"✅ Lectura exitosa: {user_count} usuarios encontrados")
            
            # Limpiar cualquier transacción pendiente
            try:
                db.session.rollback()
            except:
                pass
            
            # Intentar una transacción de prueba
            try:
                # Verificar si podemos hacer un commit simple
                db.session.commit()
                print("✅ Commit de prueba exitoso")
                
                # Intentar una operación más compleja
                test_user = User.query.first()
                if test_user:
                    original_name = test_user.full_name
                    test_user.full_name = original_name  # Cambio que no cambia nada
                    db.session.commit()
                    print("✅ Transacción de escritura exitosa")
                else:
                    print("⚠️  No hay usuarios para probar escritura")
                
                return True
                
            except Exception as write_error:
                print(f"❌ Error de escritura: {str(write_error)}")
                try:
                    db.session.rollback()
                except:
                    pass
                return False
                
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False

def create_backup():
    """Crear backup de la base de datos"""
    print("\n💾 === CREANDO BACKUP ===\n")
    
    import shutil
    from datetime import datetime
    
    db_paths = [
        'instance/floristeria.db',
        'instance/floristeria_dev.db', 
        'instance/floristeria_production.db'
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            backup_path = f"{db_path}.backup_{timestamp}"
            try:
                shutil.copy2(db_path, backup_path)
                print(f"✅ Backup creado: {backup_path}")
            except Exception as e:
                print(f"❌ Error creando backup de {db_path}: {str(e)}")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnosticar problemas de base de datos')
    parser.add_argument('--check', action='store_true', help='Solo verificar permisos')
    parser.add_argument('--fix', action='store_true', help='Intentar corregir permisos')
    parser.add_argument('--test', action='store_true', help='Probar escritura en BD')
    parser.add_argument('--backup', action='store_true', help='Crear backup')
    
    args = parser.parse_args()
    
    if args.backup:
        create_backup()
    elif args.test:
        test_database_write()
    elif args.fix:
        check_database_permissions()
        fix_database_permissions()
        test_database_write()
    elif args.check:
        check_database_permissions()
    else:
        # Ejecutar diagnóstico completo
        print("🗄️  DIAGNÓSTICO COMPLETO DE BASE DE DATOS")
        print("=" * 50)
        
        check_database_permissions()
        
        if input("\n¿Intentar corregir permisos? (s/N): ").lower() in ['s', 'si', 'sí']:
            fix_database_permissions()
            test_database_write()
        
        if input("\n¿Crear backup? (s/N): ").lower() in ['s', 'si', 'sí']:
            create_backup()

if __name__ == "__main__":
    main()
