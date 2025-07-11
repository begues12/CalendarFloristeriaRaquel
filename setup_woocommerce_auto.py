#!/usr/bin/env python3
"""
Script para configurar automáticamente WooCommerce con credenciales específicas
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import DevelopmentConfig
from app.utils.api_service import ApiIntegrationService
from app.models.user import User

def setup_woocommerce_with_credentials():
    """Configurar WooCommerce con las credenciales del wsgi.py"""
    app = create_app()
    app.config.from_object(DevelopmentConfig)
    
    with app.app_context():
        # Credenciales del comentario en wsgi.py
        consumer_key = "ck_cda0de90e5b9c4ef0130a0aa98a92dc526425c78"
        consumer_secret = "cs_e35c00cd198e198148fbf2cdbe96d1044c5169fc"
        
        # Solicitar URL de la tienda al usuario
        store_url = input("Ingresa la URL de tu tienda WooCommerce (ej: https://mi-tienda.com): ").strip()
        
        if not store_url:
            print("❌ Error: URL de tienda requerida")
            return
        
        # Obtener usuario admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("❌ Error: Usuario admin no encontrado")
            return
        
        print("🚀 Configurando integraciones WooCommerce...")
        
        # Crear múltiples integraciones útiles para floristería
        integrations_to_create = [
            {
                'type': 'products',
                'name': 'Productos de la Floristería'
            },
            {
                'type': 'orders_today',
                'name': 'Pedidos de Hoy'
            },
            {
                'type': 'featured_products',
                'name': 'Productos Destacados'
            },
            {
                'type': 'low_stock',
                'name': 'Alertas de Stock'
            }
        ]
        
        created_count = 0
        
        for integration_config in integrations_to_create:
            print(f"\n📦 Creando: {integration_config['name']}")
            
            result = ApiIntegrationService.create_woocommerce_integration(
                store_url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                integration_type=integration_config['type'],
                name=integration_config['name'],
                created_by=admin.id
            )
            
            if result['success']:
                print(f"  ✅ {result['message']}")
                if result['test_result']['success']:
                    print(f"  🔗 Conexión verificada correctamente")
                else:
                    print(f"  ⚠️  Advertencia: {result['test_result']['message']}")
                created_count += 1
            else:
                print(f"  ❌ {result['message']}")
        
        print(f"\n🎉 Configuración completada!")
        print(f"   - Integraciones creadas: {created_count}/{len(integrations_to_create)}")
        print(f"   - Ve a 'Gestionar APIs' en el calendario para ver y gestionar las integraciones")
        
        if created_count > 0:
            print(f"\n💡 Próximos pasos:")
            print(f"   1. Ve al calendario principal")
            print(f"   2. Haz clic en 'Sincronizar APIs' para obtener datos")
            print(f"   3. Los datos de WooCommerce aparecerán en los días del calendario")

if __name__ == '__main__':
    setup_woocommerce_with_credentials()
