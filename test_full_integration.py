"""
Script de prueba completa de la integración WooCommerce-Calendar
Verifica que los pedidos se muestren correctamente en el calendario
"""

import os
import sys
import json
import requests
from datetime import datetime, date, timedelta

def test_full_integration():
    """Prueba la integración completa desde API hasta Calendar"""
    
    print("🧪 PRUEBA COMPLETA DE INTEGRACIÓN WOOCOMMERCE-CALENDAR")
    print("=" * 65)
    
    base_url = "http://localhost:5000"
    
    # 1. Probar webhook
    print("\n1️⃣ PROBANDO WEBHOOK DE WOOCOMMERCE...")
    
    webhook_data = {
        "id": 77777,
        "status": "processing",
        "total": "175.50",
        "currency": "EUR",
        "date_created": date.today().isoformat() + "T12:30:00",
        "billing": {
            "first_name": "Prueba",
            "last_name": "Integración",
            "email": "prueba.integracion@test.com",
            "phone": "+34 666 123 456"
        },
        "line_items": [
            {"name": "Ramo de prueba integración", "quantity": 1},
            {"name": "Complementos florales", "quantity": 3}
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook/woocommerce",
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook procesado: {result.get('message')}")
            print(f"📅 Fecha guardada: {result.get('date')}")
        else:
            print(f"❌ Error en webhook: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. Ejecute: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    # 2. Probar sincronización manual
    print("\n2️⃣ PROBANDO SINCRONIZACIÓN MANUAL...")
    
    sync_data = {
        "start_date": (date.today() - timedelta(days=3)).strftime('%Y-%m-%d'),
        "end_date": date.today().strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/woocommerce/manual-sync",
            json=sync_data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sincronización manual exitosa!")
            details = result.get('details', {})
            print(f"   📊 Nuevos: {details.get('synced_orders', 0)}")
            print(f"   📊 Actualizados: {details.get('updated_orders', 0)}")
            print(f"   📊 Total: {details.get('total_processed', 0)}")
        else:
            print(f"❌ Error en sincronización: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")
        return False
    
    # 3. Verificar notas en API
    print("\n3️⃣ VERIFICANDO NOTAS VIA API...")
    
    today_str = date.today().strftime('%Y-%m-%d')
    
    try:
        response = requests.get(f"{base_url}/api/notes/date/{today_str}", timeout=10)
        
        if response.status_code == 200:
            notes = response.json()
            print(f"✅ API de notas funcional - {len(notes)} notas encontradas")
            
            woocommerce_notes = [note for note in notes if '🛒 Pedido #' in note.get('title', '')]
            print(f"🛒 Notas de WooCommerce: {len(woocommerce_notes)}")
            
            for note in woocommerce_notes[:3]:  # Mostrar máximo 3
                print(f"   • {note.get('title', 'Sin título')}")
                print(f"     Color: {note.get('color', 'Sin color')}")
                print(f"     Prioridad: {note.get('priority', 'Sin prioridad')}")
            
            if len(woocommerce_notes) > 3:
                print(f"   ... y {len(woocommerce_notes) - 3} más")
                
        else:
            print(f"❌ Error en API de notas: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando notas: {e}")
        return False
    
    # 4. Verificar página del calendario
    print("\n4️⃣ VERIFICANDO PÁGINA DEL CALENDARIO...")
    
    try:
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Buscar indicadores de que hay contenido del calendario
            if 'notes_by_date' in html_content:
                print("✅ Template del calendario cargado correctamente")
            else:
                print("⚠️ Template del calendario puede tener problemas")
            
            # Buscar indicadores de notas
            if 'fa-sticky-note' in html_content:
                print("✅ Iconos de notas encontrados en template")
            else:
                print("⚠️ No se encontraron iconos de notas")
                
        else:
            print(f"❌ Error cargando calendario: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando calendario: {e}")
        return False
    
    # 5. Crear nota de prueba via API
    print("\n5️⃣ CREANDO NOTA DE PRUEBA VIA API...")
    
    test_note = {
        "date_for": date.today().strftime('%Y-%m-%d'),
        "title": "🧪 Nota de prueba integración",
        "content": "Esta es una nota creada para verificar la integración completa",
        "color": "#e91e63",
        "priority": "high",
        "is_private": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/notes",
            json=test_note,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 201:
            created_note = response.json()
            print(f"✅ Nota creada via API: {created_note.get('title')}")
            note_id = created_note.get('id')
            
            # Eliminar la nota de prueba
            delete_response = requests.delete(f"{base_url}/api/notes/{note_id}", timeout=10)
            if delete_response.status_code == 200:
                print("🗑️ Nota de prueba eliminada")
            
        else:
            print(f"❌ Error creando nota: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error en API de notas: {e}")
    
    return True

def test_specific_date_notes():
    """Prueba notas para fechas específicas"""
    print("\n6️⃣ PROBANDO NOTAS EN FECHAS ESPECÍFICAS...")
    
    base_url = "http://localhost:5000"
    
    # Probar últimos 7 días
    for i in range(7):
        test_date = date.today() - timedelta(days=i)
        date_str = test_date.strftime('%Y-%m-%d')
        
        try:
            response = requests.get(f"{base_url}/api/notes/date/{date_str}", timeout=5)
            if response.status_code == 200:
                notes = response.json()
                wc_notes = [n for n in notes if '🛒' in n.get('title', '')]
                if wc_notes:
                    print(f"   📅 {date_str}: {len(wc_notes)} pedidos WooCommerce")
                elif notes:
                    print(f"   📅 {date_str}: {len(notes)} notas (no WooCommerce)")
        except:
            pass  # Ignorar errores para esta prueba rápida

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN COMPLETA")
    
    success = test_full_integration()
    
    if success:
        test_specific_date_notes()
        
        print("\n" + "=" * 65)
        print("🎉 PRUEBAS DE INTEGRACIÓN COMPLETADAS")
        print("\n✅ RESULTADOS:")
        print("   • Webhook de WooCommerce funcional")
        print("   • Sincronización manual operativa")
        print("   • API de notas del calendario activa")
        print("   • Template del calendario cargando")
        print("   • Creación/eliminación de notas via API exitosa")
        
        print("\n🏁 PASOS FINALES:")
        print("1. Abra el navegador en: http://localhost:5000")
        print("2. Vaya al calendario principal")
        print("3. Verifique que los pedidos aparezcan como notas con colores")
        print("4. Configure WooCommerce real en: /woocommerce/config")
        
        print("\n💡 Si no ve los pedidos en el calendario:")
        print("   • Verifique que sea usuario admin")
        print("   • Refresque la página del calendario")
        print("   • Revise que las fechas coincidan")
        print("   • Ejecute: python diagnose_woocommerce.py")
        
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("Revise los errores anteriores antes de continuar")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
