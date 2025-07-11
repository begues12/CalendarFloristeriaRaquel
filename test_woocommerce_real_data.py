#!/usr/bin/env python3
"""
Test específico para probar el webhook de WooCommerce con datos reales de api_all.json
"""

import requests
import json
import time

def test_woocommerce_webhook_with_real_data():
    """Prueba el webhook de WooCommerce con datos reales"""
    print("🧪 PROBANDO WEBHOOK WOOCOMMERCE CON DATOS REALES")
    print("=" * 60)
    
    # Cargar datos reales
    try:
        with open('api_all.json', 'r', encoding='utf-8') as f:
            orders_data = json.load(f)
        
        print(f"📦 Cargados {len(orders_data)} pedidos reales")
        
        # Probar con los primeros 3 pedidos
        webhook_url = "http://localhost:5000/webhook/woocommerce"
        
        for i, order in enumerate(orders_data[:3]):
            print(f"\n🔍 PROBANDO PEDIDO {i+1}/3 - ID: {order.get('id')}")
            print("-" * 40)
            
            try:
                # Enviar pedido al webhook
                response = requests.post(
                    webhook_url,
                    json=order,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                print(f"📡 Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ WEBHOOK EXITOSO")
                    print(f"   Mensaje: {result.get('message', 'N/A')}")
                    print(f"   Pedido ID: {result.get('order_id', 'N/A')}")
                    print(f"   Estado: {result.get('status', 'N/A')}")
                    print(f"   Fecha: {result.get('date', 'N/A')}")
                else:
                    print(f"❌ Error HTTP {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data.get('message', 'Error desconocido')}")
                    except:
                        print(f"   Respuesta: {response.text[:200]}")
                
            except Exception as e:
                print(f"❌ Error enviando pedido: {e}")
            
            # Pausa entre peticiones
            time.sleep(0.5)
        
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: No se encontró api_all.json")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_direct_order_processing():
    """Prueba directa del procesamiento de pedidos"""
    print("\n🔬 PRUEBA DIRECTA DE PROCESAMIENTO")
    print("=" * 40)
    
    try:
        with open('api_all.json', 'r', encoding='utf-8') as f:
            orders_data = json.load(f)
        
        # Usar el endpoint de test con datos reales
        test_url = "http://localhost:5000/api/woocommerce/test"
        
        # Tomar el primer pedido como ejemplo
        test_order = orders_data[0]
        
        response = requests.post(
            test_url,
            json=test_order,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PROCESAMIENTO EXITOSO")
            print(f"   Mensaje: {result.get('message', 'N/A')}")
            
            # Mostrar información extraída
            if 'details' in result:
                details = result['details']
                print(f"\n📋 DETALLES EXTRAÍDOS:")
                print(f"   Cliente: {details.get('customer_name', 'N/A')}")
                print(f"   Destinatario: {details.get('delivery_name', 'N/A')}")
                print(f"   Fecha entrega: {details.get('delivery_date', 'N/A')}")
                print(f"   Total: {details.get('total', 'N/A')} {details.get('currency', '')}")
                print(f"   Productos: {details.get('products_count', 0)}")
                print(f"   Dedicatorias: {details.get('dedications_count', 0)}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
    
    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")

def check_calendar_notes():
    """Verifica las notas creadas en el calendario"""
    print("\n📅 VERIFICANDO NOTAS EN EL CALENDARIO")
    print("=" * 40)
    
    from datetime import date, timedelta
    
    # Verificar fechas relevantes (hoy y los próximos días)
    dates_to_check = [
        date.today(),
        date.today() + timedelta(days=1),
        date(2025, 7, 10),  # Fecha de entrega del primer pedido
        date(2025, 7, 7),   # Fecha de entrega del tercer pedido
    ]
    
    for check_date in dates_to_check:
        url = f"http://localhost:5000/api/calendar/notes"
        params = {'date': check_date.strftime('%Y-%m-%d')}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                
                # Filtrar notas de WooCommerce
                woo_notes = [note for note in notes if '🌹' in note.get('title', '') and 'Pedido #' in note.get('title', '')]
                
                print(f"\n📅 {check_date}: {len(woo_notes)} pedidos WooCommerce")
                
                for note in woo_notes:
                    title = note.get('title', 'Sin título')
                    print(f"   🌹 {title}")
                    
                    # Mostrar si tiene dedicatoria
                    content = note.get('content', '')
                    if '💌 DEDICATORIA:' in content:
                        print(f"      💌 Incluye dedicatoria")
                    
                    if '🚚 ENTREGA:' in content:
                        print(f"      🚚 Incluye info de entrega")
            
        except Exception as e:
            print(f"   ❌ Error verificando {check_date}: {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DE WOOCOMMERCE")
    print("=" * 60)
    
    # Esperar a que el servidor esté listo
    print("⏳ Esperando servidor...")
    time.sleep(2)
    
    # Verificar que el servidor esté activo
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print(f"✅ Servidor activo (Status: {response.status_code})")
    except:
        print("❌ Error: Servidor no disponible")
        print("   Asegúrate de ejecutar: python app.py")
        return
    
    # Ejecutar pruebas
    print("\n" + "="*60)
    
    # 1. Probar webhook con datos reales
    webhook_success = test_woocommerce_webhook_with_real_data()
    
    # 2. Probar procesamiento directo
    if webhook_success:
        test_direct_order_processing()
    
    # 3. Verificar notas en calendario
    time.sleep(1)
    check_calendar_notes()
    
    print("\n🎉 PRUEBAS COMPLETADAS")
    print("\nPara ver los resultados:")
    print("🔗 Calendario: http://localhost:5000")
    print("🔗 Config WooCommerce: http://localhost:5000/calendar/woocommerce/config")
    print("\n💡 Las notas de pedidos deberían aparecer con:")
    print("   ✓ Información completa del cliente")
    print("   ✓ Detalles de entrega")
    print("   ✓ Dedicatorias formateadas")
    print("   ✓ Fechas de entrega correctas")

if __name__ == "__main__":
    main()
