"""
Script de verificación del estado del sistema WooCommerce-Calendar
Verifica que todas las funciones y archivos estén en su lugar
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Verifica si un archivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NO ENCONTRADO")
        return False

def check_directory_exists(dir_path, description):
    """Verifica si un directorio existe"""
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} - NO ENCONTRADO")
        return False

def check_code_in_file(file_path, search_text, description):
    """Verifica si cierto código existe en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - NO ENCONTRADO")
                return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def main():
    print("🔍 VERIFICACIÓN DEL SISTEMA WOOCOMMERCE-CALENDAR")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    checks_passed = 0
    total_checks = 0
    
    # Verificar archivos principales
    print("\n📁 ARCHIVOS PRINCIPALES:")
    files_to_check = [
        ("app.py", "Archivo principal de la aplicación"),
        ("models.py", "Modelos de la base de datos"),
        ("requirements.txt", "Dependencias de Python"),
    ]
    
    for file_name, description in files_to_check:
        total_checks += 1
        if check_file_exists(base_path / file_name, description):
            checks_passed += 1
    
    # Verificar estructura de directorios
    print("\n📂 ESTRUCTURA DE DIRECTORIOS:")
    dirs_to_check = [
        ("app", "Directorio principal de la aplicación"),
        ("app/blueprints", "Blueprints de Flask"),
        ("app/blueprints/calendar", "Blueprint del calendario"),
        ("app/models", "Modelos de la aplicación"),
        ("app/templates", "Templates HTML"),
        ("app/static", "Archivos estáticos"),
        ("templates", "Templates adicionales"),
    ]
    
    for dir_name, description in dirs_to_check:
        total_checks += 1
        if check_directory_exists(base_path / dir_name, description):
            checks_passed += 1
    
    # Verificar archivos de templates
    print("\n🖼️  TEMPLATES:")
    template_files = [
        ("app/templates/calendar.html", "Template principal del calendario"),
        ("app/templates/calendar_notes.html", "Template de notas del calendario"),
        ("templates/woocommerce_config.html", "Template de configuración WooCommerce"),
    ]
    
    for file_name, description in template_files:
        total_checks += 1
        if check_file_exists(base_path / file_name, description):
            checks_passed += 1
    
    # Verificar rutas importantes en el código
    print("\n🛣️  RUTAS Y FUNCIONES:")
    routes_file = base_path / "app/blueprints/calendar/routes.py"
    
    code_checks = [
        ("@bp.route('/webhook/woocommerce'", "Ruta del webhook WooCommerce"),
        ("@bp.route('/api/woocommerce/manual-sync'", "Ruta de sincronización manual"),
        ("def process_woocommerce_order", "Función de procesamiento de pedidos"),
        ("@bp.route('/woocommerce/config'", "Ruta de configuración WooCommerce"),
        ("CalendarNote", "Modelo de notas del calendario"),
    ]
    
    for search_text, description in code_checks:
        total_checks += 1
        if check_code_in_file(routes_file, search_text, description):
            checks_passed += 1
    
    # Verificar modelos
    print("\n🗃️  MODELOS DE BASE DE DATOS:")
    models_file = base_path / "app/models/user.py"
    
    model_checks = [
        ("class CalendarNote", "Modelo CalendarNote"),
        ("class ApiIntegration", "Modelo ApiIntegration"),
        ("class ApiData", "Modelo ApiData"),
    ]
    
    for search_text, description in model_checks:
        total_checks += 1
        if check_code_in_file(models_file, search_text, description):
            checks_passed += 1
    
    # Verificar archivos de documentación
    print("\n📚 DOCUMENTACIÓN:")
    doc_files = [
        ("CALENDAR_API_DOCS.md", "Documentación de la API del calendario"),
        ("WOOCOMMERCE_INTEGRATION.md", "Documentación de integración WooCommerce"),
        ("IMPLEMENTATION_SUMMARY.md", "Resumen de implementación"),
    ]
    
    for file_name, description in doc_files:
        total_checks += 1
        if check_file_exists(base_path / file_name, description):
            checks_passed += 1
    
    # Verificar scripts de demostración
    print("\n🧪 SCRIPTS DE PRUEBA:")
    demo_files = [
        ("demo_calendar_api.py", "Script de demostración de API"),
        ("demo_woocommerce_webhook.py", "Script de prueba de webhook"),
        ("test_woocommerce_sync.py", "Script de prueba de sincronización"),
    ]
    
    for file_name, description in demo_files:
        total_checks += 1
        if check_file_exists(base_path / file_name, description):
            checks_passed += 1
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print(f"✅ Verificaciones exitosas: {checks_passed}/{total_checks}")
    
    percentage = (checks_passed / total_checks) * 100
    print(f"📈 Porcentaje de completitud: {percentage:.1f}%")
    
    if percentage >= 90:
        print("🎉 ¡Excelente! El sistema está completamente implementado.")
        status = "COMPLETO"
    elif percentage >= 75:
        print("✅ Bien! El sistema está mayormente implementado.")
        status = "FUNCIONAL"
    elif percentage >= 50:
        print("⚠️  Advertencia: Faltan algunos componentes importantes.")
        status = "PARCIAL"
    else:
        print("❌ Error: Faltan muchos componentes críticos.")
        status = "INCOMPLETO"
    
    print(f"🏷️  Estado del sistema: {status}")
    
    # Instrucciones de siguiente paso
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Ejecute la aplicación: python app.py")
    print("2. Vaya a http://localhost:5000 para ver el calendario")
    print("3. Configure WooCommerce en http://localhost:5000/woocommerce/config")
    print("4. Pruebe la sincronización manual en la página de configuración")
    print("5. Los pedidos aparecerán como notas en el calendario")
    
    return percentage >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
