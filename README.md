# Calend## Características

- 📅 **Calendario visual** para navegar por meses
- 📸 **Subida múltiple de fotos** para cada día (requiere login)
- 🖼️ **Galería de fotos** con vista previa en el calendario
- 🔍 **Vista ampliada** de fotos en modal
- 👤 **Sistema de usuarios** con registro y autenticación
- 📝 **Información de autoría** - cada foto muestra quién la subió y cuándo
- 🚦 **Sistema de estados** - marca fotos como Pendiente/Hecho/Entregado
- 🎨 **Indicadores visuales** - colores distintivos para cada estado
- � **Sidebar expansible** - navegación lateral que se puede contraer
- �📱 **Diseño responsive** optimizado para dispositivos móviles
- 🗑️ **Eliminar fotos** individualmente (solo usuarios autenticados)
- ⚡ **Optimización automática** de imágenes

## Interfaz de Usuario

### Sidebar Expansible
- **Desktop**: Sidebar lateral que se puede contraer/expandir con el botón de hamburguesa
- **Mobile**: Menú lateral que se desliza desde la izquierda
- **Navegación rápida**: Acceso directo a todas las funciones principales
- **Información de usuario**: Muestra el usuario actual y opción de cerrar sesión

## Estados de las fotos

- **⏳ Pendiente** (Amarillo) - Estado inicial de todas las fotos
- **✓ Hecho** (Azul) - Trabajo completado
- **📦 Entregado** (Verde) - Entregado al clientetería Raquel

Un calendario simple en Flask para subir y visualizar fotos por fecha.

# Calendario Floristería Raquel

Un calendario simple en Flask para subir y visualizar fotos por fecha con sistema de usuarios.

## Características

- 📅 **Calendario visual** para navegar por meses
- 📸 **Subida múltiple de fotos** para cada día (requiere login)
- 🖼️ **Galería de fotos** con vista previa en el calendario
- 🔍 **Vista ampliada** de fotos en modal
- 👤 **Sistema de usuarios** con registro y autenticación
- � **Información de autoría** - cada foto muestra quién la subió y cuándo
- �📱 **Diseño responsive** para móviles y tablets
- 🗑️ **Eliminar fotos** individualmente (solo usuarios autenticados)
- ⚡ **Optimización automática** de imágenes

## Usuarios por defecto

La aplicación viene con dos usuarios preconfigurados:

- **admin** / admin123 (puede crear nuevos usuarios)
- **raquel** / floreria2025 (usuario regular)

**Importante:** Solo el usuario `admin` puede crear nuevos usuarios.

## Instalación

1. **Clonar o descargar el proyecto**
2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno (opcional):**
   - La aplicación viene con un archivo `.env` con valores por defecto
   - Puedes modificar `.env` para personalizar la configuración:
     - Cambiar las contraseñas por defecto
     - Modificar el puerto de la aplicación
     - Cambiar el nombre de la aplicación
     - Ajustar límites de archivos
   - Para seguridad en producción, **cambia obligatoriamente `SECRET_KEY`**

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
DEFAULT_USER_USER=raquel
DEFAULT_USER_PASS=floreria2025

# Configuración de archivos
MAX_FILE_SIZE=16777216  # 16MB en bytes
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif
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

## Uso

### Autenticación
- **Acceso requerido**: Todas las funciones requieren estar autenticado
- **Iniciar sesión**: Usa uno de los usuarios por defecto
- **Crear usuarios**: Solo el usuario `admin` puede crear nuevos usuarios
- **Cerrar sesión**: Usa el botón en la barra de navegación

### Vista del Calendario
- **Requiere autenticación**: Debes estar logueado para acceder
- Navega entre meses usando los botones "Anterior" y "Siguiente"
- Cada día muestra miniaturas de las fotos subidas
- Usa los botones de cada día:
  - 👁️ Ver todas las fotos del día
  - ➕ Subir nuevas fotos

### Subir Fotos
- **Requiere estar logueado**
- Selecciona múltiples fotos a la vez
- Formatos soportados: JPG, PNG, GIF
- Tamaño máximo: 16MB por foto
- Las imágenes se redimensionan automáticamente
- Se guarda información del usuario que subió cada foto

### Ver Fotos
- **Requiere estar logueado**
- Haz clic en cualquier foto para verla en tamaño completo
- Cada foto muestra:
  - Nombre del archivo
  - Usuario que la subió
  - Fecha y hora de subida
  - **Estado actual** con indicador visual
- **Cambiar estado**: Usa los botones de color para cambiar entre Pendiente/Hecho/Entregado
- **Indicadores en calendario**: Las miniaturas muestran colores según su estado
- Elimina fotos individuales con el botón de basura
- Las fotos se organizan automáticamente por fecha

### Estados y Colores
- **🟡 Amarillo**: Pendiente - Trabajo por hacer
- **🔵 Azul**: Hecho - Trabajo completado
- **🟢 Verde**: Entregado - Entregado al cliente

### Optimizado para Móvil
- **Sidebar deslizable** en dispositivos móviles
- **Interfaz táctil** optimizada para dispositivos móviles
- **Botones grandes** fáciles de presionar en pantallas pequeñas
- **Layout adaptativo** que se reorganiza según el tamaño de pantalla
- **Navegación simplificada** con menú hamburguesa
- **Header móvil** con acceso rápido al menú lateral

### Gestión de Usuarios (Solo Admin)
- Solo el usuario `admin` puede crear nuevos usuarios
- Accede a "Crear Usuario" desde la barra de navegación
- Los usuarios regulares no pueden registrarse por sí mismos

## Estructura del Proyecto

```
CalendarFloristeriaRaquel/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── README.md             # Este archivo
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── calendar.html     # Vista del calendario
│   ├── day.html          # Vista de fotos del día
│   └── upload.html       # Formulario de subida
├── static/              # Archivos estáticos
│   ├── css/
│   │   └── style.css    # Estilos CSS
│   └── uploads/         # Fotos subidas (se crea automáticamente)
│       └── YYYY-MM-DD/  # Carpetas por fecha
└── .venv/              # Entorno virtual
```

## Tecnologías Utilizadas

- **Flask** - Framework web de Python
- **Bootstrap 5** - Framework CSS para diseño responsive
- **Font Awesome** - Iconos
- **Pillow** - Procesamiento de imágenes
- **JavaScript** - Interactividad del frontend

## Características Técnicas

- **Seguridad:** Validación de tipos de archivo y nombres seguros
- **Optimización:** Redimensionamiento automático de imágenes
- **Organización:** Estructura de carpetas por fecha (YYYY-MM-DD)
- **Responsive:** Adaptado para dispositivos móviles
- **UX:** Previsualizaciones, modales, y feedback visual

## Personalización

Puedes personalizar fácilmente:
- **Colores:** Modifica `static/css/style.css`
- **Nombre:** Cambia "Floristería Raquel" en `templates/base.html`
- **Límites:** Ajusta `MAX_FILE_SIZE` y tipos permitidos en `app.py`
- **Estilos:** Modifica las clases de Bootstrap en los templates
