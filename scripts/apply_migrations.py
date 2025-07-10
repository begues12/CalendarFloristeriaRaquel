#!/usr/bin/env python3
"""
Script simple para aplicar migraciones
====================================

Script simplificado para ejecutar solo las migraciones de base de datos
sin las otras operaciones de actualización del sistema.
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def apply_migrations():
    """Aplicar migraciones de base de datos"""
    try:
        from app import create_app
        from flask_migrate import upgrade
        
        # Crear app y aplicar migraciones
        app = create_app()
        
        with app.app_context():
            print("🗄️  Aplicando migraciones...")
            upgrade()
            print("✅ Migraciones aplicadas correctamente")
            return True
            
    except Exception as e:
        print(f"❌ Error aplicando migraciones: {str(e)}")
        return False

def main():
    """Función principal"""
    print("=== APLICAR MIGRACIONES ===")
    success = apply_migrations()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
