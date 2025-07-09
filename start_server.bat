@echo off
REM Script de inicio para Windows (start_server.bat)

echo 🌸 === Iniciando Floristería Raquel Server ===

REM Crear carpeta de logs si no existe
if not exist "logs" mkdir logs

REM Verificar que existe el entorno virtual
if not exist ".venv" (
    echo ⚠️  Creando entorno virtual...
    python -m venv .venv
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Instalar dependencias si es necesario
if not exist ".dependencies_installed" (
    echo 📦 Instalando dependencias...
    pip install -r requirements.txt
    pip install gunicorn
    echo. > .dependencies_installed
)

REM Verificar base de datos
if not exist "instance\floristeria_production.db" (
    echo 🗄️  Inicializando base de datos...
    python -m flask db upgrade
    python init_users.py
)

REM Verificar configuración
if not exist ".env" (
    echo ❌ No se encontró archivo .env
    echo    Copia .env.production a .env y modifica las configuraciones
    pause
    exit /b 1
)

echo 🚀 Iniciando servidor...

REM Verificar parámetro
if "%1"=="dev" (
    echo 🔧 Modo desarrollo
    python app.py
) else (
    echo 🏭 Modo producción con Gunicorn
    gunicorn -c gunicorn.conf.py app:app
)

pause
