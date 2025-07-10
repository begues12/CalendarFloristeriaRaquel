#!/usr/bin/env python3
"""
Script para aplicar privilegios por defecto a usuarios existentes
"""

from flask import Flask
from models import db, User

def create_app():
    """Crear instancia de la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///floristeria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'temp-key-for-script'
    
    db.init_app(app)
    return app

def apply_default_privileges():
    """Aplicar privilegios por defecto a todos los usuarios existentes"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        print("🔧 APLICANDO PRIVILEGIOS POR DEFECTO")
        print("=" * 40)
        
        updated_count = 0
        
        for user in users:
            # Solo actualizar si no tiene privilegios específicos ya configurados
            if user.can_view_calendar is None:
                print(f"\n👤 Actualizando usuario: {user.username}")
                
                user.set_default_privileges()
                
                # Los admins tienen todos los privilegios
                if user.is_admin:
                    user.can_manage_photos = True
                    user.can_view_all_reports = True
                    user.can_manage_time_entries = True
                    user.can_view_all_documents = True
                    user.can_manage_users = True
                    user.can_export_data = True
                    print("   🛡️ Privilegios de administrador aplicados")
                else:
                    print("   ✅ Privilegios básicos aplicados")
                
                updated_count += 1
            else:
                print(f"\n👤 {user.username}: Ya tiene privilegios configurados, saltando...")
        
        if updated_count > 0:
            try:
                db.session.commit()
                print(f"\n✅ {updated_count} usuarios actualizados correctamente")
            except Exception as e:
                print(f"\n❌ Error al guardar cambios: {str(e)}")
                db.session.rollback()
        else:
            print("\nℹ️ No se necesitaron actualizaciones")
        
        print("\n" + "=" * 40)
        print("🎯 RESUMEN DE PRIVILEGIOS POR USUARIO:")
        print("=" * 40)
        
        for user in User.query.all():
            print(f"\n👤 {user.username}:")
            print(f"   📅 Ver calendario: {user.can_view_calendar}")
            print(f"   📷 Subir fotos: {user.can_upload_photos}")
            print(f"   🕒 Fichaje: {user.can_time_tracking}")
            print(f"   📁 Documentos propios: {user.can_upload_documents}")
            if user.is_admin:
                print("   🛡️ ADMINISTRADOR - Todos los privilegios")

if __name__ == "__main__":
    apply_default_privileges()
