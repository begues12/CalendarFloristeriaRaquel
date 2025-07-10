"""
Punto de entrada WSGI para la aplicación en producción
====================================================

Este archivo es utilizado por servidores WSGI como Gunicorn.
"""

import os
from app import create_app
from config.settings import config

# Determinar el entorno (producción por defecto)
config_name = os.environ.get('FLASK_CONFIG') or 'production'

# Crear la aplicación
application = create_app(config[config_name])

if __name__ == "__main__":
    application.run()
