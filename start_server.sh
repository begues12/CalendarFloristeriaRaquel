#!/bin/bash
# Script de inicio para servidor (start_server.sh)
# Dale permisos de ejecución: chmod +x start_server.sh

echo "🌸 === Iniciando Floristería Raquel Server ==="

# Crear carpeta de logs si no existe
mkdir -p logs

# Verificar que existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "⚠️  Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias si es necesario
if [ ! -f ".dependencies_installed" ]; then
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt
    pip install gunicorn  # Para producción
    touch .dependencies_installed
fi

# Verificar base de datos
if [ ! -f "instance/floristeria_production.db" ]; then
    echo "🗄️  Inicializando base de datos..."
    python -m flask db upgrade
    python init_users.py
fi

# Verificar configuración
if [ ! -f ".env" ]; then
    echo "❌ No se encontró archivo .env"
    echo "   Copia .env.production a .env y modifica las configuraciones"
    exit 1
fi

echo "🚀 Iniciando servidor..."

# Opción 1: Desarrollo (Flask built-in server)
if [ "$1" = "dev" ]; then
    echo "🔧 Modo desarrollo"
    python app.py
else
    # Opción 2: Producción (Gunicorn)
    echo "🏭 Modo producción con Gunicorn"
    gunicorn -c gunicorn.conf.py app:app
fi
