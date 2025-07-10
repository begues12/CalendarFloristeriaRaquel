# URL Routing - Guía de Referencia

## Prefijos de Blueprint

El proyecto utiliza blueprints con prefijos específicos. Es importante usar estos prefijos en todas las URLs.

### Blueprints Registrados

| Blueprint | Prefijo | Descripción |
|-----------|---------|-------------|
| `auth` | `/auth` | Autenticación y login |
| `calendar` | (sin prefijo) | Calendario principal |
| `time_tracking` | `/time` | Control de horarios |
| `documents` | `/documents` | Gestión de documentos |
| `admin` | `/admin` | Panel administrativo |
| `users` | `/users` | Gestión de usuarios |

### URLs Correctas por Funcionalidad

#### Time Tracking
- ✅ `/time/time_tracking` - Panel de fichaje
- ✅ `/time/time_reports` - Reportes de tiempo
- ✅ `/time/delete_time_entry/<id>` - Eliminar registro
- ✅ `/time/edit_time_entry/<id>` - Editar registro

#### Documents
- ✅ `/documents/my_documents` - Mis documentos
- ✅ `/documents/upload_document` - Subir documento
- ✅ `/documents/delete_document/<id>` - Eliminar documento
- ✅ `/documents/download_document/<id>` - Descargar documento

#### Admin
- ✅ `/admin/admin_documents` - Gestión de documentos (admin)
- ✅ `/admin/admin_delete_document/<id>` - Eliminar documento (admin)
- ✅ `/admin/super_admin_panel` - Panel de super admin
- ✅ `/admin/toggle_maintenance` - Toggle mantenimiento

#### Auth
- ✅ `/auth/login` - Iniciar sesión
- ✅ `/auth/logout` - Cerrar sesión
- ✅ `/auth/register` - Registrarse

#### Calendar (sin prefijo)
- ✅ `/` - Página principal (calendario)
- ✅ `/calendar` - Vista de calendario
- ✅ `/day/<date>` - Vista diaria

### ⚠️ Errores Comunes

#### ❌ URLs Incorrectas (sin prefijo de blueprint)
```javascript
// INCORRECTO
form.action = `/delete_time_entry/${entryId}`;
form.action = `/delete_document/${docId}`;
form.action = `/admin_delete_document/${docId}`;
```

#### ✅ URLs Correctas (con prefijo de blueprint)
```javascript
// CORRECTO
form.action = `/time/delete_time_entry/${entryId}`;
form.action = `/documents/delete_document/${docId}`;
form.action = `/admin/admin_delete_document/${docId}`;
```

### Mejores Prácticas

#### 1. Usar url_for en Templates
```django-html
<!-- RECOMENDADO: Usar url_for -->
<form action="{{ url_for('time_tracking.delete_time_entry', entry_id=entry.id) }}" method="POST">

<!-- EVITAR: URLs hardcodeadas -->
<form action="/time/delete_time_entry/{{ entry.id }}" method="POST">
```

#### 2. Usar url_for en JavaScript
```django-html
<script>
// RECOMENDADO: Generar URL desde Flask
const deleteUrl = "{{ url_for('time_tracking.delete_time_entry', entry_id=0) }}".replace('0', entryId);

// EVITAR: URLs hardcodeadas
const deleteUrl = `/time/delete_time_entry/${entryId}`;
</script>
```

#### 3. Verificar URLs en Desarrollo
```bash
# Listar todas las rutas registradas
flask routes

# Filtrar rutas específicas
flask routes | findstr delete
flask routes | findstr time
```

### Solución de Problemas

#### Error "Not Found" para URLs
1. Verificar que la URL incluya el prefijo del blueprint correcto
2. Verificar que la ruta esté definida en el archivo `routes.py` del blueprint
3. Verificar que el blueprint esté registrado en `app/__init__.py`

#### Verificar Rutas Registradas
```python
# En el shell de Flask
flask shell
>>> from app import create_app
>>> app = create_app()
>>> for rule in app.url_map.iter_rules():
...     print(rule.rule, rule.endpoint)
```

### Checklist de URLs

Al implementar nuevas funcionalidades:

- [ ] ¿La ruta está definida en el blueprint correcto?
- [ ] ¿El blueprint tiene el prefijo correcto registrado?
- [ ] ¿Los templates usan `url_for` en lugar de URLs hardcodeadas?
- [ ] ¿El JavaScript usa URLs generadas por Flask?
- [ ] ¿Se ha probado la ruta en desarrollo?

### Últimas Correcciones Aplicadas

Las siguientes URLs fueron corregidas en el proyecto:

1. **time_reports.html**: `/delete_time_entry/` → `/time/delete_time_entry/`
2. **my_documents.html**: `/delete_document/` → `/documents/delete_document/`
3. **admin_documents.html**: `/admin_delete_document/` → `/admin/admin_delete_document/`

Estas correcciones resuelven los errores 404 "Not Found" que ocurrían al intentar eliminar registros.
