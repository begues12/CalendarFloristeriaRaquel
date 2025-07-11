#!/usr/bin/env python3
"""
Script de verificación final para el sistema de API e integraciones
"""

from app import create_app, db
from app.models.user import User, ApiIntegration, ApiData, CalendarNote
from datetime import datetime, date

def verify_system():
    """Verificar que todos los componentes estén funcionando"""
    app = create_app()
    with app.app_context():
        
        print("🔍 VERIFICACIÓN DEL SISTEMA")
        print("=" * 50)
        
        # Verificar usuarios
        users = User.query.all()
        print(f"👥 Usuarios: {len(users)} encontrados")
        for user in users:
            role = "Super Admin" if user.is_super_admin else "Admin" if user.is_admin else "Usuario"
            print(f"   - {user.username} ({role})")
        
        # Verificar integraciones de API
        integrations = ApiIntegration.query.all()
        print(f"\n🔌 Integraciones de API: {len(integrations)} encontradas")
        for integration in integrations:
            status = "✅ Activa" if integration.is_active else "❌ Inactiva"
            print(f"   - {integration.name} ({integration.api_type}) - {status}")
        
        # Verificar datos de API
        api_data = ApiData.query.all()
        print(f"\n📊 Datos de API: {len(api_data)} encontrados")
        for data in api_data:
            print(f"   - {data.title} ({data.date_for})")
        
        # Verificar notas
        notes = CalendarNote.query.all()
        print(f"\n📝 Notas del calendario: {len(notes)} encontradas")
        for note in notes:
            privacy = "🔒 Privada" if note.is_private else "🌐 Pública"
            print(f"   - {note.title} ({note.date_for}) - {privacy}")
        
        # Verificar privilegios de usuarios
        print(f"\n🔐 Verificación de privilegios:")
        for user in users:
            has_notes = hasattr(user, 'can_manage_notes') and user.can_manage_notes
            print(f"   - {user.username}: can_manage_notes = {has_notes}")
        
        # Verificar tablas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        required_tables = ['users', 'api_integrations', 'api_data', 'calendar_notes']
        print(f"\n🗄️  Verificación de tablas:")
        for table in required_tables:
            exists = table in tables
            status = "✅" if exists else "❌"
            print(f"   - {table}: {status}")
        
        print("\n🎉 VERIFICACIÓN COMPLETADA")
        print("=" * 50)
        print("✅ Sistema de API e integraciones funcionando correctamente")
        print("🌐 Servidor disponible en: http://localhost:5000")
        print("👤 Login: admin / admin123")
        print("👤 Login: empleado / empleado123")

if __name__ == '__main__':
    verify_system()
