# 🔐 Sistema de Privilegios Granular - Guía Completa

## 📋 Resumen del Sistema

El sistema implementa un control de acceso granular con **jerarquía de privilegios**:

1. **Super Administradores** - Acceso completo sin restricciones
2. **Administradores** - Acceso completo sin restricciones  
3. **Usuarios Normales** - Acceso basado en privilegios específicos

## 🎯 Jerarquía de Acceso

```
Super Admin (is_super_admin = True)
    └── Acceso total automático a TODOS los privilegios
    
Admin (is_admin = True)  
    └── Acceso total automático a TODOS los privilegios
    
Usuario Normal
    └── Solo acceso a privilegios específicamente asignados
```

## 🔑 Lista de Privilegios Disponibles

### 📅 **Calendario**
- `can_view_calendar` - Ver calendario principal
- `can_upload_photos` - Subir fotos al calendario
- `can_manage_photos` - Gestionar fotos de otros usuarios

### ⏰ **Control de Tiempo**
- `can_time_tracking` - Usar sistema de fichaje personal
- `can_view_own_reports` - Ver sus propios reportes de tiempo
- `can_view_all_reports` - Ver reportes de tiempo de todos los usuarios
- `can_manage_time_entries` - Crear/editar entradas de tiempo

### 📄 **Documentos**
- `can_upload_documents` - Subir documentos personales
- `can_view_own_documents` - Ver sus propios documentos
- `can_view_all_documents` - Ver documentos de todos los usuarios

### ⚙️ **Administración**
- `can_manage_users` - Gestionar usuarios y privilegios
- `can_export_data` - Exportar datos del sistema

## 🛠️ Implementación Técnica

### Backend (Python/Flask)

1. **Modelo User** (`models.py`):
```python
def has_privilege(self, privilege_name):
    # Los admins y super admins tienen acceso completo a todo
    if self.is_admin or self.is_super_admin:
        return True
    return getattr(self, privilege_name, False)
```

2. **Decorador de Rutas**:
```python
@requires_privilege('can_upload_photos')
def upload_photo():
    # Función protegida por privilegio
```

### Frontend (Jinja2 Templates)

**Navegación Dinámica**:
```html
{% if current_user.has_privilege('can_view_calendar') or current_user.is_admin or current_user.is_super_admin %}
    <a href="{{ url_for('calendar.index') }}">Calendario</a>
{% endif %}
```

**Controles Contextuales**:
```html
{% if photo.uploaded_by == current_user.username or current_user.has_privilege('can_manage_photos') or current_user.is_admin %}
    <!-- Botones de edición -->
{% endif %}
```

## 👥 Gestión de Usuarios

### Para Administradores:
1. Ir a **"Gestión de Usuarios"**
2. Seleccionar usuario → **"Ver/Editar"**
3. Modificar privilegios usando checkboxes agrupados
4. Los cambios se aplican inmediatamente

### Privilegios por Defecto (Nuevos Usuarios):
- ✅ `can_view_calendar`
- ✅ `can_upload_photos`
- ✅ `can_time_tracking`
- ✅ `can_view_own_reports`
- ✅ `can_upload_documents`
- ✅ `can_view_own_documents`
- ❌ Resto de privilegios desactivados

## 🔒 Seguridad

- **Doble Protección**: Backend valida privilegios + Frontend adapta UI
- **Error 403**: Acceso automático denegado sin privilegios
- **Jerarquía Clara**: Admins siempre tienen acceso completo
- **Granularidad**: Control específico por funcionalidad

## 🚀 Casos de Uso

### Empleado Básico
```
✅ Ver calendario
✅ Subir sus fotos
✅ Fichaje personal
✅ Ver sus reportes
✅ Gestionar sus documentos
❌ No puede ver datos de otros
```

### Supervisor
```
✅ Todo lo de empleado básico
✅ Ver reportes de todos
✅ Gestionar fotos de otros
✅ Exportar datos
❌ No gestiona usuarios
```

### Administrador
```
✅ ACCESO COMPLETO A TODO
✅ Gestionar usuarios y privilegios
✅ Todas las funcionalidades sin restricción
```

## 📝 Notas Importantes

1. **Los cambios de privilegios se aplican inmediatamente** (no requiere relogin)
2. **La navegación se adapta automáticamente** según privilegios
3. **Los administradores ven siempre todas las opciones**
4. **Los privilegios son acumulativos** (más privilegios = más acceso)
5. **El usuario 'superadmin' está excluido** de la gestión normal

## 🧪 Verificación

Ejecutar el script de prueba:
```bash
python test_admin_privileges.py
```

Este script verifica que los administradores tengan acceso completo a todos los privilegios.

---

✅ **Sistema completamente implementado y funcional**
