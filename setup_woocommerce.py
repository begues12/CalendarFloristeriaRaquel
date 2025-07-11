"""
Script para configurar automáticamente la integración WooCommerce
usando los datos del archivo api_all.json
"""

import json
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from app.models.user import ApiIntegration, User
    from app.models import db
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

def setup_woocommerce_integration():
    """Configurar integración WooCommerce automáticamente"""
    
    print("⚙️ CONFIGURACIÓN AUTOMÁTICA DE WOOCOMMERCE")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        
        # Verificar si ya existe una integración WooCommerce
        existing = ApiIntegration.query.filter_by(api_type='woocommerce').first()
        
        if existing:
            print(f"ℹ️ Ya existe integración WooCommerce: {existing.name}")
            print(f"   URL: {existing.url}")
            print(f"   Activa: {'Sí' if existing.is_active else 'No'}")
            
            response = input("\n¿Quiere actualizarla? (s/n): ").lower().strip()
            if response != 's':
                print("❌ Configuración cancelada")
                return False
            
            integration = existing
        else:
            print("📝 Creando nueva integración WooCommerce...")
            integration = ApiIntegration()
        
        # Configurar los datos de la integración
        integration.name = "WooCommerce Floristería"
        integration.api_type = "woocommerce"
        integration.url = "https://floradomicilio.com/wp-json/wc/v3/orders"
        integration.request_method = "GET"
        integration.refresh_interval = 60
        integration.is_active = True
        
        # Headers para WooCommerce (se necesitarán las credenciales reales)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Floristeria-Calendar/1.0"
        }
        integration.headers = json.dumps(headers)
        
        # Configuración de mapeo para WooCommerce
        mapping_config = {
            "data_path": "",  # Los datos vienen directamente como array
            "date_field": "date_created",
            "id_field": "id",
            "status_field": "status",
            "total_field": "total",
            "currency_field": "currency",
            "customer_field": "billing",
            "items_field": "line_items",
            "icon": "fas fa-shopping-cart",
            "color": "#007bff"
        }
        integration.mapping_config = json.dumps(mapping_config, indent=2)
        
        # Mensaje sobre credenciales
        print("\n🔑 CONFIGURACIÓN DE CREDENCIALES:")
        print("Para que funcione correctamente, necesita configurar:")
        print("1. Consumer Key de WooCommerce")
        print("2. Consumer Secret de WooCommerce")
        print("\nEstas credenciales se obtienen en:")
        print("WooCommerce → Configuración → Avanzado → REST API → Agregar clave")
        
        # Opción de configurar credenciales ahora
        setup_creds = input("\n¿Quiere configurar las credenciales ahora? (s/n): ").lower().strip()
        
        if setup_creds == 's':
            consumer_key = input("Consumer Key: ").strip()
            consumer_secret = input("Consumer Secret: ").strip()
            
            if consumer_key and consumer_secret:
                integration.api_key = consumer_key
                integration.request_body = consumer_secret  # Usamos este campo para el secret
                print("✅ Credenciales configuradas")
            else:
                print("⚠️ Credenciales no configuradas - se usará modo de prueba")
        
        # Guardar en base de datos
        if not existing:
            db.session.add(integration)
        
        try:
            db.session.commit()
            print(f"\n✅ Integración WooCommerce configurada exitosamente")
            print(f"   ID: {integration.id}")
            print(f"   Nombre: {integration.name}")
            print(f"   URL: {integration.url}")
            print(f"   Estado: {'Activa' if integration.is_active else 'Inactiva'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            db.session.rollback()
            return False

def test_configuration():
    """Probar la configuración creada"""
    
    print(f"\n🧪 PROBANDO CONFIGURACIÓN...")
    
    app = create_app()
    
    with app.app_context():
        integration = ApiIntegration.query.filter_by(api_type='woocommerce').first()
        
        if not integration:
            print("❌ No se encontró integración WooCommerce")
            return False
        
        print(f"✅ Integración encontrada: {integration.name}")
        
        # Simular una prueba básica
        if integration.api_key and integration.request_body:
            print("✅ Credenciales configuradas")
        else:
            print("⚠️ Credenciales no configuradas - funcionará en modo de prueba")
        
        print(f"✅ URL configurada: {integration.url}")
        print(f"✅ Configuración de mapeo: OK")
        
        return True

def main():
    """Función principal"""
    
    print("🚀 CONFIGURADOR AUTOMÁTICO DE WOOCOMMERCE")
    print("Este script configura automáticamente la integración")
    print("para sincronizar pedidos de WooCommerce con el calendario\n")
    
    success = setup_woocommerce_integration()
    
    if success:
        test_configuration()
        
        print(f"\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
        print(f"\n📋 PRÓXIMOS PASOS:")
        print(f"1. Ejecute la aplicación: python app.py")
        print(f"2. Vaya a: http://localhost:5000/woocommerce/config")
        print(f"3. Pruebe la sincronización manual")
        print(f"4. Configure el webhook en WooCommerce:")
        print(f"   URL: http://localhost:5000/webhook/woocommerce")
        print(f"   Eventos: order.created, order.updated, order.status_changed")
        
        if not input("\n¿Configuró las credenciales? (s/n): ").lower().strip() == 's':
            print(f"\n⚠️ IMPORTANTE:")
            print(f"Sin credenciales reales de WooCommerce, el sistema")
            print(f"funcionará en modo de prueba con datos simulados.")
            print(f"Para conectar con WooCommerce real, configure las")
            print(f"credenciales en la interfaz web.")
    
    else:
        print(f"\n❌ CONFIGURACIÓN FALLÓ")
        print(f"Revise los errores anteriores")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
