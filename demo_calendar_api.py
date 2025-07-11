#!/usr/bin/env python3
"""
Ejemplo de uso de la API de notas del calendario
===============================================

Este script demuestra cómo usar los nuevos endpoints API para:
1. Añadir notas al calendario
2. Obtener notas de una fecha
3. Actualizar notas existentes
4. Eliminar notas
5. Verificar si una fecha tiene notas

IMPORTANTE: Debes estar autenticado en la aplicación para usar estos endpoints.
"""

import requests
import json
from datetime import datetime, date

# Configuración de la API
BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

def login(username, password):
    """Iniciar sesión en la aplicación"""
    print(f"🔐 Iniciando sesión como {username}...")
    
    # Primero obtenemos la página de login para obtener el token CSRF si es necesario
    login_page = SESSION.get(f"{BASE_URL}/auth/login")
    
    # Realizar login
    response = SESSION.post(f"{BASE_URL}/auth/login", data={
        'username': username,
        'password': password
    })
    
    if response.status_code == 200 and "Bienvenido" in response.text:
        print("✅ Login exitoso")
        return True
    else:
        print("❌ Error en login")
        return False

def add_note_to_calendar(date_str, title, content=None, color="#ffc107", priority="normal"):
    """Añadir una nota al calendario"""
    print(f"📝 Añadiendo nota para {date_str}: {title}")
    
    note_data = {
        "date_for": date_str,
        "title": title,
        "content": content,
        "color": color,
        "priority": priority,
        "is_private": False,
        "is_reminder": False
    }
    
    response = SESSION.post(
        f"{BASE_URL}/api/notes",
        json=note_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Nota creada con ID: {result['note']['id']}")
        return result['note']
    else:
        print(f"❌ Error: {response.json()}")
        return None

def add_quick_note(date_str, text, color="#ffc107"):
    """Añadir una nota rápida al calendario"""
    print(f"⚡ Añadiendo nota rápida para {date_str}: {text}")
    
    response = SESSION.post(
        f"{BASE_URL}/api/calendar/{date_str}/quick-note",
        json={
            "text": text,
            "color": color
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Nota rápida creada con ID: {result['note']['id']}")
        return result['note']
    else:
        print(f"❌ Error: {response.json()}")
        return None

def get_notes_for_date(date_str):
    """Obtener todas las notas de una fecha"""
    print(f"📋 Obteniendo notas para {date_str}")
    
    response = SESSION.get(f"{BASE_URL}/api/notes/{date_str}")
    
    if response.status_code == 200:
        result = response.json()
        notes = result['notes']
        print(f"✅ Encontradas {len(notes)} notas")
        
        for note in notes:
            print(f"  - [{note['priority'].upper()}] {note['title']}")
            if note['content']:
                print(f"    {note['content'][:50]}...")
        
        return notes
    else:
        print(f"❌ Error: {response.json()}")
        return []

def update_note(note_id, **updates):
    """Actualizar una nota existente"""
    print(f"✏️  Actualizando nota {note_id}")
    
    response = SESSION.put(
        f"{BASE_URL}/api/notes/{note_id}",
        json=updates,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Nota actualizada: {result['note']['title']}")
        return result['note']
    else:
        print(f"❌ Error: {response.json()}")
        return None

def delete_note(note_id):
    """Eliminar una nota"""
    print(f"🗑️  Eliminando nota {note_id}")
    
    response = SESSION.delete(f"{BASE_URL}/api/notes/{note_id}")
    
    if response.status_code == 200:
        print("✅ Nota eliminada")
        return True
    else:
        print(f"❌ Error: {response.json()}")
        return False

def check_if_date_has_notes(date_str):
    """Verificar si una fecha tiene notas"""
    print(f"🔍 Verificando si {date_str} tiene notas...")
    
    response = SESSION.get(f"{BASE_URL}/api/calendar/{date_str}/has-notes")
    
    if response.status_code == 200:
        result = response.json()
        if result['has_notes']:
            print(f"✅ La fecha tiene {result['note_count']} nota(s)")
        else:
            print("ℹ️  La fecha no tiene notas")
        return result
    else:
        print(f"❌ Error: {response.json()}")
        return None

def demo_api_usage():
    """Demostración completa del uso de la API"""
    print("🚀 === DEMO DE API DE NOTAS DEL CALENDARIO ===\n")
    
    # 1. Login
    if not login("admin", "admin123"):  # Cambia por tus credenciales
        print("No se pudo iniciar sesión. Verifica tus credenciales.")
        return
    
    # 2. Fecha para las pruebas
    today = date.today()
    test_date = today.strftime('%Y-%m-%d')
    
    print(f"\n📅 Trabajando con la fecha: {test_date}\n")
    
    # 3. Verificar si ya hay notas
    check_if_date_has_notes(test_date)
    
    # 4. Añadir nota completa
    note1 = add_note_to_calendar(
        test_date,
        "Reunión importante",
        "Revisar el progreso del proyecto y definir próximos pasos",
        "#dc3545",  # Rojo
        "high"
    )
    
    # 5. Añadir nota rápida
    note2 = add_quick_note(
        test_date,
        "Recordar llamar al cliente para confirmar la cita de mañana",
        "#28a745"  # Verde
    )
    
    # 6. Obtener todas las notas de la fecha
    print("\n" + "="*50)
    notes = get_notes_for_date(test_date)
    
    # 7. Actualizar una nota
    if note1:
        print("\n" + "="*50)
        update_note(note1['id'], {
            "priority": "urgent",
            "color": "#6f42c1",
            "content": "ACTUALIZADO: Reunión MUY importante - preparar presentación"
        })
    
    # 8. Verificar cambios
    print("\n" + "="*50)
    get_notes_for_date(test_date)
    
    # 9. Verificar contador de notas
    print("\n" + "="*50)
    check_if_date_has_notes(test_date)
    
    # 10. Opcional: Eliminar notas (descomenta si quieres probar)
    # if note2:
    #     print("\n" + "="*50)
    #     delete_note(note2['id'])
    #     check_if_date_has_notes(test_date)
    
    print("\n🎉 ¡Demo completada!")

if __name__ == "__main__":
    demo_api_usage()
