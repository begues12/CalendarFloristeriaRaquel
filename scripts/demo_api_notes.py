#!/usr/bin/env python3
"""
Script para agregar integraciones de API de ejemplo
"""

import sys
import os
import json
from datetime import datetime, date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import db, User, ApiIntegration, ApiData, CalendarNote

def create_example_integrations():
    app = create_app()
    
    with app.app_context():
        print("Creando integraciones de API de ejemplo...")
        
        # Obtener admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("❌ Usuario admin no encontrado")
            return
        
        # 1. Integración de clima de ejemplo
        weather_config = {
            "data_path": "forecast.forecastday",
            "date_field": "date",
            "title_field": "day.condition.text",
            "temp_field": "day.maxtemp_c",
            "icon": "fas fa-cloud-sun",
            "color": "#87CEEB"
        }
        
        weather_integration = ApiIntegration(
            name="Pronóstico del Tiempo",
            api_type="weather",
            url="https://api.weatherapi.com/v1/forecast.json?key=demo&q=Madrid&days=7",
            mapping_config=json.dumps(weather_config),
            refresh_interval=180,  # 3 horas
            is_active=True,
            created_by=admin.id
        )
        
        # 2. Integración de tareas de ejemplo
        tasks_config = {
            "data_path": "tasks",
            "date_field": "due_date",
            "title_field": "title",
            "status_field": "status",
            "icon": "fas fa-tasks",
            "color": "#ffc107"
        }
        
        tasks_integration = ApiIntegration(
            name="Tareas Pendientes",
            api_type="tasks",
            url="https://jsonplaceholder.typicode.com/todos",
            mapping_config=json.dumps(tasks_config),
            refresh_interval=60,
            is_active=True,
            created_by=admin.id
        )
        
        # 3. Integración personalizada de ejemplo
        custom_config = {
            "data_path": "events",
            "date_field": "date",
            "title_field": "name",
            "description_field": "description",
            "icon": "fas fa-calendar-alt",
            "color": "#28a745"
        }
        
        custom_integration = ApiIntegration(
            name="Eventos Locales",
            api_type="events",
            url="https://api.ejemplo.com/eventos",
            mapping_config=json.dumps(custom_config),
            refresh_interval=240,  # 4 horas
            is_active=False,  # Desactivada por defecto (URL ficticia)
            created_by=admin.id
        )
        
        # Verificar si ya existen
        existing = ApiIntegration.query.filter_by(created_by=admin.id).first()
        if existing:
            print("✅ Ya existen integraciones de ejemplo")
            return
        
        # Agregar a la base de datos
        db.session.add(weather_integration)
        db.session.add(tasks_integration)
        db.session.add(custom_integration)
        db.session.commit()
        
        print("✅ Integraciones de ejemplo creadas:")
        print("   - Pronóstico del Tiempo (activa)")
        print("   - Tareas Pendientes (activa)")
        print("   - Eventos Locales (inactiva)")
        
