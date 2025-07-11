# Consola Administrativa y Gestor de Base de Datos - ACCESO COMPLETO

## Descripción

Se han añadido dos nuevas herramientas avanzadas al **Panel de Super Administrador** con **ACCESO TOTAL** para uso interno de la empresa:

1. **🖥️ Consola Administrativa**: Ejecuta CUALQUIER comando del sistema sin restricciones
2. **🗄️ Gestor de Base de Datos**: Administración total de BD con todas las consultas SQL permitidas

## 🖥️ Consola Administrativa - SIN RESTRICCIONES

### Características
- **🔓 ACCESO COMPLETO**: Todos los comandos del sistema permitidos
- **Interfaz tipo terminal** con historial de comandos
- **Comandos rápidos** predefinidos para tareas comunes
- **Historial navegable** con flechas arriba/abajo
- **Scripts de gestión** integrados
- **Timeout extendido** (2 minutos por comando)

### Comandos Disponibles (SIN LÍMITES)
```bash
# Sistema completo
dir, ls, cd, mkdir, rmdir, del, copy, move, type, more
tasklist, taskkill, netstat, systeminfo, ping, curl

# Python completo
python --version
pip install [package]
pip uninstall [package]
pip upgrade [package]
python -c "código python"

# Git completo
git status, git pull, git push, git commit, git add
git checkout, git branch, git merge, git reset

# Flask completo
flask run, flask db upgrade, flask db migrate
flask db current, flask db history, flask shell

# Base de datos
mysql -u user -p
sqlite3 archivo.db

# Red y conectividad
ping google.com
curl -X GET http://api.ejemplo.com
wget https://archivo.com/descarga.zip

# Gestión de archivos
find . -name "*.py"
grep "texto" archivo.txt
cat archivo.txt (Linux) / type archivo.txt (Windows)
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

## 🗄️ Gestor de Base de Datos - TODAS LAS CONSULTAS PERMITIDAS

### Características
- **🔓 ACCESO TOTAL**: Cualquier consulta SQL permitida (SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, etc.)
- **Información detallada** de la base de datos
- **Ejecutor de consultas SQL** completo
- **Explorador de tablas** con detalles de columnas
- **Herramientas de optimización**
- **Estadísticas de rendimiento**

### Funcionalidades

#### 📊 Información General
- Motor de base de datos (MySQL/SQLite)
- Driver utilizado
- Número total de tablas y registros
- Estado del pool de conexiones

#### 🔍 Ejecutor SQL - SIN RESTRICCIONES
- **TODAS las consultas SQL** permitidas
- **Consultas rápidas** predefinidas
- **Resultados en tabla** formateados
- **Atajo Ctrl+Enter** para ejecutar
- **Manejo automático de transacciones**

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

### Consultas SQL - EJEMPLOS SIN RESTRICCIONES
```sql
-- ===== CONSULTAS DE LECTURA =====
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

-- Consultas complejas con JOINs
SELECT u.username, COUNT(d.id) as documentos 
FROM users u 
LEFT JOIN user_documents d ON u.id = d.user_id 
GROUP BY u.id;

-- ===== CONSULTAS DE MODIFICACIÓN =====
-- Insertar nuevo usuario
INSERT INTO users (username, email, password_hash) 
VALUES ('nuevo_usuario', 'email@empresa.com', 'hash_password');

-- Actualizar datos
UPDATE users SET is_admin = 1 WHERE username = 'admin';

-- Eliminar registros
DELETE FROM user_documents WHERE created_at < '2023-01-01';

-- ===== CONSULTAS DE ESTRUCTURA =====
-- Crear nueva tabla
CREATE TABLE configuracion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    clave VARCHAR(100) NOT NULL,
    valor TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Añadir columna
ALTER TABLE users ADD COLUMN telefono VARCHAR(20);

-- Crear índice
CREATE INDEX idx_username ON users(username);

-- Eliminar tabla (¡CUIDADO!)
DROP TABLE tabla_temporal;

-- ===== CONSULTAS DE BACKUP/RESTORE =====
-- Exportar datos
SELECT * FROM users INTO OUTFILE '/tmp/users_backup.csv'
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

-- Información del sistema (MySQL)
SHOW VARIABLES LIKE 'version%';
SHOW PROCESSLIST;
SHOW ENGINE INNODB STATUS;
```

## 🔒 Configuración de Seguridad - USO INTERNO EMPRESA

### Consola Administrativa
- **🔓 SIN RESTRICCIONES**: Todos los comandos permitidos
- **Timeout extendido** (120 segundos por comando)
- **Shell completo** con pipes y redirecciones
- **Acceso total al sistema** para administración

### Gestor de Base de Datos
- **🔓 TODAS las consultas SQL** permitidas
- **Modificaciones de datos** habilitadas
- **Creación/eliminación** de tablas y estructuras
- **Transacciones automáticas** con rollback en errores
- **Sin escape de HTML** en resultados (datos crudos)

### ⚠️ IMPORTANTE - USO RESPONSABLE
Esta configuración está diseñada para **uso interno de la empresa** con personal técnico capacitado:

- **Solo Super Administradores** tienen acceso
- **Verificación automática** de permisos  
- **Logs completos** de todas las operaciones
- **Redirección automática** si no autorizado
- **Responsabilidad del usuario** en el uso de comandos

### 💡 Buenas Prácticas Recomendadas
```bash
# Hacer backup antes de cambios importantes
python scripts/backup_database.py

# Verificar estado antes de operaciones críticas
python scripts/check_database.py

# Usar transacciones para cambios múltiples
BEGIN;
-- múltiples consultas aquí
COMMIT; -- o ROLLBACK si hay problemas
```

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
