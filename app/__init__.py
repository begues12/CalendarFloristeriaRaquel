"""
Floristería Raquel - Aplicación Flask
====================================

Sistema de gestión para floristería con calendario, control de horarios,
gestión de documentos y sistema de privilegios granular.
"""

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar modelos después de cargar variables de entorno
from app.models import db, User, MaintenanceMode
from app.utils.helpers import hours_to_hhmm
from config.settings import Config


def create_app(config_class=Config):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    init_extensions(app)
    
    # Registrar filtros personalizados
    register_filters(app)
    
    # Registrar middleware
    register_middleware(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Crear carpetas necesarias
    create_directories(app)
    
    return app


def init_extensions(app):
    """Inicializar extensiones Flask"""
    # Base de datos
    db.init_app(app)
    
    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def register_filters(app):
    """Registrar filtros personalizados para Jinja2"""
    @app.template_filter('hours_to_hhmm')
    def hours_to_hhmm_filter(hours_decimal):
        """Filtro Jinja2 para convertir horas decimales a HH:MM"""
        return hours_to_hhmm(hours_decimal)

    @app.template_filter('strftime')
    def strftime_filter(date, format='%Y-%m-%d'):
        """Filtro Jinja2 para formatear fechas"""
        if date:
            return date.strftime(format)
        return ''


def register_middleware(app):
    """Registrar middleware de la aplicación"""
    
    @app.before_request
    def check_maintenance_mode():
        """Middleware para verificar modo mantenimiento"""
        # Rutas que pueden acceder durante mantenimiento
        exempt_routes = [
            'static',
            'admin.super_admin_panel',
            'admin.toggle_maintenance',
            'admin.update_system',
            'admin.check_updates',
            'auth.login',  # Permitir acceso al login durante mantenimiento
            'auth.logout'
        ]
        
        # Si es una solicitud de archivo estático o ruta exenta, permitir
        if request.endpoint and request.endpoint in exempt_routes:
            return
            
        # Verificar modo mantenimiento
        try:
            maintenance = MaintenanceMode.get_current()
            if maintenance.is_active:
                # Solo super admins pueden acceder durante mantenimiento
                if not (current_user.is_authenticated and current_user.is_super_admin):
                    return render_template('maintenance.html', maintenance=maintenance), 503
        except Exception:
            # Si hay error accediendo a la DB, no bloquear
            pass

    @app.before_request
    def check_password_change_required():
        """Middleware para verificar si el usuario debe cambiar su contraseña"""
        # Rutas que no requieren verificación de cambio de contraseña
        exempt_routes = [
            'auth.login', 
            'auth.logout', 
            'auth.force_change_password', 
            'static'
        ]
        
        # Si es una solicitud de archivo estático, permitir
        if request.endpoint and request.endpoint in exempt_routes:
            return
        
        # Si el usuario está autenticado y debe cambiar contraseña
        if current_user.is_authenticated and hasattr(current_user, 'must_change_password'):
            if current_user.must_change_password and request.endpoint != 'auth.force_change_password':
                return redirect(url_for('auth.force_change_password'))


def register_blueprints(app):
    """Registrar blueprints de la aplicación"""
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.calendar import bp as calendar_bp
    from app.blueprints.time_tracking import bp as time_tracking_bp
    from app.blueprints.documents import bp as documents_bp
    from app.blueprints.admin import bp as admin_bp
    from app.blueprints.users import bp as users_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(calendar_bp)
    app.register_blueprint(time_tracking_bp, url_prefix='/time')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(users_bp, url_prefix='/users')


def create_directories(app):
    """Crear directorios necesarios"""
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config['DOCUMENTS_FOLDER'],
        'app/static/css',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def init_default_users():
    """Crear usuarios por defecto si no existen"""
    if not User.query.first():
        # Crear admin
        admin = User(
            username=Config.DEFAULT_ADMIN_USER,
            full_name='Administrador',
            is_admin=True,
            must_change_password=False  # Admin por defecto no necesita cambiar contraseña
        )
        admin.set_password(Config.DEFAULT_ADMIN_PASS)
        admin.set_default_privileges()  # Establecer privilegios por defecto
        
        # Crear usuario regular
        user = User(
            username=Config.DEFAULT_USER_USER,
            full_name='Raquel',
            is_admin=False,
            must_change_password=True  # Usuario debe cambiar contraseña en primer acceso
        )
        user.set_password(Config.DEFAULT_USER_PASS)
        user.set_default_privileges()  # Establecer privilegios por defecto
        
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()
