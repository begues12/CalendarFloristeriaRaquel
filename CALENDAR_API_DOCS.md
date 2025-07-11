# 📅 API de Notas del Calendario

## 🎯 Descripción

Esta API permite añadir, obtener, actualizar y eliminar notas del calendario mediante peticiones HTTP JSON. Perfecto para integración con aplicaciones externas o para crear interfaces dinámicas.

## 🔐 Autenticación

Todas las peticiones requieren que el usuario esté autenticado en la aplicación. La autenticación se maneja mediante cookies de sesión de Flask.

## 📡 Endpoints Disponibles

### 1. Crear Nota Completa

**POST** `/api/notes`

Crea una nueva nota con todas las opciones disponibles.

```json
{
  "date_for": "2025-07-15",
  "title": "Reunión con cliente",
  "content": "Revisar propuesta y definir presupuesto",
  "color": "#dc3545",
  "priority": "high",
  "is_private": false,
  "is_reminder": true,
  "reminder_time": "14:30"
}
```

**Respuesta (201):**
```json
{
  "success": true,
  "message": "Nota creada correctamente",
  "note": {
    "id": 123,
    "date_for": "2025-07-15",
    "title": "Reunión con cliente",
    "content": "Revisar propuesta y definir presupuesto",
    "color": "#dc3545",
    "priority": "high",
    "is_private": false,
    "is_reminder": true,
    "reminder_time": "14:30",
    "creator": "Admin",
    "created_at": "2025-07-11T10:30:00"
  }
}
```

### 2. Crear Nota Rápida

**POST** `/api/calendar/{date}/quick-note`

Crea una nota simple con texto y color.

```json
{
  "text": "Recordar llamar al proveedor",
  "color": "#28a745"
}
```

**Respuesta (201):**
```json
{
  "success": true,
  "message": "Nota añadida al calendario",
  "note": {
    "id": 124,
    "date_for": "2025-07-15",
    "title": "Recordar llamar al proveedor",
    "content": null,
    "color": "#28a745",
    "priority": "normal",
    "creator": "Admin"
  }
}
```

### 3. Obtener Notas de una Fecha

**GET** `/api/notes/{date}`

Obtiene todas las notas de una fecha específica.

**Ejemplo:** `/api/notes/2025-07-15`

**Respuesta (200):**
```json
{
  "notes": [
    {
      "id": 123,
      "title": "Reunión con cliente",
      "content": "Revisar propuesta y definir presupuesto",
      "color": "#dc3545",
      "priority": "high",
      "is_private": false,
      "is_reminder": true,
      "reminder_time": "14:30",
      "creator": "Admin",
      "created_at": "2025-07-11T10:30:00"
    }
  ]
}
```

### 4. Actualizar Nota

**PUT** `/api/notes/{note_id}`

Actualiza una nota existente. Solo se actualizan los campos proporcionados.

```json
{
  "title": "Reunión URGENTE con cliente",
  "priority": "urgent",
  "color": "#6f42c1"
}
```

**Respuesta (200):**
```json
{
  "success": true,
  "message": "Nota actualizada correctamente",
  "note": {
    "id": 123,
    "title": "Reunión URGENTE con cliente",
    "priority": "urgent",
    "color": "#6f42c1",
    "updated_at": "2025-07-11T11:00:00"
  }
}
```

### 5. Eliminar Nota

**DELETE** `/api/notes/{note_id}`

Elimina una nota existente.

**Respuesta (200):**
```json
{
  "success": true,
  "message": "Nota eliminada correctamente"
}
```

### 6. Verificar si una Fecha tiene Notas

**GET** `/api/calendar/{date}/has-notes`

Verifica si una fecha específica tiene notas y cuántas.

**Ejemplo:** `/api/calendar/2025-07-15/has-notes`

**Respuesta (200):**
```json
{
  "date": "2025-07-15",
  "has_notes": true,
  "note_count": 3
}
```

## 🎨 Campos y Valores

### Campos Requeridos
- `date_for`: Fecha en formato YYYY-MM-DD
- `title`: Título de la nota (string)

### Campos Opcionales
- `content`: Contenido/descripción (string)
- `color`: Color en formato hex (default: "#ffc107")
- `priority`: Prioridad (default: "normal")
- `is_private`: Si la nota es privada (default: false)
- `is_reminder`: Si es un recordatorio (default: false)
- `reminder_time`: Hora del recordatorio en formato HH:MM

### Valores de Prioridad
- `low` - Baja
- `normal` - Normal (default)
- `high` - Alta  
- `urgent` - Urgente

