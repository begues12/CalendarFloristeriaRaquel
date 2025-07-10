# Guía de Solución de Problemas de Despliegue

## 🚨 Error: `[Errno 2] No such file or directory: 'flask'`

Este error indica que Flask no está instalado o no está disponible como comando en el servidor.

### Soluciones paso a paso:

#### 1. Verificación Rápida
```bash
# En el servidor, ejecuta:
python check_server.py
```

#### 2. Diagnóstico Completo
```bash
python deploy.py
# Selecciona opción 2: "Diagnosticar entorno del servidor"
```

#### 3. Solución Automática
```bash
python deploy.py
# Selecciona opción 1: "Configurar producción"
```

#### 4. Solución Manual

Si el script automático falla, sigue estos pasos:

```bash
# 1. Verificar Python
python --version

# 2. Verificar pip
pip --version

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar Flask
python -c "import flask; print(flask.__version__)"

# 5. Configurar entorno
copy .env.production .env    # Windows
cp .env.production .env      # Linux

# 6. Inicializar base de datos
python init_database.py

# 7. Crear usuarios iniciales
python init_users.py

# 8. Ejecutar aplicación
python app.py
```

### Scripts de Ayuda

#### `check_server.py`
Verificación rápida del estado del sistema:
```bash
python check_server.py
```

#### `init_database.py`
Inicialización alternativa de base de datos:
```bash
python init_database.py
```

#### `deploy.py`
Script completo de despliegue con diagnóstico:
```bash
python deploy.py
```

## 🔍 Problemas Comunes

### Flask no instalado
```bash
pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login Flask-WTF
```

### Comando flask no funciona
```bash
# En lugar de: flask db upgrade
python init_database.py
```

### Base de datos no se crea
```bash
# Método 1
python -c "from app import app, db; db.create_all()"

# Método 2
python init_database.py
```

### Archivos de configuración
```bash
# Si falta .env
copy .env.production .env

# Editar configuración
notepad .env    # Windows
nano .env       # Linux
```

### Permisos de archivos
```bash
# Linux: dar permisos de ejecución
chmod +x *.py
chmod +x *.sh

# Crear carpetas necesarias
mkdir -p static/uploads static/documents instance backups
```

## 🚀 Proceso Completo de Despliegue

### 1. Preparación Local
```bash
# Crear paquete de despliegue
python deploy.py
# Seleccionar opción 4: "Crear paquete de despliegue"
```

### 2. En el Servidor
```bash
# Subir y descomprimir archivos
unzip floristeria_deploy_*.zip

# Verificar estado
python check_server.py

# Configurar producción
python deploy.py
# Seleccionar opción 1: "Configurar producción"

# Si hay errores, diagnosticar
python deploy.py
# Seleccionar opción 2: "Diagnosticar entorno"
```

### 3. Configuración Final
```bash
# Editar configuración segura
nano .env

# Cambiar estas variables:
SECRET_KEY=tu_clave_secreta_unica
DEFAULT_ADMIN_PASS=contraseña_admin_segura
DEFAULT_USER_PASS=contraseña_usuario_segura
```

### 4. Ejecutar
```bash
# Desarrollo
python app.py

# Producción con Gunicorn
gunicorn -c gunicorn.conf.py app:app
```

## 📋 Lista de Verificación Pre-despliegue

### Archivos Necesarios
- [ ] `app.py`
- [ ] `models.py`
- [ ] `requirements.txt`
- [ ] `.env.production`
- [ ] `deploy.py`
- [ ] `check_server.py`
- [ ] `init_database.py`
- [ ] `init_users.py`
- [ ] Carpeta `templates/`
- [ ] Carpeta `static/`
- [ ] Carpeta `migrations/`

### Scripts de Ayuda
- [ ] `check_server.py` - Verificación rápida
- [ ] `deploy.py` - Despliegue completo
- [ ] `init_database.py` - Inicialización BD
- [ ] `init_users.py` - Usuarios iniciales

### Configuración del Servidor
- [ ] Python 3.8+ instalado
- [ ] pip funcional
- [ ] Permisos de escritura en directorio
- [ ] Puerto 5000 disponible (o configurar otro)

## 🆘 Contacto de Soporte

Si los problemas persisten:

1. Ejecuta `python check_server.py` y guarda la salida
2. Ejecuta `python deploy.py` (opción 2) y guarda la salida
3. Proporciona información del servidor:
   - Sistema operativo
   - Versión de Python
   - Mensajes de error completos

## 🎯 Soluciones Específicas por Error

### Error: ModuleNotFoundError: No module named 'flask'
```bash
pip install Flask
```

### Error: No such file or directory: 'flask'
```bash
# Usar script alternativo
python init_database.py
```

### Error: Permission denied
```bash
# Linux
chmod +x *.py
sudo chown -R $USER:$USER .

# Windows
# Ejecutar como administrador
```

### Error: Address already in use
```bash
# Cambiar puerto en .env
FLASK_PORT=5001

# O matar proceso existente
pkill -f "python app.py"
```

### Error: Database is locked
```bash
# Verificar permisos
chmod 664 instance/*.db

# Reiniciar aplicación
pkill -f "python app.py"
python app.py
```
