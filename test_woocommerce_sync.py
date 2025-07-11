"""
Script de prueba para verificar la funcionalidad de sincronización de WooCommerce
"""

import requests
import json
from datetime import datetime, date, timedelta

def test_manual_sync():
    """Prueba la sincronización manual de WooCommerce"""
    base_url = "http://localhost:5000"
    
    # Datos para la sincronización
    sync_data = {
        "start_date": (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
        "end_date": date.today().strftime('%Y-%m-%d')
    }
    
    try:
        print("🔄 Probando sincronización manual de WooCommerce...")
        print(f"📅 Rango de fechas: {sync_data['start_date']} a {sync_data['end_date']}")
        
        response = requests.post(
            f"{base_url}/api/woocommerce/manual-sync",
            json=sync_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sincronización exitosa!")
            print(f"📊 Estadísticas:")
            details = result.get('details', {})
            print(f"   • Nuevos pedidos: {details.get('synced_orders', 0)}")
            print(f"   • Pedidos actualizados: {details.get('updated_orders', 0)}")
            print(f"   • Errores: {details.get('errors', 0)}")
            print(f"   • Total procesados: {details.get('total_processed', 0)}")
            
            return True
        else:
            print(f"❌ Error en sincronización: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor Flask.")
        print("   Asegúrese de que la aplicación esté ejecutándose en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def test_webhook():
    """Prueba el webhook de WooCommerce"""
    base_url = "http://localhost:5000"
    
    # Datos de ejemplo de un pedido WooCommerce
    webhook_data = {
        "id": 9999,
        "status": "processing",
        "total": "299.99",
        "currency": "EUR",
        "date_created": datetime.now().isoformat(),
        "billing": {
            "first_name": "Prueba",
            "last_name": "Webhook",
            "email": "prueba@test.com",
            "phone": "+34 666 999 888"
        },
        "line_items": [
            {"name": "Ramo de prueba webhook", "quantity": 1},
            {"name": "Decoración especial", "quantity": 2}
        ]
    }
    
    try:
        print("\n🎯 Probando webhook de WooCommerce...")
        print(f"🆔 Pedido de prueba: #{webhook_data['id']}")
        
        response = requests.post(
            f"{base_url}/webhook/woocommerce",
            json=webhook_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook procesado exitosamente!")
            print(f"📝 Mensaje: {result.get('message', 'Sin mensaje')}")
            print(f"📅 Fecha en calendario: {result.get('date', 'No especificada')}")
            return True
        else:
            print(f"❌ Error en webhook: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor Flask.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def test_notes_api():
    """Prueba la API de notas del calendario"""
    base_url = "http://localhost:5000"
    
    try:
        print("\n📝 Probando API de notas del calendario...")
        
        # Obtener notas de hoy
        today_str = date.today().strftime('%Y-%m-%d')
        response = requests.get(f"{base_url}/api/notes/date/{today_str}")
        
        if response.status_code == 200:
            notes = response.json()
            print(f"✅ API de notas funcional!")
            print(f"📋 Notas encontradas para {today_str}: {len(notes)}")
            
            # Mostrar algunas notas (máximo 3)
            for i, note in enumerate(notes[:3]):
                print(f"   {i+1}. {note.get('title', 'Sin título')}")
            
            if len(notes) > 3:
                print(f"   ... y {len(notes) - 3} más")
                
            return True
        else:
            print(f"❌ Error en API de notas: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor Flask.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 PRUEBAS DE FUNCIONALIDAD WOOCOMMERCE")
    print("=" * 50)
    
    # Contador de pruebas exitosas
    successful_tests = 0
    total_tests = 3
    
    # Ejecutar pruebas
    if test_manual_sync():
        successful_tests += 1
    
    if test_webhook():
        successful_tests += 1
        
    if test_notes_api():
        successful_tests += 1
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print(f"✅ Pruebas exitosas: {successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El sistema funciona correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revise los errores arriba.")
    
    print("\n💡 INSTRUCCIONES:")
    print("1. Inicie la aplicación Flask: python app.py")
    print("2. Vaya a http://localhost:5000/woocommerce/config para configurar")
    print("3. Use http://localhost:5000 para ver el calendario")
    print("4. Los pedidos sincronizados aparecerán como notas en el calendario")

if __name__ == "__main__":
    main()
