#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación Floristería Raquel
==============================================================

Este script inicializa y ejecuta la aplicación Flask con la configuración apropiada.
"""

import os
import sys

# Agregar el directorio raíz al path para los imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, init_default_users
from app.models import db
from config.settings import config


def main():
    """Función principal para ejecutar la aplicación"""
    # Determinar el entorno
    config_name = os.environ.get('FLASK_CONFIG') or 'default'
    
    # Crear directorios necesarios
    os.makedirs('instance', exist_ok=True)
    os.makedirs('app/static/uploads', exist_ok=True)
    os.makedirs('app/static/documents', exist_ok=True)
    
    # Crear la aplicación
    app = create_app(config[config_name])
    
    with app.app_context():
        # Crear las tablas si no existen
        db.create_all()
        
        # Inicializar usuarios por defecto
        init_default_users()
    
    # Ejecutar la aplicación
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )


if __name__ == '__main__':
    main()
