# Guía de Despliegue - Floristería Raquel

Esta guía te ayudará a desplegar la aplicación en un servidor manteniendo bases de datos separadas entre desarrollo y producción.

## 📋 Resumen del Sistema

- **Desarrollo**: Base de datos local (`floristeria.db`)
- **Producción**: Base de datos separada (`floristeria_production.db`)
- **Sincronización**: Scripts automáticos para exportar/importar datos
- **Despliegue**: Scripts automatizados para configuración

## 🚀 Despliegue Inicial

### Opción 1: Despliegue Manual

1. **Preparar archivos en local:**
   ```bash
   python deploy.py
   # Selecciona opción 2: "Listar archivos de despliegue"
   ```

2. **Subir archivos al servidor:**
   - Sube todos los archivos ✅ mostrados al servidor
   - Incluye las carpetas: `templates/`, `static/`, `migrations/`

3. **Configurar en el servidor:**
   ```bash
   python deploy.py
   # Selecciona opción 1: "Configurar producción"
   ```

4. **Personalizar configuración:**
   - Edita el archivo `.env` generado
   - Cambia `SECRET_KEY` por una clave única y segura
   - Cambia las contraseñas por defecto
   - Ajusta configuraciones según tu servidor

### Opción 2: Paquete de Despliegue

1. **Crear paquete en local:**
   ```bash
   python deploy.py
   # Selecciona opción 3: "Crear paquete de despliegue"
   ```

2. **Subir al servidor:**
   - Sube el archivo .zip generado
   - Descomprime en el directorio del proyecto

3. **Configurar en servidor:**
   ```bash
   python deploy.py
   # Selecciona opción 1: "Configurar producción"
   ```

## 🔄 Sincronización de Datos

### Exportar datos desde desarrollo

En tu máquina local:
```bash
python sync_data.py
# Selecciona opción 1: "Exportar datos"
```

Esto crea una carpeta `data_export/` con todos los datos en formato JSON.

### Importar datos en producción

1. **Subir datos al servidor:**
   - Copia la carpeta `data_export/` al servidor

2. **Importar en el servidor:**
   ```bash
   python sync_data.py
   # Selecciona opción 2: "Importar datos"
   ```

### Crear respaldos

Antes de sincronizar, siempre crea un respaldo:
```bash
python sync_data.py
# Selecciona opción 3: "Crear backup"
```

## 🖥️ Ejecutar el Servidor

### Desarrollo (local)
```bash
python app.py
```

### Producción (servidor)

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh          # Modo producción con Gunicorn
./start_server.sh dev       # Modo desarrollo
```

**Windows:**
```batch
start_server.bat           # Modo producción
start_server.bat dev        # Modo desarrollo
```

## 📁 Estructura de Archivos en Servidor

```
servidor/
├── app.py                    # Aplicación principal
├── models.py                 # Modelos de BD
├── .env                      # Config de producción (editado)
├── requirements.txt          # Dependencias
├── sync_data.py             # Script de sincronización
├── deploy.py                # Script de despliegue
├── init_users.py            # Crear usuarios iniciales
├── start_server.sh/.bat     # Scripts de inicio
├── gunicorn.conf.py         # Config del servidor web
├── templates/               # Templates HTML
├── static/                  # Archivos estáticos
├── migrations/              # Migraciones de BD
├── instance/
│   └── floristeria_production.db  # BD de producción
├── data_export/             # Datos para importar (temporal)
├── backups/                 # Respaldos automáticos
└── logs/                    # Logs del servidor
```

## ⚙️ Configuración Importante

### Variables de Entorno (.env)

**¡IMPORTANTE!** Modifica estos valores en producción:

```bash
# ¡CAMBIAR EN PRODUCCIÓN!
SECRET_KEY=CLAVE_UNICA_Y_SEGURA_AQUI

