# Panel de Configuración de Base de Datos

## Descripción

Se ha implementado un panel completo de gestión de base de datos dentro del panel de **Super Administrador**, que permite a los usuarios con privilegios de super admin:

- **Cambiar entre motores de base de datos** (SQLite ↔ MySQL)
- **Realizar backups** de los datos
- **Probar conexiones** a la base de datos
- **Editar configuraciones** de conexión

## Acceso

1. **Iniciar sesión** como super administrador
2. Ir al **Panel de Super Administrador**
3. En la sección "**Gestión de Base de Datos**", hacer clic en "**Configurar Base de Datos**"

## Funcionalidades Implementadas

### 1. Estado Actual de la Base de Datos
- **Tipo de motor**: MySQL o SQLite
- **Estado de conexión**: Conectado/Error
- **Número de tablas**: Contador de tablas en la BD
- **Mensajes de error**: Si hay problemas de conexión

### 2. Cambio de Motor de Base de Datos
- **Formulario intuitivo** para seleccionar:
  - SQLite (archivo local)
  - MySQL (servidor remoto)
- **Configuración automática** de parámetros según el tipo elegido
- **Validación de conexión** antes del cambio

### 3. Configuración de MySQL
- **Host/Servidor**
- **Puerto** (por defecto: 3306)
- **Nombre de base de datos**
- **Usuario**
- **Contraseña**
- **Configuraciones avanzadas** (charset, pool de conexiones, etc.)

### 4. Configuración de SQLite
- **Ruta del archivo** de base de datos
- **Creación automática** si no existe

### 5. Backup y Migración
- **Backup automático** antes de cambiar de motor
- **Exportación de datos** en formato JSON
- **Verificación de integridad** de los datos

### 6. Prueba de Conexión
- **Test de conectividad** sin afectar la configuración actual
- **Validación de credenciales**
- **Información detallada** sobre el estado de la conexión

## Archivos Afectados

### Templates
- `app/templates/super_admin_panel.html` - Añadida sección de gestión de BD
- `app/templates/database_config.html` - Panel principal de configuración

### Rutas y Lógica
- `app/blueprints/admin/routes.py` - Rutas para gestión de BD:
  - `/database_config` - Panel principal
  - `/switch_database` - Cambio de motor
  - `/test_database_connection` - Prueba de conexión
  - `/backup_database` - Backup de datos

### Configuración
- `config/settings.py` - Configuración de BD basada en variables de entorno
- `.env.production` - Variables de entorno para producción
- `.env.example` - Ejemplo de configuración

## Variables de Entorno Soportadas

```bash
# Base de datos
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/floristeria
DEV_DATABASE_URL=sqlite:///floristeria_dev.db

# Configuración MySQL
MYSQL_CHARSET=utf8mb4
MYSQL_COLLATION=utf8mb4_unicode_ci

# Pool de conexiones
SQLALCHEMY_POOL_RECYCLE=300
SQLALCHEMY_POOL_TIMEOUT=20
SQLALCHEMY_POOL_SIZE=5
SQLALCHEMY_MAX_OVERFLOW=0
SQLALCHEMY_ECHO=False
```

## Seguridad

- **Solo super administradores** pueden acceder
- **Backup automático** antes de cambios críticos
- **Validación de configuración** antes de aplicar
- **Rollback automático** en caso de error
- **Logs detallados** de todas las operaciones

## Uso Recomendado

1. **Desarrollo**: Usar SQLite para facilidad
2. **Producción**: Migrar a MySQL para mejor rendimiento
3. **Testing**: Usar bases de datos en memoria
4. **Backup regular**: Programar backups automáticos

## Próximas Mejoras

- [ ] Programación de backups automáticos
- [ ] Migración de datos más robusta
- [ ] Soporte para PostgreSQL
- [ ] Interface de restauración de backups
- [ ] Monitorización de rendimiento de BD
- [ ] Alertas de espacio en disco
