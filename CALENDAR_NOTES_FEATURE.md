# 📅 API de Notas del Calendario - Selección de Fechas

## Descripción
Las APIs de notas del calendario permiten añadir eventos/notas cuando un usuario selecciona una fecha en el calendario. Esta funcionalidad está completamente integrada tanto en el frontend como en las APIs REST.

## 🎯 Funcionalidad Principal

### Selección de Fecha y Añadir Nota
Cuando un usuario hace clic en el botón "+" de cualquier fecha del calendario:

1. **Se abre un modal** con un formulario para crear la nota
2. **Se completan los datos** (título, contenido, color, prioridad, etc.)
3. **Se guarda vía API** usando las rutas REST implementadas
4. **Se actualiza el indicador visual** mostrando que la fecha tiene notas

## 🔧 APIs Disponibles

### 1. Crear Nota Rápida
```
POST /api/calendar/<fecha>/quick-note
```
**Uso:** Añadir rápidamente una nota simple a una fecha seleccionada.

**Datos de entrada:**
```json
{
    "text": "Texto de la nota",
    "color": "#ffc107",
    "priority": "normal",
    "is_private": false
}
```

### 2. Crear Nota Detallada  
```
POST /api/notes
```
**Uso:** Crear una nota completa con todas las opciones.

**Datos de entrada:**
```json
{
    "date_for": "2025-07-15",
    "title": "Título de la nota",
    "content": "Contenido detallado",
    "color": "#007bff",
    "priority": "high",
    "is_private": false,
    "is_reminder": true,
    "reminder_time": "14:30"
}
```

### 3. Obtener Notas de una Fecha
```
GET /api/notes/<fecha>
```
**Uso:** Listar todas las notas de una fecha específica.

### 4. Verificar si una Fecha Tiene Notas
```
GET /api/calendar/<fecha>/has-notes
```
**Uso:** Verificar rápidamente si una fecha tiene notas (para indicadores visuales).

**Respuesta:**
```json
{
    "date": "2025-07-15",
    "has_notes": true,
    "note_count": 3
}
```

### 5. Actualizar Nota
```
PUT /api/notes/<note_id>
```
**Uso:** Modificar una nota existente.

### 6. Eliminar Nota
```
DELETE /api/notes/<note_id>
```
**Uso:** Eliminar una nota.

## 🖥️ Integración Frontend

### Componentes Añadidos al Calendario

1. **Botón "+" en cada fecha:** Permite añadir notas rápidamente
2. **Modal de creación:** Formulario completo para crear notas
3. **Indicadores visuales:** Muestran cuando una fecha tiene notas
4. **JavaScript integrado:** Maneja toda la interacción con las APIs

### Funciones JavaScript Principales

```javascript
// Instanciar API client
const calendarAPI = new CalendarAPI();

// Añadir nota
await calendarAPI.addNote(dateStr, noteData);

// Verificar si fecha tiene notas
await calendarAPI.checkDateHasNotes(dateStr);

// Obtener notas de una fecha
await calendarAPI.getNotes(dateStr);
```

## 🎨 Características de la UI

### Modal de Creación de Notas
- **Título obligatorio** (máximo 200 caracteres)
- **Contenido opcional** (máximo 1000 caracteres)
- **Selector de color** con 6 opciones predefinidas
- **Nivel de prioridad** (Baja, Normal, Alta, Urgente)
- **Opción de nota privada** (solo visible para el creador)
- **Validación en tiempo real**

### Indicadores Visuales
- **Badge con número de notas** en fechas que tienen eventos
- **Iconos diferenciados** por tipo y prioridad
- **Colores personalizables** según preferencias del usuario

## 🔐 Sistema de Permisos

### Privilegios Requeridos
- **`can_view_calendar`:** Ver el calendario y notas públicas
- **`can_manage_notes`:** Crear, editar y eliminar notas

### Reglas de Acceso
- **Usuarios normales:** Solo pueden ver/editar sus propias notas y notas públicas
- **Administradores:** Pueden ver/editar todas las notas
- **Notas privadas:** Solo visibles para el creador y administradores

## 📱 Responsive Design

### Adaptación a Dispositivos
- **Desktop:** Botones y modales completos
- **Tablet:** Interfaz adaptada con controles táctiles
- **Móvil:** Formularios optimizados y navegación simplificada

## 🚀 Cómo Usar

### Para Usuarios Finales
1. **Abrir el calendario** en la aplicación
2. **Hacer clic en el botón "+"** de cualquier fecha
3. **Completar el formulario** con los datos de la nota/evento
4. **Guardar** y ver el indicador visual actualizado

### Para Desarrolladores
```python
# Ejemplo de uso en Python
import requests

# Crear nota rápida
data = {"text": "Reunión importante", "priority": "high"}
response = requests.post(
    "http://localhost:5000/api/calendar/2025-07-15/quick-note",
    json=data,
    headers={"Content-Type": "application/json"}
)
```

### Para Aplicaciones Externas
```javascript
// Ejemplo de integración externa
fetch('/api/calendar/2025-07-15/quick-note', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({
        text: 'Evento desde app externa',
        color: '#28a745',
        priority: 'normal'
    })
});
```

## 📋 Formatos y Validaciones

### Formatos de Fecha
- **API:** `YYYY-MM-DD` (ej: `2025-07-15`)
- **Display:** Formato localizado según idioma del usuario

### Validaciones
- **Título:** Obligatorio, 1-200 caracteres
- **Contenido:** Opcional, máximo 1000 caracteres  
- **Color:** Debe ser código hex válido
- **Prioridad:** `low`, `normal`, `high`, `urgent`
- **Hora recordatorio:** Formato `HH:MM` (24 horas)

### Colores Predefinidos
- 🟡 **Amarillo** (`#ffc107`) - Por defecto
- 🟢 **Verde** (`#28a745`) - Completado/Positivo
- 🔴 **Rojo** (`#dc3545`) - Urgente/Importante
- 🔵 **Azul** (`#007bff`) - Información
- 🟣 **Morado** (`#6f42c1`) - Eventos especiales
- 🟠 **Naranja** (`#fd7e14`) - Advertencias

## 🔧 Configuración y Mantenimiento

### Base de Datos
Las notas se almacenan en la tabla `calendar_note` con los campos:
- `id`, `date_for`, `title`, `content`
- `color`, `priority`, `is_private`, `is_reminder`
- `reminder_time`, `created_by`, `created_at`, `updated_at`

### Performance
- **Carga asíncrona** de indicadores de notas
- **Cache del lado cliente** para mejorar rendimiento
- **Paginación automática** en listas largas de notas

## 🐛 Solución de Problemas

### Errores Comunes
- **403 Forbidden:** Usuario sin privilegios `can_manage_notes`
- **400 Bad Request:** Datos de entrada inválidos
- **404 Not Found:** Nota no encontrada o sin permisos

### Debug
- Verificar autenticación de usuario
- Comprobar privilegios en la base de datos
- Revisar logs del servidor para errores detallados

## ✨ Extensiones Futuras

### Posibles Mejoras
- **Notificaciones push** para recordatorios
- **Integración con calendario externo** (Google Calendar, Outlook)
- **Notas recurrentes** (eventos que se repiten)
- **Categorías personalizadas** para organizar notas
- **Exportar notas** a PDF o Excel
- **Búsqueda avanzada** por contenido y filtros

---

**Nota:** Esta funcionalidad está completamente integrada y lista para uso en producción. Para más detalles técnicos, consultar el código fuente en `app/blueprints/calendar/routes.py` y `app/static/js/calendar-api.js`.
