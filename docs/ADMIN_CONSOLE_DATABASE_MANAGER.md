# Consola Administrativa y Gestor de Base de Datos

## Descripción

Se han añadido dos nuevas herramientas avanzadas al **Panel de Super Administrador**:

1. **🖥️ Consola Administrativa**: Ejecuta comandos del sistema de forma segura
2. **🗄️ Gestor de Base de Datos**: Administración avanzada de la base de datos

## 🖥️ Consola Administrativa

### Características
- **Interfaz tipo terminal** con historial de comandos
- **Lista blanca de comandos** por seguridad
- **Comandos rápidos** predefinidos
- **Historial navegable** con flechas arriba/abajo
- **Scripts de gestión** integrados

### Comandos Permitidos
```bash
# Sistema
ls, dir, pwd, whoami

# Python
python --version
pip list
pip show [package]

# Git
git status
git log --oneline -5
git branch

# Flask
flask --version
flask db current
flask db history
flask db show

# Scripts del proyecto
python scripts/check_database.py
python scripts/manage_super_admin.py --list
python scripts/demo_database_config.py
```

### Acceso
1. **Panel Super Admin** → **"Consola Administrativa"**
2. URL directa: `/admin/admin_console`

### Uso
- **Escribir comando** en el input inferior
- **Enter** para ejecutar
- **↑/↓** para navegar historial
- **Botones rápidos** para comandos comunes
- **help** para ver comandos disponibles

## 🗄️ Gestor de Base de Datos

### Características
- **Información detallada** de la base de datos
- **Ejecutor de consultas SQL** (solo lectura)
- **Explorador de tablas** con detalles de columnas
- **Herramientas de optimización**
- **Estadísticas de rendimiento**

### Funcionalidades

#### 📊 Información General
- Motor de base de datos (MySQL/SQLite)
- Driver utilizado
- Número total de tablas y registros
- Estado del pool de conexiones

#### 🔍 Ejecutor SQL
- **Solo consultas de lectura** (SELECT, SHOW, DESCRIBE, EXPLAIN)
- **Consultas rápidas** predefinidas
- **Resultados en tabla** formateados
- **Atajo Ctrl+Enter** para ejecutar

#### 📋 Explorador de Tablas
- **Lista de todas las tablas** con estadísticas
- **Detalles de columnas** (tipo, nullable, default)
- **Acciones rápidas** por tabla:
  - Ver datos (SELECT * LIMIT 10)
  - Ver estructura (DESCRIBE)
  - Mostrar detalles expandidos

#### ⚡ Optimización
- **MySQL**: ANALYZE TABLE, OPTIMIZE TABLE
- **SQLite**: VACUUM, ANALYZE
- **Optimización automática** de todas las tablas

### Acceso
1. **Panel Super Admin** → **"Gestor de Base de Datos"**
2. URL directa: `/admin/database_manager`

### Consultas SQL Ejemplo
```sql
-- Ver todos los usuarios
SELECT * FROM users LIMIT 10;

-- Contar registros por tabla
SELECT COUNT(*) as total FROM users;

-- Mostrar estructura de tabla
DESCRIBE users;

-- Mostrar todas las tablas
SHOW TABLES;

-- Explicar consulta
EXPLAIN SELECT * FROM users WHERE username = 'admin';
```

## 🔒 Seguridad

### Consola Administrativa
- **Lista blanca** de comandos permitidos
- **Timeout de 30 segundos** para comandos
- **No comandos destructivos** (rm, del, etc.)
- **Solo comandos de lectura** y diagnóstico

### Gestor de Base de Datos
- **Solo consultas SELECT** y comandos informativos
- **No modificaciones** de datos
- **Validación de consultas** antes de ejecutar
- **Escape de HTML** en resultados

## 📁 Archivos Creados/Modificados

### Rutas (routes.py)
```python
@bp.route('/admin_console')          # Consola administrativa
@bp.route('/execute_command')        # Ejecutar comando
@bp.route('/database_manager')       # Gestor de BD
@bp.route('/execute_sql')           # Ejecutar SQL
@bp.route('/database_optimize')     # Optimizar BD
```

### Templates
- `admin_console.html` - Interfaz de consola
- `database_manager.html` - Gestor de BD
- `super_admin_panel.html` - Enlaces añadidos

### Dependencias
- ✅ `PyMySQL` - Conexión MySQL
- ✅ `cryptography` - Cifrado para PyMySQL

## 🚀 Casos de Uso

### Diagnóstico del Sistema
```bash
# En la consola administrativa
python --version
pip list
git status
flask db current
python scripts/check_database.py
```

### Análisis de Datos
```sql
-- En el gestor de BD
SELECT COUNT(*) FROM users;
SELECT username, is_admin FROM users;
SHOW TABLES;
DESCRIBE user_documents;
```

### Optimización
1. **Gestor de BD** → **Herramientas de Optimización**
2. Seleccionar tipo (ANALYZE/OPTIMIZE/VACUUM)
3. Ejecutar optimización

## 🔧 Configuración

### Variables de Entorno
Las herramientas utilizan la configuración existente:
```bash
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/db
FLASK_CONFIG=development
```

### Permisos
- Solo **Super Administradores** pueden acceder
- Verificación automática de permisos
- Redirección si no autorizado

## 📈 Mejoras Futuras

### Consola
- [ ] Autocompletado de comandos
- [ ] Sintaxis highlighting
- [ ] Guardado de sesiones
- [ ] Comandos personalizados

### Gestor BD
- [ ] Editor SQL con sintaxis highlighting
- [ ] Exportación de resultados (CSV, JSON)
- [ ] Gráficos de estadísticas
- [ ] Monitoreo en tiempo real
- [ ] Consultas guardadas

## 🛠️ Troubleshooting

### Error "Comando no permitido"
- Verificar que el comando esté en la lista blanca
- Usar comandos de solo lectura
- Revisar sintaxis del comando

### Error SQL "Solo lectura"
- Solo usar SELECT, SHOW, DESCRIBE, EXPLAIN
- No usar INSERT, UPDATE, DELETE, DROP
- Verificar sintaxis de la consulta

### Problemas de Conexión BD
- Verificar configuración en Panel de Configuración
- Probar conexión en Gestor de BD
- Revisar logs del servidor
