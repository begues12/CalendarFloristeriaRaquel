"""
Script para probar la sincronización con los datos reales de WooCommerce
Usa los datos del archivo api_all.json para probar el procesamiento
"""

import json
import sys
import os
from datetime import datetime, date

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from app.models.user import CalendarNote, User
    from app.models import db
    from app.blueprints.calendar.routes import process_woocommerce_order
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

def test_with_real_data():
    """Probar con datos reales de WooCommerce"""
    
    print("🧪 PROBANDO CON DATOS REALES DE WOOCOMMERCE")
    print("=" * 50)
    
    # Cargar datos del archivo JSON
    try:
        with open('api_all.json', 'r', encoding='utf-8') as f:
            wc_orders = json.load(f)
        print(f"📄 Datos cargados: {len(wc_orders)} pedidos")
    except FileNotFoundError:
        print("❌ No se encontró el archivo api_all.json")
        return False
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return False
    
    # Crear contexto de aplicación
    app = create_app()
    
    with app.app_context():
        # Limpiar notas de prueba previas
        test_notes = CalendarNote.query.filter(
            CalendarNote.title.contains('🛒 Pedido #')
        ).all()
        
        if test_notes:
            print(f"🗑️ Eliminando {len(test_notes)} notas de prueba previas")
            for note in test_notes:
                db.session.delete(note)
            db.session.commit()
        
        print(f"\n🔄 PROCESANDO PEDIDOS REALES...")
        
        processed_count = 0
        success_count = 0
        error_count = 0
        
        # Procesar primeros 5 pedidos como prueba
        for i, order in enumerate(wc_orders[:5]):
            if not isinstance(order, dict) or 'id' not in order:
                print(f"⚠️ Pedido {i+1}: Formato inválido")
                continue
                
            order_id = order.get('id')
            order_status = order.get('status', 'unknown')
            
            print(f"\n📦 Procesando pedido #{order_id} (Estado: {order_status})")
            
            try:
                # Mostrar información del pedido
                billing = order.get('billing', {})
                customer_name = f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip()
                total = order.get('total', '0')
                currency = order.get('currency', 'EUR')
                date_created = order.get('date_created', '')
                
                print(f"   👤 Cliente: {customer_name}")
                print(f"   💰 Total: {total} {currency}")
                print(f"   📅 Fecha: {date_created}")
                
                # Mostrar productos
                line_items = order.get('line_items', [])
                print(f"   📋 Productos: {len(line_items)}")
                for item in line_items[:3]:  # Mostrar primeros 3
                    name = item.get('name', 'Producto sin nombre')
                    quantity = item.get('quantity', 1)
                    print(f"      • {name} (x{quantity})")
                
                # Procesar el pedido
                result = process_woocommerce_order(order)
                
                if result['success']:
                    print(f"   ✅ {result['message']}")
                    print(f"   📍 Fecha en calendario: {result['date']}")
                    success_count += 1
                else:
                    print(f"   ❌ Error: {result.get('error', 'Error desconocido')}")
                    error_count += 1
                
                processed_count += 1
                
            except Exception as e:
                print(f"   💥 Excepción: {str(e)}")
                error_count += 1
        
        # Mostrar resultados
        print(f"\n" + "=" * 50)
        print(f"📊 RESULTADOS DEL PROCESAMIENTO")
        print(f"=" * 50)
        print(f"📦 Pedidos procesados: {processed_count}")
        print(f"✅ Exitosos: {success_count}")
        print(f"❌ Errores: {error_count}")
        
        # Verificar notas creadas
        new_notes = CalendarNote.query.filter(
            CalendarNote.title.contains('🛒 Pedido #')
        ).all()
        
        print(f"📝 Notas creadas en BD: {len(new_notes)}")
        
        # Mostrar algunas notas creadas
        print(f"\n📋 NOTAS CREADAS:")
        for note in new_notes[:3]:
            print(f"   • {note.title}")
            print(f"     📅 Fecha: {note.date_for}")
            print(f"     🎨 Color: {note.color}")
            print(f"     📄 Contenido: {note.content[:100]}...")
        
        if len(new_notes) > 3:
            print(f"   ... y {len(new_notes) - 3} más")
        
        # Verificar por fechas
        print(f"\n📅 DISTRIBUCIÓN POR FECHAS:")
        date_counts = {}
        for note in new_notes:
            date_str = note.date_for.strftime('%Y-%m-%d')
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        for date_str, count in sorted(date_counts.items()):
            print(f"   {date_str}: {count} pedidos")
        
        return success_count > 0

def main():
    """Función principal"""
    print("🚀 PRUEBA CON DATOS REALES DE WOOCOMMERCE")
    
    success = test_with_real_data()
    
    if success:
        print(f"\n🎉 ¡PRUEBA EXITOSA!")
        print(f"Los pedidos reales de WooCommerce se procesaron correctamente")
        print(f"y se guardaron como notas en el calendario.")
        print(f"\n💡 SIGUIENTE PASO:")
        print(f"1. Ejecute: python app.py")
        print(f"2. Vaya a: http://localhost:5000")
        print(f"3. Verifique que los pedidos aparezcan en el calendario")
    else:
        print(f"\n❌ LA PRUEBA FALLÓ")
        print(f"Revise los errores anteriores")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
