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
    
    # Base de datos MySQL
    # Formato: mysql+pymysql://usuario:contraseña@servidor:puerto/base_de_datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost:3306/floristeria'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración del pool de conexiones MySQL (optimizada con variables de entorno)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 300)),
        'pool_timeout': int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT', 20)),
        'pool_size': int(os.environ.get('SQLALCHEMY_POOL_SIZE', 5)),
        'max_overflow': int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', 0)),
        'echo': os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    }
    
    # Configuración específica de MySQL
    MYSQL_CHARSET = os.environ.get('MYSQL_CHARSET', 'utf8mb4')
    MYSQL_COLLATION = os.environ.get('MYSQL_COLLATION', 'utf8mb4_unicode_ci')
    
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
    
    # Pool más pequeño para desarrollo
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 300)),
        'pool_timeout': int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT', 20)),
        'pool_size': int(os.environ.get('SQLALCHEMY_POOL_SIZE', 2)),
        'max_overflow': int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', 5)),
        'echo': os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    }


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost:3306/floristeria_production'
    
    # Pool optimizado para producción
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 3600)),
        'pool_timeout': int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT', 20)),
        'pool_size': int(os.environ.get('SQLALCHEMY_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', 20)),
        'echo': False  # Nunca activar en producción
    }


class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # Pool mínimo para testing
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': False,
        'pool_recycle': -1,
        'pool_timeout': 10,
        'pool_size': 1,
        'max_overflow': 0,
        'echo': False
    }


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
