from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime, date, timedelta
import calendar
import os
from PIL import Image
from dotenv import load_dotenv

# Importar modelos
from models import db, User, TimeEntry, UserDocument, Photo, MaintenanceMode

# Cargar variables de entorno
load_dotenv()

# Configuración desde variables de entorno
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_clave_secreta_muy_segura_aqui_cambiar_en_produccion'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    DOCUMENTS_FOLDER = os.environ.get('DOCUMENTS_FOLDER') or 'static/documents'
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB por defecto
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,pdf,doc,docx').split(','))
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///floristeria.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de la aplicación
    APP_NAME = os.environ.get('APP_NAME') or 'Floristería Raquel'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST') or '0.0.0.0'
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Usuarios por defecto
    DEFAULT_ADMIN_USER = os.environ.get('DEFAULT_ADMIN_USER') or 'admin'
    DEFAULT_ADMIN_PASS = os.environ.get('DEFAULT_ADMIN_PASS') or 'admin123'
    DEFAULT_USER_USER = os.environ.get('DEFAULT_USER_USER') or 'raquel'
    DEFAULT_USER_PASS = os.environ.get('DEFAULT_USER_PASS') or 'floreria2025'

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
migrate = Migrate(app, db)

# Registrar filtros personalizados para Jinja2
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

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

# Crear carpetas necesarias
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.DOCUMENTS_FOLDER, exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('templates', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(800, 600)):
    """Redimensiona imagen para optimizar el almacenamiento"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, optimize=True, quality=85)
    except Exception as e:
        print(f"Error redimensionando imagen: {e}")

def hours_to_hhmm(hours_decimal):
    """Convierte horas decimales a formato HH:MM"""
    if not hours_decimal:
        return "00:00"
    
    total_minutes = int(hours_decimal * 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"

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
        
        # Crear usuario regular
        user = User(
            username=Config.DEFAULT_USER_USER,
            full_name='Raquel',
            is_admin=False,
            must_change_password=True  # Usuario debe cambiar contraseña en primer acceso
        )
        user.set_password(Config.DEFAULT_USER_PASS)
        
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

# Registrar blueprints de rutas
from rutas import register_blueprints
register_blueprints(app)









if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_users()
    
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
