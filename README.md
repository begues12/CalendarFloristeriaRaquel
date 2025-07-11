# Floristería Raquel - Sistema de Gestión

Sistema integral de gestión para floristería con calendario, control de horarios, gestión de documentos y sistema de privilegios granular.

## ✅ Estado del Proyecto

**PROYECTO COMPLETAMENTE REORGANIZADO Y FUNCIONAL**

- ✅ Estructura modular implementada
- ✅ Sistema de privilegios granular funcionando
- ✅ Flask-Migrate integrado correctamente
- ✅ Scripts de gestión disponibles
- ✅ Base de datos inicializada
- ✅ Todos los comandos `flask db` disponibles

## Estructura del Proyecto

```
CalendarFloristeriaRaquel/
├── app/                          # Aplicación principal
│   ├── __init__.py              # Factory de la aplicación
│   ├── models/                  # Modelos de datos
│   │   ├── __init__.py
│   │   └── user.py             # Modelos de usuario y relacionados
│   ├── blueprints/             # Módulos de la aplicación
│   │   ├── auth/               # Autenticación
│   │   ├── calendar/           # Gestión de calendario
│   │   ├── time_tracking/      # Control de horarios
│   │   ├── documents/          # Gestión de documentos
│   │   ├── admin/              # Panel administrativo
│   │   └── users/              # Gestión de usuarios
│   ├── static/                 # Archivos estáticos
│   ├── templates/              # Plantillas HTML
│   └── utils/                  # Utilidades comunes
├── config/                     # Configuración
│   ├── __init__.py
│   └── settings.py            # Configuraciones de entorno
├── scripts/                   # Scripts de utilidad
├── tests/                     # Pruebas
├── docs/                      # Documentación
├── migrations/                # Migraciones de base de datos
├── instance/                  # Datos de instancia
├── run.py                     # Punto de entrada desarrollo
├── wsgi.py                    # Punto de entrada producción
├── flask-cmd.bat              # Helper para comandos Flask (Windows)
└── requirements.txt           # Dependencias
```

## Instalación y Configuración

### Bases de Datos Soportadas

Este proyecto soporta tanto **SQLite** (por defecto) como **MySQL**:

- **SQLite**: Ideal para desarrollo y aplicaciones pequeñas
- **MySQL**: Recomendado para producción y múltiples usuarios concurrentes

#### Migración a MySQL

Para usar MySQL en lugar de SQLite, sigue estos pasos:

**Opción 1: Configuración Automática (Recomendada)**
```bash
# Windows
setup_mysql.bat

# Linux/Mac
python scripts/setup_mysql.py
```

**Opción 2: Configuración Manual**
1. Instalar MySQL Server
2. Instalar dependencias: `pip install PyMySQL cryptography`
3. Crear archivo `.env` con configuración MySQL
4. Ejecutar: `python scripts/setup_mysql.py`

📖 **Documentación completa**: [docs/MYSQL_MIGRATION.md](docs/MYSQL_MIGRATION.md)

### Requisitos Previos
- Python 3.8+
- pip
- virtualenv (recomendado)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd CalendarFloristeriaRaquel
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno** (opcional)
   ```bash
   cp .env.example .env
   # Editar .env con tu configuración
   ```

5. **Inicializar base de datos**
   ```bash
   python run.py
   ```

## Ejecución

### Desarrollo
```bash
python run.py
```

### Usando Flask CLI
```bash
# Windows (usando el helper)
flask-cmd.bat run

# Linux/Mac
FLASK_APP=run.py flask run --debug
```

### Producción (con Gunicorn)
```bash
gunicorn -c scripts/gunicorn.conf.py wsgi:application
```

### Usando VS Code
Utiliza la tarea configurada: `Ctrl+Shift+P` → "Tasks: Run Task" → "Ejecutar Calendario Flask"

## Gestión de Base de Datos

### Panel de Configuración (Super Admin)

El sistema incluye un **panel de configuración de base de datos** completo accesible desde el Panel de Super Administrador:

#### 🔧 Funcionalidades Disponibles
- **Cambio de motor**: Migración entre SQLite ↔ MySQL
- **Configuración en tiempo real**: Edita configuraciones sin reiniciar
- **Backup automático**: Respaldo antes de cambios críticos
- **Prueba de conexión**: Valida configuraciones antes de aplicar
- **Monitor de estado**: Estado actual y estadísticas de la BD

#### 📖 Acceso al Panel
1. Iniciar sesión como **Super Administrador**
2. Ir a **Panel de Super Administrador**
3. Sección "**Gestión de Base de Datos**"
4. Clic en "**Configurar Base de Datos**"

