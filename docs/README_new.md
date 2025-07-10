# Calendario Floristería Raquel

Sistema integral de gestión para floristería con calendario, control horario y gestión de documentos.

## Características Principales

### 📅 Calendario y Fotos
- **Calendario visual** para navegar por meses
- **Subida múltiple de fotos** para cada día (requiere login)
- **Galería de fotos** con vista previa en el calendario
- **Vista ampliada** de fotos en modal
- **Sistema de estados** - marca fotos como Pendiente/Hecho/Entregado
- **Indicadores visuales** - contadores de estado por día
- **Optimización automática** de imágenes
- **Eliminar fotos** individualmente (solo usuarios autenticados)

### 👤 Sistema de Usuarios
- **Autenticación segura** con contraseñas hasheadas
- **Roles de usuario** (Administrador/Usuario regular)
- **Gestión de usuarios** (solo administradores)
- **Cambio de contraseñas** individual
- **Activación/desactivación** de usuarios

### ⏰ Control Horario (Fichaje)
- **Fichar entrada y salida** diaria
- **Control de descansos** (inicio/fin)
- **Cálculo automático** de horas trabajadas
- **Historial personal** de fichajes
- **Estados de jornada** (Activo/Completado/Ausente)

### 📄 Gestión de Documentos
- **Subida de documentos** personales (justificantes, contratos, etc.)
- **Categorización** por tipo de documento
- **Descripción y fecha** relacionada
- **Descarga segura** de documentos
- **Eliminación** de documentos propios

### 📊 Reportes y Administración
- **Reportes de horarios** (solo administradores)
- **Filtrado por usuario** y rango de fechas
- **Exportación a CSV** de reportes
- **Panel de gestión** de usuarios

### 🎨 Interfaz de Usuario
- **Sidebar fijo** con iconos intuitivos
- **Diseño responsive** optimizado para móviles y tablets
- **Indicadores visuales** claros y distintivos
- **Navegación intuitiva** entre funciones

## Base de Datos

El sistema utiliza **SQLite** con **SQLAlchemy** y **Flask-Migrate** para la gestión de la base de datos:

### Tablas principales:
- **users** - Información de usuarios y credenciales
- **photos** - Fotos subidas por fecha con estados
- **time_entries** - Registros de fichaje y control horario
- **user_documents** - Documentos personales de usuarios

## Estados de las fotos

- **⏳ Pendiente** (Amarillo) - Estado inicial de todas las fotos
- **✓ Hecho** (Azul) - Trabajo completado  
- **📦 Entregado** (Verde) - Entregado al cliente

## Usuarios por defecto

La aplicación viene con dos usuarios preconfigurados:

- **admin** / admin123 (puede crear nuevos usuarios)
- **usuario** / usuario123 (usuario regular)

**Importante:** Solo el usuario `admin` puede crear nuevos usuarios.

## Instalación

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
   source .venv/bin/activate  # En Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno (opcional):**
   - La aplicación viene con un archivo `.env` con valores por defecto
   - Puedes modificar `.env` para personalizar la configuración:
     - Cambiar las contraseñas por defecto
     - Modificar el puerto de la aplicación
     - Cambiar el nombre de la aplicación
     - Ajustar límites de archivos
   - Para seguridad en producción, **cambia obligatoriamente `SECRET_KEY`**

5. **Inicializar la base de datos:**
   ```bash
   python -m flask db upgrade
   python init_users.py  # Crear usuarios por defecto
   ```

## Configuración mediante Variables de Entorno

La aplicación se puede configurar mediante el archivo `.env` incluido. Las principales variables son:

```bash
# Configuración de seguridad (¡CAMBIAR EN PRODUCCIÓN!)
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_cambiar_en_produccion

# Configuración de la aplicación
APP_NAME=Floristería Raquel
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Configuración de usuarios por defecto
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASS=admin123
DEFAULT_USER_USER=usuario
DEFAULT_USER_PASS=usuario123

# Configuración de archivos
MAX_FILE_SIZE=16777216  # 16MB en bytes
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,pdf,doc,docx

# Base de datos
DATABASE_URL=sqlite:///floristeria.db
```

**Importante para producción:**
- Cambia `SECRET_KEY` por una clave segura única
- Cambia las contraseñas por defecto (`DEFAULT_ADMIN_PASS`, `DEFAULT_USER_PASS`)
- Configura `FLASK_DEBUG=false` en producción

## Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: http://localhost:5000

## Funcionalidades

### 1. Autenticación
- **Acceso requerido**: Todas las funciones requieren estar autenticado
- **Iniciar sesión**: Usa uno de los usuarios por defecto
- **Crear usuarios**: Solo el usuario `admin` puede crear nuevos usuarios
- **Cerrar sesión**: Usa el botón en la sidebar

### 2. Calendario y Fotos
- Navega entre meses usando los botones "Anterior" y "Siguiente"
- Cada día muestra contadores de fotos por estado (pendiente/hecho/entregado)
- Haz clic en un día para ver/subir fotos
- **Estados de fotos**: Cambia entre Pendiente → Hecho → Entregado
- **Eliminar fotos**: Solo el usuario que las subió puede eliminarlas

