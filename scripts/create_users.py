#!/usr/bin/env python3
"""
Script para crear usuarios iniciales en el sistema
"""

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_initial_users():
    """Crear usuarios iniciales del sistema"""
    app = create_app()
    with app.app_context():
        
        # Verificar si ya existe el admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Crear usuario administrador
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@floristeria.com',
                full_name='Administrador',
                is_admin=True,
                is_super_admin=True,
                is_active=True,
                must_change_password=False,
                can_view_calendar=True,
                can_upload_photos=True,
                can_manage_photos=True,
                can_time_tracking=True,
                can_view_own_reports=True,
                can_view_all_reports=True,
                can_manage_time_entries=True,
                can_upload_documents=True,
                can_view_own_documents=True,
                can_view_all_documents=True,
                can_manage_users=True,
                can_export_data=True,
                can_manage_notes=True
            )
            db.session.add(admin)
            print("✅ Usuario admin creado")
        else:
            print("ℹ️  Usuario admin ya existe")
            
        # Verificar si ya existe un usuario de prueba
        test_user = User.query.filter_by(username='empleado').first()
        if not test_user:
            # Crear usuario empleado
            test_user = User(
                username='empleado',
                password_hash=generate_password_hash('empleado123'),
                email='empleado@floristeria.com',
                full_name='Empleado de Prueba',
                is_admin=False,
                is_super_admin=False,
                is_active=True,
                must_change_password=False,
                can_view_calendar=True,
                can_upload_photos=True,
                can_manage_photos=False,
                can_time_tracking=True,
                can_view_own_reports=True,
                can_view_all_reports=False,
                can_manage_time_entries=False,
                can_upload_documents=True,
                can_view_own_documents=True,
                can_view_all_documents=False,
                can_manage_users=False,
                can_export_data=False,
                can_manage_notes=True
            )
            db.session.add(test_user)
            print("✅ Usuario empleado creado")
        else:
            print("ℹ️  Usuario empleado ya existe")
            
        db.session.commit()
        print("🎉 Usuarios iniciales creados/verificados correctamente")
        
        # Mostrar usuarios disponibles
        users = User.query.all()
        print("\n👥 Usuarios disponibles:")
        for user in users:
            role = "Super Admin" if user.is_super_admin else "Admin" if user.is_admin else "Usuario"
            print(f"  - {user.username} ({user.full_name}) - {role}")

if __name__ == '__main__':
    create_initial_users()