#### 🗃️ Tipos Soportados
- **SQLite**: Ideal para desarrollo y despliegues pequeños
- **MySQL**: Recomendado para producción y múltiples usuarios

#### ⚙️ Variables de Entorno
```bash
# Configuración principal
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/floristeria
DEV_DATABASE_URL=sqlite:///floristeria_dev.db

# Configuración MySQL
MYSQL_CHARSET=utf8mb4
MYSQL_COLLATION=utf8mb4_unicode_ci

# Pool de conexiones
SQLALCHEMY_POOL_RECYCLE=300
SQLALCHEMY_POOL_SIZE=5
```

### Comandos Flask-Migrate

```bash
# Verificar estado actual
flask-cmd.bat db current

# Ver historial de migraciones
flask-cmd.bat db history

# Verificar cambios pendientes
flask-cmd.bat db check

# Crear nueva migración
flask-cmd.bat db migrate -m "descripción"

# Aplicar migraciones
flask-cmd.bat db upgrade
```

### Scripts Alternativos

```bash
# Verificar estado de BD
python scripts/init_database.py --check

# Inicializar BD (si es necesario)
python scripts/init_database.py --init

# Resetear BD completamente (¡CUIDADO!)
python scripts/init_database.py --reset
```

## Gestión de Super Administradores

```bash
# Crear nuevo super admin
python scripts/manage_super_admin.py create <username>

# Promover usuario existente
python scripts/manage_super_admin.py add <username>

# Listar super admins
python scripts/manage_super_admin.py list

# Usuario de emergencia
python scripts/manage_super_admin.py create-emergency

# Ayuda completa
python scripts/manage_super_admin.py help
```

## Funcionalidades

### Sistema de Privilegios Granular
- **Gestión de usuarios**: Crear, editar y eliminar usuarios
- **Control de acceso**: Privilegios específicos por funcionalidad
- **Roles**: Admin, Super Admin y usuarios regulares
- **Perfiles de usuario**: Información personal y profesional

### Módulos Principales

#### 📅 Calendario
- Vista mensual y diaria
- Subida y gestión de fotos por día
- Estado de actividades (completado, pendiente, etc.)

#### ⏰ Control de Horarios
- Fichaje de entrada y salida
- Gestión de descansos
- Reportes de horarios personales y generales
- Exportación de datos

#### 📁 Gestión de Documentos
- Subida de documentos personales
- Administración centralizada de documentos
- Control de acceso por privilegios

#### 👥 Administración
- Panel de super administración
- **🆕 Configuración de Base de Datos**: Cambio entre SQLite y MySQL
- **🆕 Consola Administrativa**: Ejecutar comandos del sistema de forma segura
- **🆕 Gestor de Base de Datos**: Administración avanzada, consultas SQL, optimización
- Modo mantenimiento
- Actualizaciones del sistema
- Gestión de usuarios y privilegios

## Arquitectura

### Patrón Application Factory
La aplicación utiliza el patrón Factory para crear instancias configurables de Flask.

### Blueprints Modulares
Cada funcionalidad está organizada en blueprints independientes para mejor mantenibilidad.

### Sistema de Privilegios
Control granular de acceso basado en privilegios específicos:
- `can_view_calendar`
- `can_time_tracking`
- `can_view_own_documents`
- `can_view_all_documents`
- `can_manage_users`
- `can_view_own_reports`
- `can_view_all_reports`

## Documentación

Consulta la carpeta `docs/` para documentación detallada:
- `MIGRACIONES.md` - Guía completa de migraciones
- `MYSQL_MIGRATION.md` - Migración específica a MySQL
- **`DATABASE_CONFIG_PANEL.md`** - Guía del panel de configuración de BD
- `PRIVILEGIOS_SISTEMA.md` - Guía de privilegios del sistema
- `TROUBLESHOOTING.md` - Solución de problemas
- `DEPLOY.md` - Documentación de despliegue

## Scripts Disponibles

- `scripts/init_database.py` - Inicializar/verificar base de datos
- `scripts/manage_super_admin.py` - Gestión de super administradores
- `flask-cmd.bat` - Helper para comandos Flask en Windows

## Usuarios por Defecto

Después de la inicialización:
- **Admin**: `admin` / `admin123`
- **Usuario**: `raquel` / `raquel123`

⚠️ **Importante**: Cambia las contraseñas por defecto en producción.

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto es privado y está destinado únicamente para uso interno de Floristería Raquel.

## Contacto

Para soporte técnico, consulta la documentación en `docs/TROUBLESHOOTING.md`.