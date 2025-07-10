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