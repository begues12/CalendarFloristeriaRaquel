#!/usr/bin/env python3
"""
Script para probar la sincronización manual de WooCommerce con el mapeo mejorado
"""

import requests
import json
import time

def test_manual_sync():
    """Prueba la sincronización manual de WooCommerce"""
    print("🔄 Probando sincronización manual de WooCommerce...")
    print("=" * 50)
    
    # URL del endpoint
    url = "http://localhost:5000/api/woocommerce/manual-sync"
    
    try:
        # Realizar petición POST
        response = requests.post(url, json={}, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RESPUESTA EXITOSA:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                processed = data.get('processed', 0)
                print(f"\n🎉 Se procesaron {processed} pedidos exitosamente")
                
                # Mostrar detalles de los pedidos procesados
                results = data.get('results', [])
                for i, result in enumerate(results[:3]):  # Mostrar solo los primeros 3
                    print(f"\n📦 PEDIDO {i+1}:")
                    print(f"   ID: {result.get('order_id', 'N/A')}")
                    print(f"   Fecha: {result.get('date', 'N/A')}")
                    print(f"   Estado: {result.get('status', 'N/A')}")
                    print(f"   Acción: {result.get('action', 'N/A')}")
            else:
                print(f"❌ Error en la sincronización: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: ¿Está ejecutándose el servidor Flask?")
        print("   Ejecuta: python app.py")
    
    except requests.exceptions.Timeout:
        print("❌ Timeout: La petición tardó demasiado")
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_calendar_api():
    """Prueba la API del calendario para ver las notas creadas"""
    print("\n🗓️ Verificando notas en el calendario...")
    print("=" * 50)
    
    # Obtener notas de hoy y mañana
    from datetime import date, timedelta
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    for test_date in [today, tomorrow]:
        url = f"http://localhost:5000/api/calendar/notes?date={test_date.strftime('%Y-%m-%d')}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                
                print(f"\n📅 {test_date.strftime('%Y-%m-%d')}: {len(notes)} notas")
                
                # Mostrar notas de WooCommerce
                woo_notes = [note for note in notes if 'Pedido #' in note.get('title', '')]
                
                for note in woo_notes[:2]:  # Mostrar solo 2
                    print(f"   🌹 {note.get('title', 'Sin título')}")
                    content_preview = note.get('content', '')[:100]
                    if len(content_preview) == 100:
                        content_preview += '...'
                    print(f"      {content_preview}")
            
        except Exception as e:
            print(f"   ❌ Error obteniendo notas de {test_date}: {e}")

if __name__ == "__main__":
    print("🧪 PRUEBA DE INTEGRACIÓN WOOCOMMERCE")
    print("=" * 60)
    
    # Esperar un poco para asegurar que el servidor esté listo
    print("⏳ Esperando a que el servidor esté listo...")
    time.sleep(2)
    
    # Probar sincronización
    test_manual_sync()
    
    # Probar API del calendario
    test_calendar_api()
    
    print("\n✨ Prueba completada")
    print("\nPara ver los resultados en el navegador:")
    print("🔗 http://localhost:5000")
    print("🔗 http://localhost:5000/calendar/woocommerce/config")