# Contraseñas seguras
DEFAULT_ADMIN_PASS=CONTRASEÑA_ADMIN_SEGURA
DEFAULT_USER_PASS=CONTRASEÑA_USUARIO_SEGURA

# Configuración del servidor
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Base de datos de producción
DATABASE_URL=sqlite:///floristeria_production.db
```

### Seguridad
- Cambia `SECRET_KEY` por una clave aleatoria única
- Usa contraseñas fuertes para los usuarios por defecto
- Configura `FLASK_DEBUG=false` en producción
- Considera usar HTTPS en producción

## 🔄 Workflow de Desarrollo a Producción

### 1. Desarrollo Local
- Trabaja normalmente en tu aplicación local
- Sube fotos, crea usuarios, registra horarios, etc.
- La BD local (`floristeria.db`) mantiene todos tus datos

### 2. Preparar Sincronización
```bash
# En local - exportar datos
python sync_data.py
# Opción 1: Exportar datos
```

### 3. Subir al Servidor
- Copia la carpeta `data_export/` al servidor
- Sube cualquier archivo nuevo o modificado

### 4. Actualizar Producción
```bash
# En servidor - crear backup primero
python sync_data.py
# Opción 3: Crear backup

# Luego importar datos nuevos
python sync_data.py
# Opción 2: Importar datos
```

### 5. Reiniciar Servidor
```bash
# Reiniciar la aplicación
./start_server.sh
```

## 🛠️ Solución de Problemas

### Error: "No se encontró .env"
- Asegúrate de haber ejecutado `python deploy.py` en el servidor
- Verifica que `.env.production` fue copiado correctamente

### Error: "Base de datos no existe"
- Ejecuta `python -m flask db upgrade` 
- Luego `python init_users.py`

### Error: "Puerto en uso"
- Cambia `FLASK_PORT` en `.env`
- O detén el proceso que usa el puerto

### Error: "Permisos denegados"
- En Linux: `chmod +x start_server.sh`
- Verifica permisos de carpetas: `chmod 755 static/ templates/`

### Problemas de importación de datos
- Verifica que la carpeta `data_export/` existe
- Asegúrate de que los archivos JSON no están corruptos
- Crea un backup antes de importar

## 📊 Monitoreo

### Logs del Servidor
```bash
# Ver logs en tiempo real
tail -f logs/access.log
tail -f logs/error.log
```

### Estado de la Base de Datos
```bash
# Verificar datos importados
python -c "
from app import app
from models import User, Photo, TimeEntry
with app.app_context():
    print(f'Usuarios: {User.query.count()}')
    print(f'Fotos: {Photo.query.count()}')
    print(f'Fichajes: {TimeEntry.query.count()}')
"
```

## 🔄 Actualizaciones Futuras

### Para actualizar código:
1. Desarrolla y prueba localmente
2. Sube archivos modificados al servidor
3. Reinicia el servidor: `./start_server.sh`

### Para sincronizar datos:
1. Exporta desde local: `python sync_data.py` → opción 1
2. Sube `data_export/` al servidor
3. Importa en servidor: `python sync_data.py` → opción 2

## 💾 Respaldos Automatizados

Programa respaldos automáticos en el servidor:

```bash
# Agregar al crontab (Linux)
crontab -e

# Backup diario a las 2 AM
0 2 * * * cd /ruta/al/proyecto && python sync_data.py <<< "3"
```

## 🎯 Resumen Rápido

**Para desplegar por primera vez:**
1. `python deploy.py` → opción 3 (crear paquete)
2. Subir y descomprimir en servidor
3. `python deploy.py` → opción 1 (configurar producción)
4. Editar `.env` con configuraciones seguras
5. `./start_server.sh`

**Para sincronizar datos regularmente:**
1. Local: `python sync_data.py` → opción 1
2. Subir `data_export/` al servidor  
3. Servidor: `python sync_data.py` → opción 2

**¡Listo para producción!** 🚀
