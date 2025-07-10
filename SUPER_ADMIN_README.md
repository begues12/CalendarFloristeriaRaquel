# Sistema de Super Administrador

## Descripción

El sistema de super administrador permite actualizar automáticamente la aplicación desde el repositorio git, ejecutar migraciones de base de datos y gestionar el modo mantenimiento, todo sin afectar los datos de los usuarios.

## Características

### 🔐 Permisos de Super Admin
- Solo usuarios con `is_super_admin = True` pueden acceder a estas funcionalidades
- Los super admins también tienen permisos de administrador normal
- Acceso al panel especial desde la sidebar (icono de corona dorada)

### 🛠️ Modo Mantenimiento
- **Activación manual**: Permite activar el modo mantenimiento con mensaje personalizado y duración estimada
- **Activación automática**: Se activa automáticamente durante las actualizaciones del sistema
- **Acceso restringido**: Solo los super admins pueden acceder durante el mantenimiento
- **Página de mantenimiento**: Los usuarios ven una página informativa durante el mantenimiento

### 🔄 Actualización del Sistema
- **Git pull**: Descarga la última versión del código desde el repositorio
- **Instalación de dependencias**: Ejecuta `pip install -r requirements.txt`
- **Migraciones**: Aplica automáticamente las migraciones pendientes con `flask db upgrade`
- **Logs detallados**: Registra todo el proceso de actualización con timestamps
- **Rollback automático**: En caso de error, mantiene el estado anterior

### 📊 Monitoreo
- **Estado del sistema**: Visualización del estado actual de mantenimiento
- **Información Git**: Branch actual, commit, último mensaje
- **Historial de actualizaciones**: Log completo de todas las actualizaciones realizadas
- **Verificación de actualizaciones**: Comprueba si hay nuevas versiones disponibles

## Uso

### Asignar Permisos de Super Admin

Usa el script `manage_super_admin.py`:

```bash
# Convertir un usuario en super admin
python manage_super_admin.py add username

# Remover permisos de super admin
python manage_super_admin.py remove username

# Listar todos los super admins
python manage_super_admin.py list
```

### Acceso al Panel

1. Inicia sesión con un usuario que tenga permisos de super admin
2. En la sidebar aparecerá el icono de corona dorada
3. Haz click para acceder al "Panel Super Admin"

### Activar Modo Mantenimiento

1. Ve al Panel Super Admin
2. En la sección "Control de Mantenimiento":
   - Escribe un mensaje personalizado
   - Establece la duración estimada en minutos
   - Haz click en "Activar Mantenimiento"

### Actualizar el Sistema

1. Ve al Panel Super Admin
2. En la sección "Actualización del Sistema":
   - (Opcional) Haz click en "Verificar Actualizaciones" para ver si hay nuevas versiones
   - Haz click en "Actualizar Sistema"
   - Confirma la acción en el diálogo
   - Espera a que termine el proceso

### Durante la Actualización

1. **Se activa automáticamente el modo mantenimiento**
2. **Los usuarios normales ven la página de mantenimiento**
3. **Solo los super admins pueden continuar usando el sistema**
4. **El proceso se registra en el historial**
5. **Al finalizar, se desactiva automáticamente el mantenimiento**

## Archivos y Rutas

### Nuevos Modelos
- `MaintenanceMode`: Gestiona el estado de mantenimiento
- `UpdateLog`: Registra el historial de actualizaciones

### Nuevas Rutas
- `/super_admin_panel`: Panel principal de super admin
- `/toggle_maintenance`: Activar/desactivar mantenimiento
- `/update_system`: Ejecutar actualización del sistema
- `/check_updates`: Verificar actualizaciones disponibles
- `/update_log/<id>`: Ver detalles de una actualización

### Nuevas Plantillas
- `super_admin_panel.html`: Panel principal
- `maintenance.html`: Página mostrada durante mantenimiento
- `update_log_detail.html`: Detalles de una actualización

### Middleware
- Verificación de modo mantenimiento en cada request
- Redirección automática a página de mantenimiento

## Seguridad

### Protecciones
- **Autenticación requerida**: Solo usuarios autenticados
- **Autorización específica**: Solo super admins
- **Verificación en cada request**: Middleware de seguridad
- **Logs auditables**: Registro de todas las acciones

### Datos Protegidos
- **Base de datos**: Las migraciones solo añaden/modifican estructura, nunca eliminan datos
- **Archivos de usuario**: Los uploads y documentos no se ven afectados
- **Configuración**: Los datos de configuración se mantienen

## Comandos de Git Utilizados

```bash
# Obtener actualizaciones
git fetch

# Verificar si hay cambios
git rev-list --count HEAD..origin/main

# Actualizar código
git pull origin main

# Información del repositorio
git rev-parse HEAD              # Commit actual
git rev-parse --abbrev-ref HEAD # Branch actual
git log -1 --pretty=%s          # Último mensaje de commit
```

## Dependencias

El sistema utiliza:
- **subprocess**: Para ejecutar comandos git y pip
- **flask_login**: Para autenticación y autorización
- **flask_migrate**: Para migraciones de base de datos
- **sqlite3**: Base de datos (configurable)

## Troubleshooting

### Error en Git Pull
- Verificar que el directorio sea un repositorio git válido
- Comprobar conectividad a internet
- Verificar permisos de escritura en el directorio

### Error en Migraciones
- Verificar que no haya conflictos en la base de datos
- Comprobar que Flask-Migrate esté configurado correctamente
- Revisar los logs de error en el panel

### Modo Mantenimiento "Stuck"
Si el modo mantenimiento queda activo accidentalmente:

```python
# En la consola de Python/Flask
from models import MaintenanceMode, db
maintenance = MaintenanceMode.get_current()
maintenance.deactivate()
```

### Restaurar Backup
En caso de problema severo, restaurar desde backup:

```bash
# Si tienes backups automáticos
cp backups/floristeria_YYYY-MM-DD.db instance/floristeria.db
```

## Mejoras Futuras

- [ ] Backups automáticos antes de cada actualización
- [ ] Notificaciones por email de actualizaciones
- [ ] Integración con webhooks de GitHub
- [ ] Rollback automático en caso de error
- [ ] Métricas de rendimiento del sistema
- [ ] Programación de mantenimientos
