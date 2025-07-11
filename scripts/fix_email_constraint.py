#!/usr/bin/env python3
"""
Script para diagnosticar y solucionar el problema de UNIQUE constraint en users.email
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, User
from config.settings import config


def diagnose_email_constraint_issue():
    """Diagnosticar el problema de constraint UNIQUE en email"""
    
    print("🔍 DIAGNÓSTICO: Problema UNIQUE constraint en users.email")
    print("=" * 60)
    
    # Crear aplicación
    config_name = os.environ.get('FLASK_CONFIG') or 'development'
    app = create_app(config[config_name])
    
    with app.app_context():
        print("\n1. 📊 Información general de usuarios:")
        users = User.query.all()
        print(f"   Total usuarios: {len(users)}")
        
        print("\n2. 📧 Análisis de emails:")
        email_counts = {}
        users_with_empty_email = []
        
        for user in users:
            email = user.email or ''  # Tratar None como string vacío
            if email in email_counts:
                email_counts[email] += 1
            else:
                email_counts[email] = 1
            
            if not email:  # Email vacío o None
                users_with_empty_email.append(user)
        
        # Mostrar emails duplicados
        print("   Emails y sus ocurrencias:")
        for email, count in email_counts.items():
            status = "❌ DUPLICADO" if count > 1 else "✅ OK"
            email_display = f"'{email}'" if email else "'[VACÍO]'"
            print(f"   - {email_display}: {count} usuario(s) {status}")
        
        print(f"\n3. 👥 Usuarios con email vacío ({len(users_with_empty_email)}):")
        for user in users_with_empty_email:
            print(f"   - ID: {user.id}, Usuario: {user.username}, Email: '{user.email}'")
        
        print(f"\n4. 📋 Detalles de todos los usuarios:")
        for user in users:
            print(f"   ID: {user.id:2d} | Usuario: {user.username:15s} | Email: '{user.email or '[None]':20s}' | Activo: {user.is_active}")
        
        return users_with_empty_email, email_counts


def fix_email_constraint_issue():
    """Solucionar el problema de constraint UNIQUE en email"""
    
    print("\n" + "=" * 60)
    print("🔧 SOLUCIÓN: Reparar constraint UNIQUE en users.email")
    print("=" * 60)
    
    config_name = os.environ.get('FLASK_CONFIG') or 'development'
    app = create_app(config[config_name])
    
    with app.app_context():
        try:
            print("\n1. 🔍 Identificando usuarios problemáticos...")
            users_with_empty_email = User.query.filter(
                (User.email == '') | (User.email.is_(None))
            ).all()
            
            print(f"   Encontrados {len(users_with_empty_email)} usuarios con email vacío/None")
            
            if len(users_with_empty_email) <= 1:
                print("   ✅ No hay problema de duplicados")
                return
            
            print("\n2. 🔧 Asignando emails únicos...")
            for i, user in enumerate(users_with_empty_email):
                if i == 0:
                    # El primer usuario puede mantener email vacío si es necesario
                    new_email = None
                    print(f"   - Usuario {user.username} (ID: {user.id}): Mantener email None")
                else:
                    # Asignar emails únicos a los demás
                    new_email = f"user{user.id}@floristeria.local"
                    print(f"   - Usuario {user.username} (ID: {user.id}): Asignar email '{new_email}'")
                
                user.email = new_email
            
            print("\n3. 💾 Guardando cambios...")
            db.session.commit()
            print("   ✅ Cambios guardados exitosamente")
            
            print("\n4. ✅ Verificación final:")
            # Verificar que no hay duplicados
            from sqlalchemy import func
            duplicates = db.session.query(User.email, func.count(User.id)).group_by(User.email).having(func.count(User.id) > 1).all()
            
            if duplicates:
                print("   ❌ Aún hay emails duplicados:")
                for email, count in duplicates:
                    print(f"      - '{email}': {count} usuarios")
            else:
                print("   ✅ No hay emails duplicados")
            
        except Exception as e:
            print(f"\n❌ Error durante la reparación: {str(e)}")
            db.session.rollback()


def show_user_management_solution():
    """Mostrar solución para el formulario de gestión de usuarios"""
    
    print("\n" + "=" * 60)
    print("💡 SOLUCIÓN PARA FORMULARIO DE GESTIÓN")
    print("=" * 60)
    
    print("""
🔧 Para evitar este error en el futuro:

1. VALIDACIÓN EN EL FORMULARIO:
   - Verificar que el email no esté vacío antes de enviar
   - Generar email único automáticamente si está vacío
   - Validar formato de email

2. LÓGICA RECOMENDADA:
   ```python
   # En lugar de enviar email vacío, generar uno único
   if not email or email.strip() == '':
       email = f"user{user_id}@floristeria.local"
   ```

3. VALIDACIÓN EN EL BACKEND:
   - Verificar unicidad antes de UPDATE
   - Manejar casos de email vacío/None
   - Transacciones con rollback

4. INTERFAZ DE USUARIO:
   - Campo email requerido en formularios
   - Validación JavaScript antes de envío
   - Mensajes de error claros
""")


if __name__ == '__main__':
    print("Iniciando diagnóstico del problema UNIQUE constraint...")
    print(f"Timestamp: {datetime.now() if 'datetime' in globals() else 'N/A'}")
    
    try:
        from datetime import datetime
        
        # Diagnóstico
        users_with_empty_email, email_counts = diagnose_email_constraint_issue()
        
        # Verificar si necesita reparación
        duplicates = [email for email, count in email_counts.items() if count > 1]
        
        if duplicates:
            print(f"\n⚠️ PROBLEMA DETECTADO: {len(duplicates)} email(s) duplicado(s)")
            response = input("\n¿Quieres reparar automáticamente? (s/n): ")
            
            if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                fix_email_constraint_issue()
            else:
                print("ℹ️ Reparación omitida por el usuario")
        else:
            print("\n✅ No se detectaron problemas de emails duplicados")
        
        # Mostrar solución para el futuro
        show_user_management_solution()
        
        print(f"\n" + "=" * 60)
        print("✅ DIAGNÓSTICO COMPLETADO")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {str(e)}")
        print(f"Verifica que el servidor esté corriendo y la BD accesible.")
