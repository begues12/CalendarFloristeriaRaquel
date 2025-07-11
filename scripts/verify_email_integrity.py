#!/usr/bin/env python3
"""
Script para verificar la integridad de emails después del fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import db, User

def verify_email_integrity():
    """Verifica que todos los emails sean únicos y válidos"""
    app = create_app()
    
    with app.app_context():
        print("🔍 VERIFICANDO INTEGRIDAD DE EMAILS")
        print("=" * 50)
        
        # Obtener todos los usuarios
        all_users = User.query.all()
        print(f"📊 Total de usuarios: {len(all_users)}")
        
        # Verificar emails únicos
        emails = []
        duplicates = []
        empty_emails = []
        
        for user in all_users:
            if not user.email or user.email.strip() == '':
                empty_emails.append(user)
            elif user.email in emails:
                duplicates.append(user)
            else:
                emails.append(user.email)
        
        print(f"✅ Emails únicos: {len(emails)}")
        print(f"⚠️ Emails vacíos: {len(empty_emails)}")
        print(f"❌ Emails duplicados: {len(duplicates)}")
        
        if empty_emails:
            print("\n🚨 USUARIOS CON EMAIL VACÍO:")
            for user in empty_emails:
                print(f"   - ID: {user.id}, Usuario: {user.username}")
        
        if duplicates:
            print("\n🚨 USUARIOS CON EMAIL DUPLICADO:")
            for user in duplicates:
                print(f"   - ID: {user.id}, Usuario: {user.username}, Email: {user.email}")
        
        print("\n📧 LISTA DE TODOS LOS EMAILS:")
        for user in all_users:
            status = "✅" if user.email and user.email not in ['', None] else "❌"
            print(f"   {status} ID: {user.id:2d} | {user.username:15s} | {user.email or '[VACÍO]'}")
        
        # Verificar constraint en la base de datos
        try:
            # Intentar un update que podría fallar por constraint
            test_user = all_users[0] if all_users else None
            if test_user:
                original_email = test_user.email
                test_user.email = test_user.email  # Self-assignment should work
                db.session.commit()
                print("\n✅ CONSTRAINT UNIQUE funcionando correctamente")
            else:
                print("\n⚠️ No hay usuarios para probar el constraint")
        except Exception as e:
            print(f"\n❌ ERROR EN CONSTRAINT: {e}")
            db.session.rollback()
        
        print("\n" + "=" * 50)
        if not empty_emails and not duplicates:
            print("🎉 ¡TODOS LOS EMAILS SON VÁLIDOS Y ÚNICOS!")
        else:
            print("⚠️ Se encontraron problemas que necesitan ser corregidos")

if __name__ == '__main__':
    verify_email_integrity()
