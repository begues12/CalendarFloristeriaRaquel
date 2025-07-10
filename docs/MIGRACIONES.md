# Guía de Migraciones de Base de Datos

## Flask-Migrate - Comandos Principales

### Configuración

Para que los comandos `flask db` funcionen, asegúrate de tener configurada la variable `FLASK_APP`:

```powershell
$env:FLASK_APP="run.py"
```

### Comandos Básicos

#### 1. Verificar Estado Actual
```bash
flask db current
```
Muestra la revisión actual de la base de datos.

#### 2. Ver Historial de Migraciones
```bash
flask db history
```
Lista todas las migraciones aplicadas.

#### 3. Verificar si hay Cambios Pendientes
```bash
flask db check
```
Verifica si hay cambios en los modelos que requieren migración.

#### 4. Crear Nueva Migración
```bash
flask db migrate -m "descripción del cambio"
```
Genera automáticamente una nueva migración basada en los cambios en los modelos.

#### 5. Aplicar Migraciones
```bash
flask db upgrade
```
Aplica todas las migraciones pendientes.

#### 6. Revertir Migración
```bash
flask db downgrade
```
Revierte la última migración aplicada.

### Ejemplos Prácticos

#### Agregar un nuevo campo a un modelo:
1. Edita el modelo en `app/models/user.py`
2. Genera la migración: `flask db migrate -m "add new field"`
3. Revisa el archivo generado en `migrations/versions/`
4. Aplica la migración: `flask db upgrade`

#### Verificar estado:
```bash
flask db current
flask db check
```

### Scripts de Actualización del Sistema

Para entornos de producción donde los comandos CLI pueden no estar disponibles:

#### Script Completo de Actualización
```bash
# Actualización completa (git + dependencias + migraciones)
python scripts/system_update.py

# Solo migraciones
python scripts/system_update.py --migrate-only

# Solo dependencias
python scripts/system_update.py --deps-only

# Solo git
python scripts/system_update.py --git-only

# Salida en JSON (para integración)
python scripts/system_update.py --json
```

#### Script Simple de Migraciones
```bash
# Solo aplicar migraciones (método más seguro)
python scripts/apply_migrations.py
```

#### Uso desde el Panel de Administración

El panel de super administrador utiliza automáticamente estos scripts para manejar las actualizaciones del sistema de manera robusta, especialmente en entornos de producción donde los comandos `flask`, `git` o `pip` pueden no estar en el PATH.

### Solución de Problemas de Actualización

#### Error: "No such file or directory: 'flask'"
Este error ocurre cuando el comando `flask` no está disponible en el PATH del sistema.

**Solución automática**: El sistema ahora usa scripts robustos que manejan este caso:
1. Intenta usar el CLI de Flask desde el entorno virtual
2. Si falla, usa `python -m flask`
3. Como último recurso, ejecuta las migraciones programáticamente

#### Error: "table already exists"
Este error ocurre cuando hay conflictos entre el estado de la base de datos y las migraciones.

**Solución**:
1. Verifica el estado actual: `flask db current`
2. Marca la base de datos en la revisión correcta: `flask db stamp head`
3. Aplica migraciones: `flask db upgrade`

#### Para Entornos de Producción

**Recomendado**: Usar siempre los scripts Python en lugar de comandos CLI:
```bash
# En lugar de: flask db upgrade
python scripts/apply_migrations.py

# En lugar de: git pull && pip install -r requirements.txt && flask db upgrade
python scripts/system_update.py
```

**Configuración de Servidor**: 
- Asegúrate de que el usuario del servidor tenga permisos para escribir en la base de datos
- Configura variables de entorno si es necesario
- Testa los scripts en un entorno de staging primero

### Gestión de Super Administradores

```bash
# Crear nuevo super admin
python scripts/manage_super_admin.py create <username>

# Promover usuario existente
python scripts/manage_super_admin.py add <username>

# Listar super admins
python scripts/manage_super_admin.py list

# Usuario de emergencia
python scripts/manage_super_admin.py create-emergency
```

### Estructura de Archivos

```
migrations/
├── alembic.ini          # Configuración de Alembic
├── env.py              # Configuración del entorno
├── script.py.mako      # Plantilla para nuevas migraciones
└── versions/           # Archivos de migración
    ├── xxx_initial_migration.py
    └── yyy_add_new_field.py
```

### Solución de Problemas

#### Si `flask db` no funciona:
1. Verifica que `FLASK_APP` esté configurado
2. Verifica que Flask-Migrate esté instalado: `pip install Flask-Migrate`
3. Usa el script alternativo: `python scripts/init_database.py`

#### Si hay conflictos de migración:
1. Revisa el estado: `flask db current`
2. Revisa el historial: `flask db history`
3. Si es necesario, resuelve manualmente o resetea la base de datos

### Notas Importantes

- **Siempre** haz backup antes de aplicar migraciones en producción
- Revisa los archivos de migración generados antes de aplicarlos
- En producción, usa `flask db upgrade` para aplicar migraciones
- Para desarrollo, puedes usar `python scripts/init_database.py --reset` si necesitas empezar desde cero

### Desarrollo vs Producción

#### Desarrollo:
- Puedes resetear la base de datos cuando sea necesario
- Usa el script `init_database.py` para reinicios rápidos

#### Producción:
- **NUNCA** uses `--reset`
- Siempre usa migraciones incrementales
- Haz backup antes de cualquier cambio
- Testa las migraciones en un entorno de staging primero
