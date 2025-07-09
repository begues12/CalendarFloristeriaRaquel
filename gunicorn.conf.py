# Configuración para Gunicorn (servidor WSGI para producción)
# Guarda este archivo como gunicorn.conf.py

# Configuración del servidor
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Configuración de archivos
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Configuración de logs
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configuración de rendimiento
preload_app = True
max_requests = 1000
max_requests_jitter = 50

# Variables de entorno
raw_env = [
    'FLASK_ENV=production',
]
