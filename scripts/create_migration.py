#!/usr/bin/env python3
"""
Script para crear migración para agregar columna must_change_password
"""

import os
from flask_migrate import Migrate, migrate, upgrade
from app import app, db

def create_migration():
    with app.app_context():
        # Crear la migración
        migrate(message='add_must_change_password_column')

if __name__ == '__main__':
    # Establecer variable de entorno
    os.environ['FLASK_APP'] = 'app.py'
    create_migration()
