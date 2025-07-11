@echo off
echo 🚀 Iniciando Floristería Raquel - Servidor Flask
echo =====================================================

REM Activar entorno virtual
call .\venv_house\Scripts\activate.bat

REM Establecer variables de entorno
set FLASK_APP=run.py
set FLASK_ENV=development
set FLASK_DEBUG=1

echo ✅ Entorno virtual activado
echo 🔧 Variables de entorno configuradas
echo 📊 Base de datos: SQLite (instance/floristeria.db)
echo 🌐 URL: http://localhost:5000
echo 🛒 Webhook WooCommerce: http://localhost:5000/webhook/woocommerce
echo ⚙️  Configuración: http://localhost:5000/woocommerce/config
echo.

echo 🚀 Iniciando servidor...
python run.py

pause
