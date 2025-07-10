"""
Paquete de rutas modularizadas para la aplicación de Floristería Raquel
Organiza todas las rutas en módulos separados para mejor mantenibilidad
"""

from .auth import auth_bp
from .calendar import calendar_bp
from .users import users_bp
from .time_tracking import time_tracking_bp
from .documents import documents_bp
from .admin import admin_bp

def register_blueprints(app):
    """Registra todos los blueprints en la aplicación Flask"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(time_tracking_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(admin_bp)
