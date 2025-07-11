#!/usr/bin/env python3
"""
Script para actualizar integraciones existentes y agregar soporte completo para WooCommerce
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import DevelopmentConfig
from app.models.user import db, ApiIntegration

def update_woocommerce_support():
    """Actualizar base de datos para soporte completo de WooCommerce"""
    app = create_app()
    app.config.from_object(DevelopmentConfig)
    
    with app.app_context():
        print("🔄 Actualizando soporte para WooCommerce...")
        
        # Verificar si hay integraciones que podrían ser WooCommerce
        integrations = ApiIntegration.query.all()
        
        updated_count = 0
        for integration in integrations:
            if 'wp-json/wc/' in integration.url or 'woocommerce' in integration.name.lower():
                print(f"🛒 Detectada posible integración WooCommerce: {integration.name}")
                
                # Actualizar tipo si no es ya woocommerce
                if integration.api_type != 'woocommerce':
                    old_type = integration.api_type
                    integration.api_type = 'woocommerce'
                    updated_count += 1
                    print(f"  ✅ Actualizado de '{old_type}' a 'woocommerce'")
        
        # Guardar cambios
        if updated_count > 0:
            db.session.commit()
            print(f"\n✅ Actualizadas {updated_count} integraciones a tipo WooCommerce")
        else:
            print("\n✅ No se encontraron integraciones WooCommerce para actualizar")
        
        print("\n🎉 Sistema actualizado con soporte completo para WooCommerce!")
        print("   - Configuración automática disponible")
        print("   - Mapeos optimizados para e-commerce")
        print("   - Sincronización inteligente")
        print("   - Tipos específicos: productos, pedidos, stock, etc.")

if __name__ == '__main__':
    update_woocommerce_support()
