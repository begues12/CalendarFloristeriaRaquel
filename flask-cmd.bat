@echo off
REM Script para facilitar comandos de Flask en Windows
REM Configura automáticamente FLASK_APP y ejecuta comandos

set FLASK_APP=run.py

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="db" goto db_command
if "%1"=="run" goto run_app
if "%1"=="shell" goto flask_shell

REM Comando general de Flask
flask %*
goto end

:help
echo.
echo === FLORISTERIA RAQUEL - COMANDOS FLASK ===
echo.
echo Uso: flask-cmd.bat [comando] [argumentos]
echo.
echo Comandos disponibles:
echo   db [subcomando]    - Comandos de base de datos
echo   run               - Ejecutar servidor de desarrollo
echo   shell             - Abrir shell de Flask
echo   help              - Mostrar esta ayuda
echo.
echo Ejemplos de comandos de BD:
echo   flask-cmd.bat db current      - Ver migración actual
echo   flask-cmd.bat db history      - Ver historial
echo   flask-cmd.bat db check        - Verificar cambios pendientes
echo   flask-cmd.bat db migrate -m "mensaje" - Crear migración
echo   flask-cmd.bat db upgrade      - Aplicar migraciones
echo.
goto end

:db_command
REM Pasar todos los argumentos restantes al comando flask db
shift
flask db %1 %2 %3 %4 %5 %6 %7 %8 %9
goto end

:run_app
echo Iniciando servidor de desarrollo...
flask run --debug
goto end

:flask_shell
echo Abriendo shell de Flask...
flask shell
goto end

:end
