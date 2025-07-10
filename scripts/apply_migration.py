#!/usr/bin/env python3
"""
Script para aplicar migración de base de datos
"""

import os
from flask_migrate import upgrade
from app import app, db

def apply_migration():
    with app.app_context():
        # Aplicar la migración
        upgrade()
        print("Migración aplicada exitosamente!")

if __name__ == '__main__':
    # Establecer variable de entorno
    os.environ['FLASK_APP'] = 'app.py'
    apply_migration()
