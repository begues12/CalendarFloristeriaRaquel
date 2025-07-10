#!/usr/bin/env python3
"""
Script para probar que los privilegios de admin funcionan correctamente
"""

from app import app
from models import db, User

def test_admin_privileges():
    """Probar que los admins y super admins tienen acceso completo"""
    with app.app_context():
        # Buscar usuarios admin
        admin_users = User.query.filter(
            (User.is_admin == True) | (User.is_super_admin == True)
        ).all()
        
        if not admin_users:
            print("❌ No se encontraron usuarios admin o super admin")
            return False
        
        # Lista de todos los privilegios para probar
        all_privileges = [
            'can_view_calendar',
            'can_upload_photos', 
            'can_manage_photos',
            'can_time_tracking',
            'can_view_own_reports',
            'can_view_all_reports',
            'can_manage_time_entries',
            'can_upload_documents',
            'can_view_own_documents',
            'can_view_all_documents',
            'can_manage_users',
            'can_export_data'
        ]
        
        print("🔍 Probando privilegios de administradores...")
        
        for user in admin_users:
            print(f"\n👤 Usuario: {user.username}")
            print(f"   - is_admin: {user.is_admin}")
            print(f"   - is_super_admin: {user.is_super_admin}")
            
            all_pass = True
            for privilege in all_privileges:
                has_privilege = user.has_privilege(privilege)
                status = "✅" if has_privilege else "❌"
                print(f"   - {privilege}: {status}")
                if not has_privilege:
                    all_pass = False
            
            if all_pass:
                print(f"   ✅ {user.username} tiene acceso completo como se esperaba")
            else:
                print(f"   ❌ {user.username} NO tiene acceso completo")
                return False
        
        # Probar usuario normal para comparar
        normal_users = User.query.filter(
            (User.is_admin == False) & (User.is_super_admin == False) & 
            (User.username != 'superadmin')
        ).limit(3).all()
        
        if normal_users:
            print(f"\n🔍 Comparando con usuarios normales...")
            for user in normal_users:
                print(f"\n👤 Usuario normal: {user.username}")
                restricted_count = 0
                for privilege in all_privileges:
                    has_privilege = user.has_privilege(privilege)
                    if not has_privilege:
                        restricted_count += 1
                
                print(f"   - Privilegios restringidos: {restricted_count}/{len(all_privileges)}")
                if restricted_count > 0:
                    print(f"   ✅ Usuario normal correctamente restringido")
                else:
                    print(f"   ⚠️  Usuario normal tiene todos los privilegios")
        
        print(f"\n✅ Prueba completada: Los administradores tienen acceso completo")
        return True

if __name__ == "__main__":
    test_admin_privileges()
