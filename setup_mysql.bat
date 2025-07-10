@echo off
echo ===========================================
echo  Configuracion de MySQL - Floristeria Raquel
echo ===========================================
echo.

echo 1. Verificando estado actual...
python scripts\check_database.py

echo.
echo 2. ¿Deseas continuar con la configuracion de MySQL?
set /p continue="Continuar (s/N): "
if /i "%continue%" neq "s" goto :end

echo.
echo 3. Exportando datos SQLite (si existen)...
python scripts\export_sqlite_data.py

echo.
echo 4. Configurando MySQL...
python scripts\setup_mysql.py

echo.
echo 5. ¿Importar datos exportados? (solo si exportaste en paso 3)
set /p import="Importar datos (s/N): "
if /i "%import%" equ "s" (
    if exist "data_export\import_to_mysql.py" (
        echo Importando datos...
        python data_export\import_to_mysql.py
    ) else (
        echo No se encontro script de importacion.
    )
)

echo.
echo 6. Verificacion final...
python scripts\check_database.py

echo.
echo ===========================================
echo  Configuracion completada!
echo ===========================================
echo.
echo Ahora puedes ejecutar la aplicacion con:
echo   python run.py
echo.
echo Para mas informacion, consulta:
echo   docs\MYSQL_MIGRATION.md

:end
pause
