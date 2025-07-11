"""
Script de diagnóstico para verificar el flujo completo de WooCommerce → Base de Datos → Calendario
"""

import os
import sys
import json
from datetime import datetime, date, timedelta

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from app.models.user import CalendarNote, User, ApiIntegration
    from app.models import db
    from app.blueprints.calendar.routes import process_woocommerce_order
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrese de que esté en el directorio raíz del proyecto")
    sys.exit(1)

def diagnose_system():
    """Diagnóstico completo del sistema"""
    
    print("🔍 DIAGNÓSTICO DEL SISTEMA WOOCOMMERCE-CALENDAR")
    print("=" * 60)
    
    # Crear contexto de aplicación
    app = create_app()
    
    with app.app_context():
        # 1. Verificar conexión a base de datos
        print("\n1️⃣ VERIFICANDO BASE DE DATOS...")
        try:
            db.engine.execute('SELECT 1')
            print("✅ Conexión a base de datos exitosa")
        except Exception as e:
            print(f"❌ Error conectando a base de datos: {e}")
            return False
        
        # 2. Verificar tablas
        print("\n2️⃣ VERIFICANDO TABLAS...")
        try:
            users_count = User.query.count()
            notes_count = CalendarNote.query.count()
            integrations_count = ApiIntegration.query.count()
            
            print(f"✅ Tabla users: {users_count} registros")
            print(f"✅ Tabla calendar_notes: {notes_count} registros")
            print(f"✅ Tabla api_integrations: {integrations_count} registros")
        except Exception as e:
            print(f"❌ Error accediendo a tablas: {e}")
            return False
        
        # 3. Verificar usuario admin
        print("\n3️⃣ VERIFICANDO USUARIOS...")
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            print(f"✅ Usuario admin encontrado: {admin_user.username}")
        else:
            print("⚠️ No se encontró usuario admin")
            any_user = User.query.first()
            if any_user:
                print(f"ℹ️ Usando usuario: {any_user.username}")
            else:
                print("❌ No hay usuarios en el sistema")
                return False
        
        # 4. Probar procesamiento de pedido
        print("\n4️⃣ PROBANDO PROCESAMIENTO DE PEDIDO...")
        test_order = {
            "id": 99999,
            "status": "processing",
            "total": "150.75",
            "currency": "EUR",
            "date_created": date.today().isoformat(),
            "billing": {
                "first_name": "Test",
                "last_name": "Diagnóstico",
                "email": "test@diagnostico.com",
                "phone": "+34 999 888 777"
            },
            "line_items": [
                {"name": "Ramo de diagnóstico", "quantity": 1},
                {"name": "Prueba de sistema", "quantity": 2}
            ]
        }
        
        # Eliminar pedido de prueba anterior si existe
        existing_test = CalendarNote.query.filter(
            CalendarNote.title.contains(f"Pedido #{test_order['id']}")
        ).first()
        if existing_test:
            db.session.delete(existing_test)
            db.session.commit()
            print("🗑️ Eliminado pedido de prueba anterior")
        
        # Procesar pedido de prueba
        result = process_woocommerce_order(test_order)
        
        if result['success']:
            print(f"✅ Pedido procesado exitosamente: {result['message']}")
            print(f"   📅 Fecha: {result['date']}")
            print(f"   📝 Acción: {result['action']}")
        else:
            print(f"❌ Error procesando pedido: {result.get('error', 'Error desconocido')}")
            return False
        
        # 5. Verificar que el pedido se guardó
        print("\n5️⃣ VERIFICANDO GUARDADO EN BASE DE DATOS...")
        saved_note = CalendarNote.query.filter(
            CalendarNote.title.contains(f"Pedido #{test_order['id']}")
        ).first()
        
        if saved_note:
            print("✅ Pedido encontrado en base de datos:")
            print(f"   📝 Título: {saved_note.title}")
            print(f"   📅 Fecha: {saved_note.date_for}")
            print(f"   🎨 Color: {saved_note.color}")
            print(f"   📊 Prioridad: {saved_note.priority}")
            print(f"   👤 Creado por: {saved_note.created_by}")
            print(f"   📄 Contenido: {saved_note.content[:100]}...")
        else:
            print("❌ Pedido no encontrado en base de datos")
            return False
        
        # 6. Verificar notas de hoy
        print("\n6️⃣ VERIFICANDO NOTAS DE HOY...")
        today = date.today()
        today_notes = CalendarNote.query.filter_by(date_for=today).all()
        
        print(f"📋 Notas para {today.strftime('%Y-%m-%d')}: {len(today_notes)}")
        for note in today_notes:
            print(f"   • {note.title} (Color: {note.color})")
        
        # 7. Verificar integraciones WooCommerce
        print("\n7️⃣ VERIFICANDO INTEGRACIONES WOOCOMMERCE...")
        wc_integrations = ApiIntegration.query.filter_by(api_type='woocommerce').all()
        
        if wc_integrations:
            print(f"✅ Integraciones WooCommerce encontradas: {len(wc_integrations)}")
            for integration in wc_integrations:
                status = "Activa" if integration.is_active else "Inactiva"
                print(f"   • {integration.name} ({status})")
        else:
            print("ℹ️ No hay integraciones WooCommerce configuradas")
        
        # 8. Simulacr datos para el calendario
        print("\n8️⃣ SIMULANDO DATOS PARA CALENDARIO...")
        
        # Crear datos de ejemplo para diferentes días
        sample_dates = [
            date.today() - timedelta(days=2),
            date.today() - timedelta(days=1),
            date.today(),
            date.today() + timedelta(days=1)
        ]
        
        sample_orders = [
            {
                "id": 88881,
                "status": "pending",
                "total": "89.99",
                "currency": "EUR",
                "billing": {"first_name": "María", "last_name": "García"},
                "line_items": [{"name": "Ramo primaveral", "quantity": 1}]
            },
            {
                "id": 88882,
                "status": "completed",
                "total": "125.50",
                "currency": "EUR",
                "billing": {"first_name": "Juan", "last_name": "López"},
                "line_items": [{"name": "Centro de mesa", "quantity": 3}]
            },
            {
                "id": 88883,
                "status": "processing",
                "total": "200.00",
                "currency": "EUR",
                "billing": {"first_name": "Ana", "last_name": "Martín"},
                "line_items": [{"name": "Decoración evento", "quantity": 1}]
            }
        ]
        
        for i, (sample_date, order) in enumerate(zip(sample_dates[:3], sample_orders)):
            order['date_created'] = sample_date.isoformat()
            
            # Eliminar si ya existe
            existing = CalendarNote.query.filter(
                CalendarNote.title.contains(f"Pedido #{order['id']}")
            ).first()
            if existing:
                db.session.delete(existing)
            
            result = process_woocommerce_order(order)
            if result['success']:
                print(f"   ✅ Pedido #{order['id']} creado para {sample_date}")
            else:
                print(f"   ❌ Error creando pedido #{order['id']}: {result.get('error')}")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DEL DIAGNÓSTICO")
        
        # Contar notas totales
        total_notes = CalendarNote.query.count()
        woocommerce_notes = CalendarNote.query.filter(
            CalendarNote.title.contains('🛒 Pedido #')
        ).count()
        
        print(f"📝 Total de notas en sistema: {total_notes}")
        print(f"🛒 Notas de WooCommerce: {woocommerce_notes}")
        
        # Limpiar pedidos de prueba
        print("\n🧹 LIMPIANDO DATOS DE PRUEBA...")
        test_notes = CalendarNote.query.filter(
            CalendarNote.title.contains('Pedido #99999')
        ).all()
        for note in test_notes:
            db.session.delete(note)
        db.session.commit()
        print("✅ Datos de prueba eliminados")
        
        return True

def main():
    """Función principal"""
    try:
        success = diagnose_system()
        
        if success:
            print("\n🎉 DIAGNÓSTICO COMPLETADO EXITOSAMENTE")
            print("\n💡 PRÓXIMOS PASOS:")
            print("1. Ejecute la aplicación: python app.py")
            print("2. Vaya al calendario: http://localhost:5000")
            print("3. Configure WooCommerce: http://localhost:5000/woocommerce/config")
            print("4. Pruebe sincronización manual")
            print("5. Verifique que los pedidos aparezcan en el calendario")
        else:
            print("\n❌ SE ENCONTRARON PROBLEMAS EN EL DIAGNÓSTICO")
            print("Revise los errores anteriores y corrija antes de continuar")
        
        return success
        
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO EN DIAGNÓSTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