### Colores Sugeridos
- `#ffc107` - Amarillo (Normal)
- `#007bff` - Azul (Información)
- `#28a745` - Verde (Éxito/Completado)
- `#fd7e14` - Naranja (Advertencia)
- `#dc3545` - Rojo (Urgente/Importante)
- `#6f42c1` - Morado (Especial)
- `#6c757d` - Gris (Menor prioridad)

## 🔒 Permisos

### Privilegio Requerido
Todas las operaciones de escritura (crear, actualizar, eliminar) requieren el privilegio `can_manage_notes`.

### Reglas de Acceso
- **Lectura**: Los usuarios pueden ver sus notas privadas y todas las notas públicas
- **Escritura**: Los usuarios pueden crear notas
- **Edición/Eliminación**: Solo el creador de la nota o administradores

## 🚀 Ejemplos de Uso

### Python con requests
```python
import requests

# Login primero
session = requests.Session()
session.post('http://localhost:5000/auth/login', data={
    'username': 'admin',
    'password': 'admin123'
})

# Añadir nota
response = session.post('http://localhost:5000/api/notes', json={
    'date_for': '2025-07-15',
    'title': 'Tarea importante',
    'priority': 'high'
})

print(response.json())
```

### JavaScript/Fetch
```javascript
// Añadir nota rápida
fetch('/api/calendar/2025-07-15/quick-note', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        text: 'Recordatorio importante',
        color: '#dc3545'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL
```bash
# Obtener notas de una fecha
curl -X GET "http://localhost:5000/api/notes/2025-07-15" \
     -H "Content-Type: application/json"

# Crear nota rápida
curl -X POST "http://localhost:5000/api/calendar/2025-07-15/quick-note" \
     -H "Content-Type: application/json" \
     -d '{"text": "Nueva tarea", "color": "#28a745"}'
```

## ❌ Códigos de Error

- **400** - Bad Request: Datos inválidos o campos faltantes
- **403** - Forbidden: Sin permisos para realizar la acción
- **404** - Not Found: Nota no encontrada
- **500** - Internal Server Error: Error interno del servidor

### Ejemplos de Errores
```json
{
  "error": "Campo requerido: title"
}
```

```json
{
  "error": "Formato de fecha inválido. Use YYYY-MM-DD"
}
```

```json
{
  "error": "No tienes permisos para editar esta nota"
}
```

## 🛠️ Integración Frontend

### Archivo JavaScript Incluido
El archivo `calendar-api.js` proporciona una clase `CalendarAPI` lista para usar:

```javascript
const api = new CalendarAPI();

// Añadir nota
await api.addNote('2025-07-15', {
    title: 'Nueva tarea',
    priority: 'high',
    color: '#dc3545'
});

// Obtener notas
const notes = await api.getNotesForDate('2025-07-15');
```

### Integración con Calendario Existente
El archivo incluye un `CalendarEventHandler` que se puede integrar fácilmente con el calendario actual:

```html
<script src="/static/js/calendar-api.js"></script>
```

## 📱 Casos de Uso

### 1. Selector de Fecha + Añadir Nota
```html
<input type="date" id="selectedDate">
<input type="text" id="noteText" placeholder="Añadir nota...">
<button onclick="addQuickNote()">Añadir</button>

<script>
async function addQuickNote() {
    const date = document.getElementById('selectedDate').value;
    const text = document.getElementById('noteText').value;
    
    const api = new CalendarAPI();
    await api.addQuickNote(date, text);
    
    alert('Nota añadida al calendario!');
}
</script>
```

### 2. Widget de Notas del Día
```javascript
async function loadTodayNotes() {
    const today = new Date().toISOString().split('T')[0];
    const api = new CalendarAPI();
    const result = await api.getNotesForDate(today);
    
    const container = document.getElementById('todayNotes');
    container.innerHTML = result.notes.map(note => 
        `<div class="note">${note.title}</div>`
    ).join('');
}
```

### 3. Formulario de Evento
```html
<form onsubmit="createEvent(event)">
    <input type="date" name="date" required>
    <input type="text" name="title" placeholder="Título del evento" required>
    <textarea name="content" placeholder="Descripción"></textarea>
    <select name="priority">
        <option value="normal">Normal</option>
        <option value="high">Alta</option>
        <option value="urgent">Urgente</option>
    </select>
    <button type="submit">Crear Evento</button>
</form>

<script>
async function createEvent(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    const api = new CalendarAPI();
    await api.addNote(formData.get('date'), {
        title: formData.get('title'),
        content: formData.get('content'),
        priority: formData.get('priority')
    });
    
    alert('Evento creado!');
}
</script>
```

¡La API está lista para usar! 🎉