### 3. Control Horario (Fichaje)
- **Fichar entrada**: Registra el inicio de la jornada laboral
- **Fichar salida**: Registra el fin de la jornada
- **Descansos**: Inicia y finaliza períodos de descanso
- **Historial**: Ve tus registros de los últimos 7 días
- **Cálculo automático**: Las horas se calculan automáticamente

### 4. Gestión de Documentos
- **Subir documentos**: Justificantes, contratos, nóminas, etc.
- **Categorizar**: Organiza por tipo de documento
- **Descargar**: Descarga tus documentos cuando los necesites
- **Eliminar**: Elimina documentos que ya no necesites

### 5. Reportes (Solo Administradores)
- **Ver todos los fichajes**: Filtrar por usuario y fechas
- **Exportar CSV**: Descargar reportes para análisis externo
- **Gestión de usuarios**: Crear, modificar y desactivar usuarios

## Estructura del Proyecto

```
CalendarFloristeriaRaquel/
├── app.py                    # Aplicación principal
├── models.py                 # Modelos de la base de datos
├── init_users.py            # Script para crear usuarios iniciales
├── requirements.txt         # Dependencias de Python
├── README.md               # Este archivo
├── .env                    # Variables de entorno
├── .env.example           # Ejemplo de variables de entorno
├── migrations/            # Migraciones de la base de datos
├── instance/
│   └── floristeria.db    # Base de datos SQLite
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── calendar.html     # Vista del calendario
│   ├── day.html          # Vista de fotos del día
│   ├── upload.html       # Formulario de subida de fotos
│   ├── login.html        # Página de login
│   ├── time_tracking.html   # Control horario personal
│   ├── time_reports.html    # Reportes (admin)
│   ├── upload_document.html # Subir documentos
│   ├── my_documents.html    # Ver documentos personales
│   ├── manage_users.html    # Gestión de usuarios (admin)
│   ├── register.html        # Crear usuario (admin)
│   └── change_password.html # Cambiar contraseña
├── static/              # Archivos estáticos
│   ├── css/
│   │   └── style.css    # Estilos CSS personalizados
│   ├── uploads/         # Fotos subidas (se crea automáticamente)
│   │   └── YYYY-MM-DD/  # Carpetas por fecha
│   └── documents/       # Documentos subidos (se crea automáticamente)
│       └── {user_id}/   # Carpetas por usuario
└── .venv/              # Entorno virtual de Python
```

## Tecnologías Utilizadas

### Backend
- **Flask** - Framework web de Python
- **SQLAlchemy** - ORM para base de datos
- **Flask-Migrate** - Migraciones de base de datos
- **Flask-Login** - Gestión de sesiones de usuario
- **Werkzeug** - Utilidades web (hashing de contraseñas)
- **Pillow** - Procesamiento de imágenes
- **python-dotenv** - Gestión de variables de entorno

### Frontend
- **Bootstrap 5** - Framework CSS para diseño responsive
- **Font Awesome** - Iconos
- **JavaScript** - Interactividad del frontend

### Base de Datos
- **SQLite** - Base de datos ligera y sin configuración

## Características Técnicas

- **Seguridad**: 
  - Contraseñas hasheadas con Werkzeug
  - Validación de tipos de archivo
  - Nombres de archivo seguros
  - Control de acceso basado en roles

- **Optimización**: 
  - Redimensionamiento automático de imágenes
  - Compresión de imágenes para ahorrar espacio
  - Estructura eficiente de carpetas

- **Responsive**: 
  - Sidebar adaptativo
  - Diseño móvil optimizado
  - Botones táctiles grandes

- **Base de datos**:
  - Migraciones automáticas
  - Relaciones entre tablas
  - Índices para rendimiento

## Migración desde JSON a SQL

El sistema ha migrado de almacenamiento en archivos JSON a base de datos SQL. Si tienes datos antiguos:

1. Los archivos `users.json` y datos de fotos antiguos se conservan como respaldo
2. La nueva estructura SQL es más robusta y escalable
3. Se mantiene compatibilidad con la estructura de archivos de fotos existente

## Personalización

Puedes personalizar fácilmente:

- **Colores y estilos**: Modifica `static/css/style.css`
- **Nombre de la aplicación**: Cambia `APP_NAME` en `.env`
- **Límites de archivos**: Ajusta `MAX_FILE_SIZE` en `.env`
- **Tipos de archivo permitidos**: Modifica `ALLOWED_EXTENSIONS` en `.env`
- **Configuración de base de datos**: Cambia `DATABASE_URL` en `.env`

## Desarrollo

Para contribuir al desarrollo:

1. Fork el proyecto
2. Crea una rama para tu función: `git checkout -b nueva-funcion`
3. Commit tus cambios: `git commit -am 'Agregar nueva función'`
4. Push a la rama: `git push origin nueva-funcion`
5. Crea un Pull Request

## Licencia

Este proyecto es de uso libre para la Floristería Raquel.

## Soporte

Para reportar problemas o solicitar nuevas funciones, por favor crea un issue en el repositorio del proyecto.
