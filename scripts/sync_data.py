#!/usr/bin/env python3
"""
Script para sincronización de datos entre desarrollo y producción
Permite exportar e importar datos manteniendo bases de datos separadas
"""

import os
import sys
import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Agregar el directorio actual al path para importar la app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def export_data():
    """Exporta todos los datos a archivos JSON para sincronización"""
    from app import app
    from models import db, User, Photo, TimeEntry, UserDocument
    
    print("🔄 Exportando datos desde la base de datos...")
    
    with app.app_context():
        # Crear carpeta de exportación
        export_folder = Path("data_export")
        export_folder.mkdir(exist_ok=True)
        
        # Exportar usuarios
        users = User.query.all()
        users_data = []
        for user in users:
            users_data.append({
                'username': user.username,
                'password_hash': user.password_hash,
                'email': user.email or '',
                'full_name': user.full_name or '',
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        with open(export_folder / "users.json", 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        
        # Exportar fotos
        photos = Photo.query.all()
        photos_data = []
        for photo in photos:
            photos_data.append({
                'filename': photo.filename,
                'original_filename': photo.original_filename,
                'file_path': photo.file_path,
                'date_taken': photo.date_taken.isoformat(),
                'uploaded_by': photo.uploaded_by,
                'uploaded_at': photo.uploaded_at.isoformat() if photo.uploaded_at else None,
                'status': photo.status,
                'status_updated_by': photo.status_updated_by,
                'status_updated_at': photo.status_updated_at.isoformat() if photo.status_updated_at else None
            })
        
        with open(export_folder / "photos.json", 'w', encoding='utf-8') as f:
            json.dump(photos_data, f, indent=2, ensure_ascii=False)
        
        # Exportar registros de tiempo
        time_entries = TimeEntry.query.all()
        time_entries_data = []
        for entry in time_entries:
            time_entries_data.append({
                'user_username': entry.user.username,  # Usar username en lugar de ID
                'date': entry.date.isoformat(),
                'entry_time': entry.entry_time.isoformat() if entry.entry_time else None,
                'exit_time': entry.exit_time.isoformat() if entry.exit_time else None,
                'break_start': entry.break_start.isoformat() if entry.break_start else None,
                'break_end': entry.break_end.isoformat() if entry.break_end else None,
                'total_hours': entry.total_hours,
                'break_hours': entry.break_hours,
                'notes': entry.notes,
                'status': entry.status,
                'created_at': entry.created_at.isoformat() if entry.created_at else None,
                'updated_at': entry.updated_at.isoformat() if entry.updated_at else None
            })
        
        with open(export_folder / "time_entries.json", 'w', encoding='utf-8') as f:
            json.dump(time_entries_data, f, indent=2, ensure_ascii=False)
        
        # Exportar documentos
        documents = UserDocument.query.all()
        documents_data = []
        for doc in documents:
            documents_data.append({
                'user_username': doc.user.username,  # Usar username en lugar de ID
                'filename': doc.filename,
                'original_filename': doc.original_filename,
                'file_path': doc.file_path,
                'file_type': doc.file_type,
                'document_type': doc.document_type,
                'description': doc.description,
                'date_related': doc.date_related.isoformat() if doc.date_related else None,
                'uploaded_at': doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                'uploaded_by': doc.uploaded_by
            })
        
        with open(export_folder / "user_documents.json", 'w', encoding='utf-8') as f:
            json.dump(documents_data, f, indent=2, ensure_ascii=False)
        
        # Crear info del export
        export_info = {
            'export_date': datetime.now().isoformat(),
            'total_users': len(users_data),
            'total_photos': len(photos_data),
            'total_time_entries': len(time_entries_data),
            'total_documents': len(documents_data)
        }
        
        with open(export_folder / "export_info.json", 'w', encoding='utf-8') as f:
            json.dump(export_info, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Datos exportados exitosamente:")
        print(f"   📁 Carpeta: {export_folder.absolute()}")
        print(f"   👥 Usuarios: {len(users_data)}")
        print(f"   📸 Fotos: {len(photos_data)}")
        print(f"   ⏰ Fichajes: {len(time_entries_data)}")
        print(f"   📄 Documentos: {len(documents_data)}")
        
        return export_folder

def import_data():
    """Importa datos desde archivos JSON"""
    from app import app
    from models import db, User, Photo, TimeEntry, UserDocument
    from datetime import datetime
    
    export_folder = Path("data_export")
    if not export_folder.exists():
        print("❌ No se encontró la carpeta data_export. Ejecuta primero export_data()")
        return False
    
    print("🔄 Importando datos a la base de datos...")
    
    with app.app_context():
        # Importar usuarios
        try:
            with open(export_folder / "users.json", 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            for user_data in users_data:
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    user = User(
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        email=user_data.get('email', ''),
                        full_name=user_data.get('full_name', ''),
                        is_admin=user_data['is_admin'],
                        is_active=user_data['is_active']
                    )
                    if user_data.get('created_at'):
                        user.created_at = datetime.fromisoformat(user_data['created_at'])
                    db.session.add(user)
                    print(f"   ➕ Usuario creado: {user_data['username']}")
                else:
                    print(f"   ⚠️  Usuario ya existe: {user_data['username']}")
            
            db.session.commit()
            
        except FileNotFoundError:
            print("⚠️  Archivo users.json no encontrado")
        
        # Importar fotos
        try:
            with open(export_folder / "photos.json", 'r', encoding='utf-8') as f:
                photos_data = json.load(f)
            
            for photo_data in photos_data:
                existing_photo = Photo.query.filter_by(
                    filename=photo_data['filename'],
                    date_taken=datetime.fromisoformat(photo_data['date_taken']).date()
                ).first()
                
                if not existing_photo:
                    photo = Photo(
                        filename=photo_data['filename'],
                        original_filename=photo_data['original_filename'],
                        file_path=photo_data['file_path'],
                        date_taken=datetime.fromisoformat(photo_data['date_taken']).date(),
                        uploaded_by=photo_data['uploaded_by'],
                        status=photo_data['status'],
                        status_updated_by=photo_data.get('status_updated_by')
                    )
                    
                    if photo_data.get('uploaded_at'):
                        photo.uploaded_at = datetime.fromisoformat(photo_data['uploaded_at'])
                    if photo_data.get('status_updated_at'):
                        photo.status_updated_at = datetime.fromisoformat(photo_data['status_updated_at'])
                    
                    db.session.add(photo)
                    print(f"   ➕ Foto importada: {photo_data['filename']}")
            
            db.session.commit()
            
        except FileNotFoundError:
            print("⚠️  Archivo photos.json no encontrado")
        
        # Importar registros de tiempo
        try:
            with open(export_folder / "time_entries.json", 'r', encoding='utf-8') as f:
                time_entries_data = json.load(f)
            
            for entry_data in time_entries_data:
                user = User.query.filter_by(username=entry_data['user_username']).first()
                if user:
                    existing_entry = TimeEntry.query.filter_by(
                        user_id=user.id,
                        date=datetime.fromisoformat(entry_data['date']).date()
                    ).first()
                    
                    if not existing_entry:
                        entry = TimeEntry(
                            user_id=user.id,
                            date=datetime.fromisoformat(entry_data['date']).date(),
                            total_hours=entry_data.get('total_hours', 0.0),
                            break_hours=entry_data.get('break_hours', 0.0),
                            notes=entry_data.get('notes'),
                            status=entry_data.get('status', 'active')
                        )
                        
                        if entry_data.get('entry_time'):
                            entry.entry_time = datetime.fromisoformat(entry_data['entry_time'])
                        if entry_data.get('exit_time'):
                            entry.exit_time = datetime.fromisoformat(entry_data['exit_time'])
                        if entry_data.get('break_start'):
                            entry.break_start = datetime.fromisoformat(entry_data['break_start'])
                        if entry_data.get('break_end'):
                            entry.break_end = datetime.fromisoformat(entry_data['break_end'])
                        if entry_data.get('created_at'):
                            entry.created_at = datetime.fromisoformat(entry_data['created_at'])
                        if entry_data.get('updated_at'):
                            entry.updated_at = datetime.fromisoformat(entry_data['updated_at'])
                        
                        db.session.add(entry)
                        print(f"   ➕ Fichaje importado: {user.username} - {entry_data['date']}")
            
            db.session.commit()
            
        except FileNotFoundError:
            print("⚠️  Archivo time_entries.json no encontrado")
        
        print("✅ Importación completada")
        return True

def create_backup():
    """Crea backup de la base de datos actual"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = Path("backups")
    backup_folder.mkdir(exist_ok=True)
    
    # Backup de la base de datos
    db_file = "instance/floristeria.db"
    if os.path.exists(db_file):
        backup_db = backup_folder / f"floristeria_backup_{timestamp}.db"
        shutil.copy2(db_file, backup_db)
        print(f"✅ Backup de BD creado: {backup_db}")
    
    # Backup de archivos subidos
    if os.path.exists("static/uploads"):
        backup_uploads = backup_folder / f"uploads_backup_{timestamp}"
        shutil.copytree("static/uploads", backup_uploads, dirs_exist_ok=True)
        print(f"✅ Backup de archivos creado: {backup_uploads}")
    
    return backup_folder

def main():
    """Función principal con menú interactivo"""
    print("🌸 === Sincronización de Datos - Floristería Raquel ===")
    print()
    print("Opciones disponibles:")
    print("1. Exportar datos (para subir al servidor)")
    print("2. Importar datos (desde export)")
    print("3. Crear backup")
    print("4. Salir")
    print()
    
    while True:
        choice = input("Selecciona una opción (1-4): ").strip()
        
        if choice == "1":
            print("\n📤 EXPORTANDO DATOS...")
            export_data()
            print("\n📋 Para subir al servidor:")
            print("   1. Copia la carpeta 'data_export' al servidor")
            print("   2. En el servidor ejecuta: python sync_data.py")
            print("   3. Selecciona opción 2 (Importar datos)")
            break
            
        elif choice == "2":
            print("\n📥 IMPORTANDO DATOS...")
            success = import_data()
            if success:
                print("\n✅ Datos importados correctamente")
            break
            
        elif choice == "3":
            print("\n💾 CREANDO BACKUP...")
            create_backup()
            break
            
        elif choice == "4":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida. Por favor selecciona 1, 2, 3 o 4.")

if __name__ == "__main__":
    main()
