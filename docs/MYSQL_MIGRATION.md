# Migración a MySQL - Floristería Raquel

Esta documentación describe el proceso completo para migrar la aplicación de SQLite a MySQL.

## Prerrequisitos

### 1. Instalar MySQL Server

**Windows:**
- Descargar MySQL Community Server desde: https://dev.mysql.com/downloads/mysql/
- Ejecutar el instalador y configurar:
  - Tipo de instalación: Server only
  - Configuración de autenticación: Use Strong Password Encryption
  - Crear usuario root con contraseña segura
  - Puerto por defecto: 3306

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 2. Configurar MySQL

Conectar a MySQL como root:
```bash
mysql -u root -p
```

Crear usuario para la aplicación (opcional pero recomendado):
```sql
CREATE USER 'floristeria'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON floristeria*.* TO 'floristeria'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Proceso de Migración

### Paso 1: Exportar Datos Existentes (Solo si tienes datos en SQLite)

Si ya tienes datos en SQLite que quieres conservar:

```bash
cd "C:\Users\afuentes\Documents\CalendarFloristeriaRaquel"
python scripts/export_sqlite_data.py
```

Este script:
- Exportará todos los datos de SQLite a archivos JSON
- Creará un script de importación automática
- Guardará todo en la carpeta `data_export/`

### Paso 2: Configurar MySQL

Ejecutar el script de configuración automática:

```bash
python scripts/setup_mysql.py
```

Este script te guiará a través de:
1. Instalación de dependencias Python (PyMySQL, cryptography)
2. Verificación de conexión a MySQL
3. Creación de bases de datos necesarias
4. Configuración del archivo .env
5. Ejecución de migraciones de Flask-Migrate
6. Inicialización de datos básicos

### Paso 3: Importar Datos (Solo si exportaste desde SQLite)

Si exportaste datos en el Paso 1:

```bash
python data_export/import_to_mysql.py
```

### Paso 4: Verificar la Configuración

```bash
# Verificar conexión a la base de datos
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import db; print('Conexión exitosa:', db.engine.execute('SELECT 1').scalar())"

# Verificar que las tablas existen
python -c "from app import create_app; from app.models import User; app = create_app(); app.app_context().push(); print('Usuarios:', User.query.count())"
```

### Paso 5: Ejecutar la Aplicación

```bash
python run.py
```

## Configuración Manual (Alternativa)

Si prefieres configurar manualmente sin usar los scripts:

### 1. Instalar Dependencias

```bash
pip install PyMySQL==1.1.1 cryptography==42.0.5
```

### 2. Crear Archivo .env

Crear `.env` en la raíz del proyecto:

```env
# Configuración de Base de Datos MySQL
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/floristeria
DEV_DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/floristeria_dev
TEST_DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/floristeria_test

# Otras configuraciones
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=tu_clave_secreta_muy_segura_cambiar_en_produccion
```

### 3. Crear Bases de Datos

```sql
CREATE DATABASE floristeria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE floristeria_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE floristeria_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE floristeria_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Ejecutar Migraciones

```bash
# Inicializar migraciones (solo si no existe carpeta migrations/)
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration to MySQL"

# Aplicar migraciones
flask db upgrade

# Inicializar datos básicos
python scripts/init_database.py
```

## Diferencias Importantes entre SQLite y MySQL

### 1. Tipos de Datos

- **SQLite**: Más flexible con tipos de datos
- **MySQL**: Más estricto, especialmente con fechas y strings

### 2. Configuración de Caracteres

- MySQL usa UTF-8 (utf8mb4) para soporte completo de Unicode
- SQLite maneja UTF-8 automáticamente

### 3. Conexiones Concurrentes

- **SQLite**: Solo una escritura a la vez
- **MySQL**: Multiple conexiones concurrentes (mejor para producción)

### 4. Performance

- **SQLite**: Mejor para desarrollo y aplicaciones pequeñas
- **MySQL**: Mejor para producción con múltiples usuarios

## Configuración de Producción

### Variables de Entorno para Producción

```env
FLASK_ENV=production
FLASK_DEBUG=false
DATABASE_URL=mysql+pymysql://usuario:contraseña@servidor:3306/floristeria_production
SECRET_KEY=clave_secreta_muy_compleja_y_segura
```

### Configuración de MySQL para Producción

Editar `/etc/mysql/mysql.conf.d/mysqld.cnf` (Linux) o `my.ini` (Windows):

```ini
[mysqld]
# Configuración de caracteres
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# Configuración de performance
innodb_buffer_pool_size=256M
max_connections=100
max_allowed_packet=64M

# Configuración de logs
log_error=/var/log/mysql/error.log
slow_query_log=1
slow_query_log_file=/var/log/mysql/slow.log
```

### Backup de MySQL

Script de backup automático:

```bash
#!/bin/bash
# Backup diario de MySQL
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u usuario -p contraseña floristeria_production > backup_floristeria_$DATE.sql
```

## Troubleshooting

### Error: "No module named 'MySQLdb'"

**Solución**: Instalar PyMySQL
```bash
pip install PyMySQL
```

### Error: "Access denied for user"

**Solución**: Verificar credenciales en .env y permisos de usuario MySQL

### Error: "Unknown database"

**Solución**: Crear las bases de datos manualmente:
```sql
CREATE DATABASE floristeria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Error: "Table doesn't exist"

**Solución**: Ejecutar migraciones:
```bash
flask db upgrade
```

### Performance lenta

**Soluciones**:
1. Verificar índices en tablas
2. Ajustar configuración de MySQL
3. Usar connection pooling
4. Optimizar queries

## Rollback a SQLite

Si necesitas volver a SQLite:

1. Cambiar `.env`:
```env
DATABASE_URL=sqlite:///floristeria.db
```

2. Restaurar desde backup SQLite:
```bash
cp instance/floristeria.db.backup instance/floristeria.db
```

3. Ejecutar migraciones:
```bash
flask db upgrade
```

## Scripts Útiles

### Verificar Estado de la Base de Datos

```bash
python scripts/check_database.py
```

### Verificar Conectividad MySQL

```bash
python -c "import pymysql; print('PyMySQL disponible')"
```

### Backup Manual

```bash
python scripts/backup_mysql.py
```

## Monitoreo

### Logs de MySQL

- Linux: `/var/log/mysql/error.log`
- Windows: `C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err`

### Queries Lentas

Habilitar slow query log en MySQL para identificar consultas problemáticas.

### Métricas de Performance

Usar herramientas como:
- MySQL Workbench
- phpMyAdmin
- Grafana + Prometheus

---

Para más información, consultar:
- [Documentación oficial de MySQL](https://dev.mysql.com/doc/)
- [Flask-SQLAlchemy MySQL](https://flask-sqlalchemy.palletsprojects.com/)
- [PyMySQL Documentation](https://pymysql.readthedocs.io/)
