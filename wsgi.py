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

# Print data base environment variable
print(f"Database URL: {application.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == "__main__":
    application.run()


# Clave del cliente ck_cda0de90e5b9c4ef0130a0aa98a92dc526425c78
# Clave secreta de cliente cs_e35c00cd198e198148fbf2cdbe96d1044c5169fc