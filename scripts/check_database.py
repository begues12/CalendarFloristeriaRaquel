#!/usr/bin/env python
"""
Script para verificar la configuración de la base de datos
=========================================================

Verifica qué tipo de base de datos está configurada y su estado.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def check_database_config():
    """Verificar configuración de base de datos"""
    print("🔍 VERIFICACIÓN DE BASE DE DATOS")
    print("=" * 40)
    
    try:
        from app import create_app
        from app.models import db, User
        
        app = create_app()
        
        with app.app_context():
            # Información de configuración
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            print(f"📄 Database URI: {db_uri}")
            
            # Determinar tipo de base de datos
            if 'mysql' in db_uri.lower():
                db_type = "MySQL"
                print("🗄️  Tipo de BD: MySQL")
            elif 'sqlite' in db_uri.lower():
                db_type = "SQLite"
                print("🗄️  Tipo de BD: SQLite")
            else:
                db_type = "Desconocido"
                print("🗄️  Tipo de BD: Desconocido")
            
            # Verificar conexión
            try:
                # Test de conexión simple
                result = db.engine.execute("SELECT 1").scalar()
                print("✅ Conexión: Exitosa")
                
                # Verificar tablas
                try:
                    user_count = User.query.count()
                    print(f"👥 Usuarios en BD: {user_count}")
                    
                    # Mostrar información de tablas
                    inspector = db.inspect(db.engine)
                    tables = inspector.get_table_names()
                    print(f"📋 Tablas encontradas: {len(tables)}")
                    
                    for table in sorted(tables):
                        print(f"   - {table}")
                    
                    print("✅ Estado: Base de datos operativa")
                    
                except Exception as e:
                    print(f"⚠️  Error accediendo a tablas: {e}")
                    print("💡 Posible solución: Ejecutar 'flask db upgrade'")
                
            except Exception as e:
                print(f"❌ Error de conexión: {e}")
                
                if 'mysql' in db_uri.lower():
                    print("💡 Soluciones posibles para MySQL:")
                    print("   1. Verificar que MySQL esté ejecutándose")
                    print("   2. Verificar credenciales en .env")
                    print("   3. Verificar que la base de datos existe")
                    print("   4. Instalar PyMySQL: pip install PyMySQL")
                elif 'sqlite' in db_uri.lower():
                    print("💡 Soluciones posibles para SQLite:")
                    print("   1. Verificar permisos de escritura en instance/")
                    print("   2. Ejecutar 'flask db upgrade'")
    
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Instalar dependencias: pip install -r requirements.txt")
        return False
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    
    return True

def check_mysql_availability():
    """Verificar disponibilidad de MySQL"""
    print("\n🐬 VERIFICACIÓN DE MYSQL")
    print("=" * 30)
    
    try:
        import pymysql
        print("✅ PyMySQL: Instalado")
        
        # Test de conexión básica (sin base de datos específica)
        try:
            host = input("Host MySQL (localhost): ").strip() or 'localhost'
            port = int(input("Puerto MySQL (3306): ").strip() or '3306')
            user = input("Usuario MySQL (root): ").strip() or 'root'
            password = input("Contraseña MySQL: ").strip()
            
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password
            )
            
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            print("✅ Conexión MySQL: Exitosa")
            print("📋 Bases de datos disponibles:")
            for db in databases:
                print(f"   - {db[0]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error conectando a MySQL: {e}")
            return False
    
    except ImportError:
        print("❌ PyMySQL: No instalado")
        print("💡 Instalar con: pip install PyMySQL")
        return False

def suggest_next_steps():
    """Sugerir próximos pasos según el estado actual"""
    print("\n🚀 PRÓXIMOS PASOS SUGERIDOS")
    print("=" * 30)
    
    # Verificar si existe .env
    env_file = root_dir / '.env'
    if env_file.exists():
        print("✅ Archivo .env encontrado")
    else:
        print("⚠️  Archivo .env no encontrado")
        print("💡 Crear .env con configuración de BD")
    
    # Verificar migraciones
    migrations_dir = root_dir / 'migrations'
    if migrations_dir.exists():
        print("✅ Carpeta migrations encontrada")
    else:
        print("⚠️  Carpeta migrations no encontrada")
        print("💡 Ejecutar: flask db init")
    
    # Verificar requisitos
    try:
        import pymysql
        print("✅ PyMySQL disponible")
    except ImportError:
        print("⚠️  PyMySQL no disponible")
        print("💡 Ejecutar: pip install PyMySQL cryptography")
    
    print("\n📋 Comandos útiles:")
    print("   Migrar a MySQL: python scripts/setup_mysql.py")
    print("   Exportar SQLite: python scripts/export_sqlite_data.py")
    print("   Inicializar BD: python scripts/init_database.py")
    print("   Ejecutar app: python run.py")

def main():
    """Función principal"""
    os.chdir(root_dir)
    
    success = check_database_config()
    
    print("\n" + "=" * 50)
    
    # Solo verificar MySQL si la configuración actual falló o es SQLite
    verify_mysql = input("\n¿Verificar disponibilidad de MySQL? (s/N): ").lower().strip() == 's'
    if verify_mysql:
        check_mysql_availability()
    
    suggest_next_steps()

if __name__ == "__main__":
    main()
