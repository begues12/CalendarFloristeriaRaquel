# Floristería Raquel - Calendario y Gestión

## Estructura Modular Refactorizada

El proyecto ha sido refactorizado para usar una estructura modular con blueprints de Flask, organizando las rutas en módulos separados para mejor mantenibilidad y escalabilidad.

### Estructura del Proyecto

```
CalendarFloristeriaRaquel/
├── app.py                 # Aplicación principal con configuración
├── models.py             # Modelos de base de datos
├── requirements.txt      # Dependencias del proyecto
├── rutas/               # Módulo de rutas modularizadas
│   ├── __init__.py      # Registro de blueprints
│   ├── auth.py          # Autenticación (login, logout, cambio contraseña)
│   ├── calendar.py      # Calendario y fotos (vista calendario, días, fotos)
│   ├── users.py         # Gestión de usuarios (crear, editar, eliminar)
│   ├── time_tracking.py # Control horario (fichaje, reportes)
│   ├── documents.py     # Documentos personales (subir, descargar)
│   └── admin.py         # Administración (gestión documentos)
├── templates/           # Plantillas HTML
├── static/             # Archivos estáticos (CSS, JS, imágenes)
├── migrations/         # Migraciones de base de datos
└── instance/           # Base de datos SQLite
```

### Blueprints Organizados

#### 1. **auth.py** - Autenticación
- `auth.login` - Página de inicio de sesión
- `auth.logout` - Cerrar sesión
- `auth.force_change_password` - Cambio obligatorio de contraseña

#### 2. **calendar.py** - Calendario y Fotos
- `calendar.index` - Vista principal del calendario
- `calendar.view_day` - Ver fotos de un día específico
- `calendar.upload_photo` - Subir fotos para un día
- `calendar.update_photo_status` - Actualizar estado de foto
- `calendar.change_status` - Cambiar estado de foto (GET)
- `calendar.delete_photo` - Eliminar foto

#### 3. **users.py** - Gestión de Usuarios
- `users.register` - Crear nuevo usuario (solo admin)
- `users.manage_users` - Lista y gestión de usuarios
- `users.toggle_user_status` - Activar/desactivar usuario
- `users.change_password` - Cambiar contraseña propia
- `users.change_password` - Cambiar contraseña de cualquier usuario (admin)
- `users.delete_user` - Eliminar usuario (admin)

#### 4. **time_tracking.py** - Control Horario
- `time_tracking.time_tracking` - Panel personal de fichaje
- `time_tracking.clock_in` - Fichar entrada
- `time_tracking.clock_out` - Fichar salida
- `time_tracking.break_start` - Iniciar descanso
- `time_tracking.break_end` - Finalizar descanso
- `time_tracking.time_reports` - Reportes de horarios (admin)
- `time_tracking.export_time_report` - Exportar reporte CSV
- `time_tracking.edit_time_entry` - Editar registro de tiempo
- `time_tracking.delete_time_entry` - Eliminar registro
- `time_tracking.create_time_entry` - Crear nuevo registro

#### 5. **documents.py** - Documentos Personales
- `documents.upload_document` - Subir documento personal
- `documents.my_documents` - Ver documentos propios
- `documents.download_document` - Descargar documento propio
- `documents.delete_document` - Eliminar documento propio

#### 6. **admin.py** - Administración
- `admin.admin_documents` - Ver todos los documentos
- `admin.admin_download_document` - Descargar cualquier documento
- `admin.admin_delete_document` - Eliminar cualquier documento

### Características Principales

1. **Autenticación y Autorización**
   - Sistema de login/logout seguro
   - Roles de usuario (admin/usuario normal)
   - Cambio obligatorio de contraseña en primer acceso
   - Middleware de verificación de contraseña

2. **Calendario Interactivo**
   - Vista mensual con navegación
   - Subida múltiple de fotos por día
   - Estados de trabajo (pendiente, hecho, entregado)
   - Contadores de estado por día

3. **Control Horario**
   - Fichaje de entrada/salida
   - Control de descansos
   - Reportes detallados para administradores
   - Exportación a CSV
   - Edición/creación manual de registros

4. **Gestión de Documentos**
   - Documentos personales por usuario
   - Categorización (médico, justificante, etc.)
   - Gestión administrativa completa
   - Descarga segura de archivos

5. **Panel de Administración**
   - Gestión completa de usuarios
   - Reportes de actividad
   - Control de documentos
   - Herramientas de configuración

### Tecnologías Utilizadas

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-Migrate
- **Frontend**: Bootstrap 5, Font Awesome, JavaScript
- **Base de Datos**: SQLite
- **Autenticación**: Flask-Login con hash de contraseñas
- **Migración**: Flask-Migrate con Alembic

### Instalación y Configuración

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno** (opcional):
   - Crear archivo `.env` con configuraciones personalizadas
   - Ver `app.py` para variables disponibles

3. **Ejecutar la aplicación**:
   ```bash
   python app.py
   ```

4. **Acceder a la aplicación**:
   - URL: http://localhost:5000
   - Usuario admin por defecto: `admin` / `admin123`
   - Usuario normal por defecto: `raquel` / `floreria2025`

### Seguridad y Configuración

- Cambiar la `SECRET_KEY` en producción
- Configurar base de datos PostgreSQL para producción
- Usar servidor WSGI (Gunicorn) en producción
- Configurar HTTPS y certificados SSL
- Ajustar límites de subida de archivos según necesidades

### Mantenimiento

- Las migraciones se ejecutan automáticamente
- Los usuarios por defecto se crean al iniciar por primera vez
- Logs de actividad disponibles en la consola
- Respaldos automáticos de base de datos (configurables)

---

Este proyecto ahora tiene una arquitectura modular que facilita:
- **Mantenimiento**: Cada funcionalidad en su propio módulo
- **Escalabilidad**: Fácil agregar nuevas funcionalidades
- **Colaboración**: Múltiples desarrolladores pueden trabajar en paralelo
- **Testing**: Cada módulo puede probarse independientemente
- **Despliegue**: Configuración centralizada y flexible
