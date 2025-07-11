#!/usr/bin/env python3
"""
Demo de APIs de Notas del Calendario
===================================

Este script demuestra cómo usar las APIs de notas del calendario
que permiten añadir eventos/notas cuando se selecciona una fecha.
"""

import requests
import json
from datetime import datetime, date, timedelta

class CalendarNotesDemo:
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
    
    def add_quick_note(self, date_str, text, color='#ffc107', priority='normal', is_private=False):
        """Añadir una nota rápida a una fecha"""
        if not self.logged_in:
            print("❌ Debe hacer login primero")
            return None
        
        try:
            data = {
                'text': text,
                'color': color,
                'priority': priority,
                'is_private': is_private
            }
            
            response = self.session.post(
                f'{self.base_url}/api/calendar/{date_str}/quick-note',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if response.status_code == 201 and result.get('success'):
                print(f"✅ Nota rápida añadida para {date_str}: {text[:50]}...")
                return result['note']
            else:
                print(f"❌ Error añadiendo nota rápida: {result.get('error', 'Error desconocido')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def add_detailed_note(self, date_str, title, content=None, color='#ffc107', 
                         priority='normal', is_private=False, is_reminder=False, 
                         reminder_time=None):
        """Añadir una nota detallada a una fecha"""
        if not self.logged_in:
            print("❌ Debe hacer login primero")
            return None
        
        try:
            data = {
                'date_for': date_str,
                'title': title,
                'content': content,
                'color': color,
                'priority': priority,
                'is_private': is_private,
                'is_reminder': is_reminder,
                'reminder_time': reminder_time
            }
            
            response = self.session.post(
                f'{self.base_url}/api/notes',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if response.status_code == 201 and result.get('success'):
                print(f"✅ Nota detallada añadida para {date_str}: {title}")
                return result['note']
            else:
                print(f"❌ Error añadiendo nota: {result.get('error', 'Error desconocido')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_notes_for_date(self, date_str):
        """Obtener todas las notas de una fecha"""
        if not self.logged_in:
            print("❌ Debe hacer login primero")
            return None
        
        try:
            response = self.session.get(f'{self.base_url}/api/notes/{date_str}')
            result = response.json()
            
            if response.status_code == 200:
                notes = result.get('notes', [])
                print(f"📋 Notas para {date_str}: {len(notes)} encontradas")
                for note in notes:
                    print(f"   - {note['title']} ({note['priority']}) - {note['creator']}")
                return notes
            else:
                print(f"❌ Error obteniendo notas: {result.get('error', 'Error desconocido')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def check_date_has_notes(self, date_str):
        """Verificar si una fecha tiene notas"""
        if not self.logged_in:
            print("❌ Debe hacer login primero")
            return None
        
        try:
            response = self.session.get(f'{self.base_url}/api/calendar/{date_str}/has-notes')
            result = response.json()
            
            if response.status_code == 200:
                has_notes = result.get('has_notes', False)
                note_count = result.get('note_count', 0)
                print(f"🔍 {date_str}: {'Tiene' if has_notes else 'No tiene'} notas ({note_count})")
                return result
            else:
                print(f"❌ Error verificando notas: {result.get('error', 'Error desconocido')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def update_note(self, note_id, **updates):
        """Actualizar una nota existente"""
        if not self.logged_in:
            print("❌ Debe hacer login primero")
            return None
        
        try:
            response = self.session.put(
                f'{self.base_url}/api/notes/{note_id}',
                json=updates,
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                print(f"✅ Nota {note_id} actualizada")
                return result['note']
            else:
                print(f"❌ Error actualizando nota: {result.get('error', 'Error desconocido')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def delete_note(self, note_id):
        """Eliminar una nota"""
        if not self.logged_in:
            print("❌ Debe hacer login primero")
            return None
        
        try:
            response = self.session.delete(f'{self.base_url}/api/notes/{note_id}')
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                print(f"✅ Nota {note_id} eliminada")
                return True
            else:
                print(f"❌ Error eliminando nota: {result.get('error', 'Error desconocido')}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def demo_complete_workflow(self):
        """Demostrar el flujo completo de trabajo con notas"""
        print("\n🚀 Iniciando demo completo de notas del calendario")
        print("=" * 60)
        
        # Fechas para la demo
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        today_str = today.strftime('%Y-%m-%d')
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        next_week_str = next_week.strftime('%Y-%m-%d')
        
        print(f"\n📅 Trabajando con fechas:")
        print(f"   - Hoy: {today_str}")
        print(f"   - Mañana: {tomorrow_str}")
        print(f"   - Próxima semana: {next_week_str}")
        
        # 1. Añadir notas rápidas
        print(f"\n1️⃣ Añadiendo notas rápidas...")
        self.add_quick_note(today_str, "Reunión con proveedor de flores", color='#007bff', priority='high')
        self.add_quick_note(tomorrow_str, "Entrega pedido boda García", color='#dc3545', priority='urgent')
        
        # 2. Añadir notas detalladas
        print(f"\n2️⃣ Añadiendo notas detalladas...")
        note1 = self.add_detailed_note(
            today_str,
            "Revisión de inventario",
            "Revisar stock de rosas rojas y blancas para el fin de semana",
            color='#28a745',
            priority='normal',
            is_reminder=True,
            reminder_time='14:00'
        )
        
        note2 = self.add_detailed_note(
            next_week_str,
            "Evento corporativo",
            "Preparar 50 centros de mesa para evento de empresa XYZ",
            color='#6f42c1',
            priority='high',
            is_private=False
        )
        
        # 3. Verificar qué fechas tienen notas
        print(f"\n3️⃣ Verificando notas por fecha...")
        self.check_date_has_notes(today_str)
        self.check_date_has_notes(tomorrow_str)
        self.check_date_has_notes(next_week_str)
        
        # 4. Obtener notas detalladas
        print(f"\n4️⃣ Obteniendo listado de notas...")
        self.get_notes_for_date(today_str)
        self.get_notes_for_date(tomorrow_str)
        self.get_notes_for_date(next_week_str)
        
        # 5. Actualizar una nota (si se creó correctamente)
        if note1 and note1.get('id'):
            print(f"\n5️⃣ Actualizando nota...")
            self.update_note(note1['id'], 
                           title="Revisión de inventario - COMPLETADO",
                           priority='low')
        
        print(f"\n✅ Demo completado exitosamente!")
        print("=" * 60)


def main():
    """Función principal"""
    print("🌸 Demo de APIs de Notas del Calendario - Floristería Raquel")
    print("=" * 70)
    
    # Crear instancia del demo
    demo = CalendarNotesDemo()
    
    # Hacer login
    if not demo.login():
        print("❌ No se pudo hacer login. Verifique que el servidor esté ejecutándose.")
        return
    
    # Ejecutar demo completo
    demo.demo_complete_workflow()
    
    print(f"\n💡 Consejos para usar las APIs:")
    print("  - Use /api/calendar/<fecha>/quick-note para notas rápidas")
    print("  - Use /api/notes para notas detalladas con más opciones")
    print("  - Use /api/notes/<fecha> para ver todas las notas de una fecha")
    print("  - Use /api/calendar/<fecha>/has-notes para verificar si hay notas")
    print("  - Todas las APIs requieren autenticación de usuario")
    print("  - Los usuarios solo pueden editar sus propias notas (excepto admins)")


if __name__ == '__main__':
    main()
