"""
Configuración de la aplicación Flask
===================================

Configuración principal cargada desde variables de entorno.
"""

import os


class Config:
    """Configuración base de la aplicación"""
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_clave_secreta_muy_segura_aqui_cambiar_en_produccion'
    
    # Archivos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'app/static/uploads'
    DOCUMENTS_FOLDER = os.environ.get('DOCUMENTS_FOLDER') or 'app/static/documents'
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


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///floristeria_dev.db'


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///floristeria_production.db'


class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