def create_example_notes():
    app = create_app()
    
    with app.app_context():
        print("\nCreando notas de ejemplo...")
        
        # Obtener admin user
        admin = User.query.filter_by(username='admin').first()
        
        # Crear algunas notas de ejemplo para días futuros
        today = date.today()
        
        notes = [
            {
                'date_offset': 1,
                'title': 'Reunión con proveedor',
                'content': 'Revisar catálogo de flores de temporada\nNegociar precios para el próximo mes',
                'priority': 'high',
                'color': '#fd7e14',
                'is_reminder': True,
                'reminder_time': '10:00'
            },
            {
                'date_offset': 2,
                'title': 'Pedido especial',
                'content': 'Arreglo floral para boda\n- 50 rosas rojas\n- Follaje variado\n- Lazo dorado',
                'priority': 'urgent',
                'color': '#dc3545',
                'is_reminder': True,
                'reminder_time': '09:00'
            },
            {
                'date_offset': 3,
                'title': 'Inventario semanal',
                'content': 'Revisar stock de flores y materiales',
                'priority': 'normal',
                'color': '#007bff',
                'is_reminder': False
            },
            {
                'date_offset': 5,
                'title': 'Curso de arreglos',
                'content': 'Taller de arreglos navideños\nLocal: Centro Cultural\nHorario: 16:00 - 18:00',
                'priority': 'low',
                'color': '#28a745',
                'is_reminder': True,
                'reminder_time': '15:30'
            }
        ]
        
        # Verificar si ya existen notas
        existing_notes = CalendarNote.query.filter_by(created_by=admin.id).first()
        if existing_notes:
            print("✅ Ya existen notas de ejemplo")
            return
        
        for note_data in notes:
            from datetime import timedelta, time
            note_date = today + timedelta(days=note_data['date_offset'])
            reminder_time = None
            
            if note_data['is_reminder'] and note_data.get('reminder_time'):
                hour, minute = map(int, note_data['reminder_time'].split(':'))
                reminder_time = time(hour, minute)
            
            note = CalendarNote(
                date_for=note_date,
                title=note_data['title'],
                content=note_data['content'],
                priority=note_data['priority'],
                color=note_data['color'],
                is_reminder=note_data['is_reminder'],
                reminder_time=reminder_time,
                is_private=False,
                created_by=admin.id
            )
            
            db.session.add(note)
        
        db.session.commit()
        print(f"✅ {len(notes)} notas de ejemplo creadas para los próximos días")

def create_example_api_data():
    app = create_app()
    
    with app.app_context():
        print("\nCreando datos de API de ejemplo...")
        
        # Buscar integración de tareas
        tasks_integration = ApiIntegration.query.filter_by(api_type='tasks', is_active=True).first()
        if not tasks_integration:
            print("⚠️ No se encontró integración de tareas activa")
            return
        
        # Crear algunos datos de ejemplo
        from datetime import timedelta
        today = date.today()
        
        api_data_examples = [
            {
                'date_offset': 0,
                'title': 'Actualizar inventario',
                'description': 'Revisar stock de flores frescas',
                'icon': 'fas fa-clipboard-list',
                'color': '#17a2b8'
            },
            {
                'date_offset': 1,
                'title': 'Entrega pedido López',
                'description': 'Ramo de novia - Dirección: Calle Mayor 45',
                'icon': 'fas fa-truck',
                'color': '#28a745'
            },
            {
                'date_offset': 2,
                'title': 'Reposición de materiales',
                'description': 'Comprar cintas, papel de regalo, oasis',
                'icon': 'fas fa-shopping-cart',
                'color': '#ffc107'
            }
        ]
        
        # Verificar si ya existen datos
        existing_data = ApiData.query.filter_by(integration_id=tasks_integration.id).first()
        if existing_data:
            print("✅ Ya existen datos de API de ejemplo")
            return
        
        for data in api_data_examples:
            api_date = today + timedelta(days=data['date_offset'])
            
            api_data = ApiData(
                integration_id=tasks_integration.id,
                date_for=api_date,
                title=data['title'],
                description=data['description'],
                icon=data['icon'],
                color=data['color'],
                data_json=json.dumps({'example': True, 'type': 'task'}),
                is_visible=True
            )
            
            db.session.add(api_data)
        
        db.session.commit()
        print(f"✅ {len(api_data_examples)} elementos de API de ejemplo creados")

if __name__ == '__main__':
    print("🌸 CREANDO DATOS DE EJEMPLO PARA API Y NOTAS")
    print("=" * 50)
    
    create_example_integrations()
    create_example_notes()
    create_example_api_data()
    
    print("\n" + "=" * 50)
    print("✅ DATOS DE EJEMPLO CREADOS EXITOSAMENTE")
    print("\n📋 Lo que puedes hacer ahora:")
    print("   1. Ve al calendario para ver las notas y datos de API")
    print("   2. Accede a 'APIs' desde el panel de admin")
    print("   3. Crea nuevas integraciones y notas")
    print("   4. Prueba la sincronización de APIs")
