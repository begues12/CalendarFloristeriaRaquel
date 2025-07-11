#!/usr/bin/env python3
"""
Demo de Webhook WooCommerce para Calendario
==========================================

Este script demuestra cómo los pedidos de WooCommerce se añaden
automáticamente como notas en el calendario de la floristería.
"""

import requests
import json
from datetime import datetime, date, timedelta

class WooCommerceWebhookDemo:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.logged_in = False
    
    def login(self, username='admin', password='admin123'):
        """Iniciar sesión en la aplicación"""
        try:
            # Obtener formulario de login
            login_page = self.session.get(f'{self.base_url}/auth/login')
            print(f"📝 Obteniendo página de login: {login_page.status_code}")
            
            # Hacer login
            login_data = {
                'username': username,
                'password': password
            }
            
            response = self.session.post(
                f'{self.base_url}/auth/login',
                data=login_data,
                allow_redirects=False
            )
            
            if response.status_code in [302, 200]:
                self.logged_in = True
                print(f"✅ Login exitoso como {username}")
                return True
            else:
                print(f"❌ Error en login: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    def simulate_woocommerce_order(self, order_data):
        """Simular un pedido de WooCommerce enviado vía webhook"""
        try:
            response = self.session.post(
                f'{self.base_url}/webhook/woocommerce',
                json=order_data,
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                print(f"✅ Pedido #{order_data['id']} añadido al calendario:")
                print(f"   📅 Fecha: {result['date']}")
                print(f"   🏷️  Estado: {result['status']}")
                print(f"   ⚡ Acción: {result['action']}")
                return result
            else:
                print(f"❌ Error procesando pedido: {result.get('error', 'Error desconocido')}")
                if result.get('message'):
                    print(f"   Detalle: {result['message']}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_webhook_endpoint(self):
        """Probar el endpoint de test del webhook"""
        if not self.logged_in:
            print("❌ Debe hacer login primero")
            return None
        
        try:
            response = self.session.post(
                f'{self.base_url}/api/woocommerce/test-webhook',
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                print(f"✅ Test del webhook exitoso:")
                print(f"   📝 {result['message']}")
                print(f"   📅 Fecha: {result['date']}")
                print(f"   🛒 Pedido: #{result['order_id']}")
                return result
            else:
                print(f"❌ Error en test: {result.get('error', 'Error desconocido')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def check_calendar_note(self, date_str):
        """Verificar si se creó la nota en el calendario"""
        if not self.logged_in:
            print("❌ Debe hacer login primero")
            return None
        
        try:
            response = self.session.get(f'{self.base_url}/api/notes/{date_str}')
            result = response.json()
            
            if response.status_code == 200:
                notes = result.get('notes', [])
                woo_notes = [note for note in notes if '🛒' in note.get('title', '')]
                
                if woo_notes:
                    print(f"📋 Notas de WooCommerce encontradas para {date_str}:")
                    for note in woo_notes:
                        print(f"   • {note['title']} ({note['priority']})")
                else:
                    print(f"ℹ️  No se encontraron notas de WooCommerce para {date_str}")
                
                return woo_notes
            else:
                print(f"❌ Error obteniendo notas: {result.get('error', 'Error desconocido')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def demo_different_order_statuses(self):
        """Demostrar diferentes estados de pedidos WooCommerce"""
        print("\n🚀 Demo de Estados de Pedidos WooCommerce")
        print("=" * 60)
        
        # Datos base del pedido
        base_order = {
            "total": "75.50",
            "currency": "EUR",
            "date_created": datetime.now().isoformat(),
            "billing": {
                "first_name": "María",
                "last_name": "García",
                "email": "maria.garcia@email.com",
                "phone": "+34 666 123 456"
            },
            "line_items": [
                {
                    "name": "Ramo de novia - Rosas blancas",
                    "quantity": 1
                },
                {
                    "name": "Boutonniere",
                    "quantity": 2
                }
            ]
        }
        
        # Diferentes estados para probar
        statuses = [
            {"id": 1001, "status": "pending", "description": "Pedido pendiente"},
            {"id": 1002, "status": "processing", "description": "Pedido en proceso"},
            {"id": 1003, "status": "on-hold", "description": "Pedido en espera"},
            {"id": 1004, "status": "completed", "description": "Pedido completado"},
            {"id": 1005, "status": "cancelled", "description": "Pedido cancelado"}
        ]
        
        created_notes = []
        
        for status_info in statuses:
            print(f"\n{status_info['id']}. Simulando {status_info['description']}...")
            
            order_data = base_order.copy()
            order_data.update({
                "id": status_info["id"],
                "status": status_info["status"]
            })
            
            result = self.simulate_woocommerce_order(order_data)
            if result:
                created_notes.append({
                    'date': result['date'],
                    'order_id': result['order_id'],
                    'status': result['status']
                })
        
        # Verificar que las notas se crearon en el calendario
        if created_notes:
            print(f"\n📅 Verificando notas en el calendario...")
            unique_dates = list(set(note['date'] for note in created_notes))
            
            for date_str in unique_dates:
                self.check_calendar_note(date_str)
        
        return created_notes
    
    def demo_order_updates(self):
        """Demostrar actualización de un pedido existente"""
        print(f"\n🔄 Demo de Actualización de Pedidos")
        print("=" * 60)
        
        order_id = 2001
        
        # 1. Crear pedido inicial
        print(f"1️⃣ Creando pedido inicial #{order_id}...")
        initial_order = {
            "id": order_id,
            "status": "pending",
            "total": "120.00",
            "currency": "EUR",
            "date_created": datetime.now().isoformat(),
            "billing": {
                "first_name": "Carlos",
                "last_name": "Rodríguez",
                "email": "carlos.rodriguez@email.com"
            },
            "line_items": [
                {
                    "name": "Centro de mesa bodas",
                    "quantity": 5
                }
            ]
        }
        
        result1 = self.simulate_woocommerce_order(initial_order)
        
        if result1:
            print(f"\n2️⃣ Actualizando estado a 'procesando'...")
            
            # 2. Actualizar a procesando
            updated_order = initial_order.copy()
            updated_order["status"] = "processing"
            updated_order["total"] = "125.00"  # Cambio de precio
            
            result2 = self.simulate_woocommerce_order(updated_order)
            
            if result2:
                print(f"\n3️⃣ Completando pedido...")
                
                # 3. Completar pedido
                completed_order = updated_order.copy()
                completed_order["status"] = "completed"
                
                result3 = self.simulate_woocommerce_order(completed_order)
                
                # Verificar nota final
                if result3:
                    print(f"\n📋 Verificando nota final en el calendario...")
                    self.check_calendar_note(result3['date'])
    
    def demo_multiple_orders_same_day(self):
        """Demostrar múltiples pedidos el mismo día"""
        print(f"\n📦 Demo de Múltiples Pedidos - Mismo Día")
        print("=" * 60)
        
        today = date.today()
        
        orders = [
            {
                "id": 3001,
                "status": "processing",
                "total": "45.00",
                "billing": {"first_name": "Ana", "last_name": "López"},
                "line_items": [{"name": "Ramo pequeño", "quantity": 1}]
            },
            {
                "id": 3002,
                "status": "processing",
                "total": "80.00",
                "billing": {"first_name": "Pedro", "last_name": "Martín"},
                "line_items": [{"name": "Arreglo funeral", "quantity": 1}]
            },
            {
                "id": 3003,
                "status": "pending",
                "total": "150.00",
                "billing": {"first_name": "Lucía", "last_name": "Fernández"},
                "line_items": [{"name": "Decoración evento", "quantity": 1}]
            }
        ]
        
        for i, order_data in enumerate(orders, 1):
            print(f"\n{i}. Procesando pedido #{order_data['id']}...")
            
            # Completar datos del pedido
            order_data.update({
                "currency": "EUR",
                "date_created": datetime.now().isoformat()
            })
            
            self.simulate_woocommerce_order(order_data)
        
        # Verificar todas las notas del día
        print(f"\n📅 Verificando todas las notas de hoy ({today.strftime('%Y-%m-%d')})...")
        self.check_calendar_note(today.strftime('%Y-%m-%d'))


def main():
    """Función principal"""
    print("🛒 Demo de Webhook WooCommerce → Calendario Floristería")
    print("=" * 70)
    
    # Crear instancia del demo
    demo = WooCommerceWebhookDemo()
    
    # Hacer login
    if not demo.login():
        print("❌ No se pudo hacer login. Verifique que el servidor esté ejecutándose.")
        return
    
    print(f"\n🧪 Probando endpoint de test...")
    demo.test_webhook_endpoint()
    
    # Ejecutar demos
    demo.demo_different_order_statuses()
    demo.demo_order_updates()
    demo.demo_multiple_orders_same_day()
    
    print(f"\n💡 Información importante:")
    print("  🔗 URL del webhook: http://localhost:5000/webhook/woocommerce")
    print("  🔧 Configuración: http://localhost:5000/woocommerce/config")
    print("  📅 Ver calendario: http://localhost:5000/")
    print("  📋 Los pedidos aparecen como notas con icono 🛒")
    print("  🎨 Los colores dependen del estado del pedido")
    print("  🔄 Los pedidos actualizados modifican la nota existente")
    
    print(f"\n✅ Demo completado exitosamente!")
    print("=" * 70)


if __name__ == '__main__':
    main()
