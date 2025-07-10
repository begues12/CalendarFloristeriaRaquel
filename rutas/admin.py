"""
Rutas administrativas: gestión de documentos de todos los usuarios
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
import subprocess
import json
from models import UserDocument, User, MaintenanceMode, UpdateLog, db

admin_bp = Blueprint('admin', __name__)

def requires_privilege(privilege_name):
    """Decorador para verificar privilegios específicos"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            # Los admins y super admins tienen acceso completo
            if current_user.is_admin or current_user.is_super_admin:
                return f(*args, **kwargs)
            if not current_user.has_privilege(privilege_name):
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def require_super_admin(f):
    """Decorador para requerir permisos de super admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin:
            flash('No tienes permisos de super administrador para acceder a esta función', 'error')
            return redirect(url_for('calendar.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin_documents')
@login_required
@requires_privilege('can_view_all_documents')
def admin_documents():
    """Ver todos los documentos"""
    # Obtener filtros
    user_id = request.args.get('user_id', type=int)
    document_type = request.args.get('document_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Construir query
    query = UserDocument.query
    
    if user_id:
        query = query.filter(UserDocument.user_id == user_id)
    
    if document_type:
        query = query.filter(UserDocument.document_type == document_type)
    
    if start_date:
        query = query.filter(UserDocument.uploaded_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(UserDocument.uploaded_at < end_datetime)
    
    # Obtener documentos ordenados por fecha
    documents = query.order_by(UserDocument.uploaded_at.desc()).all()
    
    # Obtener usuarios activos para el filtro (excluir usuario de emergencia)
    users = User.query.filter(User.is_active == True, User.username != 'superadmin').all()
    
    # Tipos de documentos disponibles
    document_types = [
        ('justificante', 'Justificante'),
        ('medico', 'Justificante Médico'),
        ('vacaciones', 'Solicitud de Vacaciones'),
        ('contrato', 'Contrato'),
        ('nomina', 'Nómina'),
        ('otros', 'Otros')
    ]
    
    return render_template('admin_documents.html',
                         documents=documents,
                         users=users,
                         document_types=document_types,
                         selected_user_id=user_id,
                         selected_document_type=document_type,
                         start_date=start_date,
                         end_date=end_date)

@admin_bp.route('/admin_download_document/<int:doc_id>')
@login_required
def admin_download_document(doc_id):
    """Descargar cualquier documento - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para descargar este documento', 'error')
        return redirect(url_for('documents.my_documents'))
    
    document = UserDocument.query.get_or_404(doc_id)
    
    try:
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=f"{document.user.username}_{document.filename}"
        )
    except FileNotFoundError:
        flash('El archivo no existe en el servidor', 'error')
        return redirect(url_for('admin.admin_documents'))

@admin_bp.route('/admin_delete_document/<int:doc_id>', methods=['POST'])
@login_required
def admin_delete_document(doc_id):
    """Eliminar cualquier documento - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para eliminar documentos', 'error')
        return redirect(url_for('documents.my_documents'))
    
    document = UserDocument.query.get_or_404(doc_id)
    
    try:
        # Eliminar archivo físico
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Eliminar registro de la base de datos
        filename = document.filename
        db.session.delete(document)
        db.session.commit()
        
        flash(f'Documento {filename} eliminado correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar el documento', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.admin_documents'))

# ===============================================
# RUTAS DE SUPER ADMINISTRADOR
# ===============================================

@admin_bp.route('/super_admin_panel')
@login_required
@require_super_admin
def super_admin_panel():
    """Panel de control del super administrador"""
    maintenance = MaintenanceMode.get_current()
    recent_updates = UpdateLog.query.order_by(UpdateLog.started_at.desc()).limit(10).all()
    
    # Obtener información del git
    git_info = get_git_info()
    
    return render_template('super_admin_panel.html', 
                         maintenance=maintenance,
                         recent_updates=recent_updates,
                         git_info=git_info)

@admin_bp.route('/toggle_maintenance', methods=['POST'])
@login_required
@require_super_admin
def toggle_maintenance():
    """Activar/desactivar modo mantenimiento"""
    maintenance = MaintenanceMode.get_current()
    
    if maintenance.is_active:
        maintenance.deactivate()
        flash('Modo mantenimiento desactivado', 'success')
    else:
        message = request.form.get('message', 'Sistema en mantenimiento. Volveremos pronto.')
        estimated_minutes = request.form.get('estimated_minutes', 30, type=int)
        maintenance.activate(current_user, message, estimated_minutes)
        flash('Modo mantenimiento activado', 'success')
    
    return redirect(url_for('admin.super_admin_panel'))

@admin_bp.route('/update_system', methods=['POST'])
@login_required
@require_super_admin
def update_system():
    """Actualizar el sistema desde git y ejecutar migraciones"""
    try:
        # Crear log de actualización
        update_log = UpdateLog(
            started_by=current_user.username,
            git_commit_before=get_current_git_commit()
        )
        db.session.add(update_log)
        db.session.commit()
        
        # Activar modo mantenimiento automáticamente
        maintenance = MaintenanceMode.get_current()
        if not maintenance.is_active:
            maintenance.activate(current_user, 'Actualizando sistema...', 15)
        
        # Ejecutar actualización
        result = perform_system_update(update_log)
        
        if result['success']:
            update_log.mark_completed(result.get('commit_after'))
            flash('Sistema actualizado correctamente', 'success')
        else:
            update_log.mark_failed(result['error'])
            flash(f'Error en la actualización: {result["error"]}', 'error')
            
    except Exception as e:
        flash(f'Error inesperado durante la actualización: {str(e)}', 'error')
    
    return redirect(url_for('admin.super_admin_panel'))

@admin_bp.route('/check_updates')
@login_required
@require_super_admin
def check_updates():
    """Verificar si hay actualizaciones disponibles"""
    try:
        result = subprocess.run(['git', 'fetch'], capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            return jsonify({'error': 'Error al verificar actualizaciones'})
        
        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD..origin/main'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            updates_available = int(result.stdout.strip()) > 0
            return jsonify({'updates_available': updates_available, 'count': result.stdout.strip()})
        else:
            return jsonify({'error': 'Error al verificar actualizaciones'})
            
    except Exception as e:
        return jsonify({'error': str(e)})

@admin_bp.route('/update_log/<int:log_id>')
@login_required
@require_super_admin
def view_update_log(log_id):
    """Ver detalles de un log de actualización"""
    update_log = UpdateLog.query.get_or_404(log_id)
    return render_template('update_log_detail.html', update_log=update_log)

# ===============================================
# FUNCIONES AUXILIARES
# ===============================================

def get_git_info():
    """Obtener información del repositorio git"""
    try:
        # Obtener commit actual
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        current_commit = result.stdout.strip()[:8] if result.returncode == 0 else 'Unknown'
        
        # Obtener branch actual
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        current_branch = result.stdout.strip() if result.returncode == 0 else 'Unknown'
        
        # Obtener último mensaje de commit
        result = subprocess.run(['git', 'log', '-1', '--pretty=%s'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        last_commit_message = result.stdout.strip() if result.returncode == 0 else 'Unknown'
        
        return {
            'current_commit': current_commit,
            'current_branch': current_branch,
            'last_commit_message': last_commit_message
        }
    except Exception:
        return {
            'current_commit': 'Error',
            'current_branch': 'Error', 
            'last_commit_message': 'Error al obtener información'
        }

def get_current_git_commit():
    """Obtener el hash del commit current"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None

def perform_system_update(update_log):
    """Realizar la actualización del sistema"""
    try:
        output_log = []
        
        # 1. Git pull
        result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        output_log.append(f"Git pull: {result.stdout}")
        
        if result.returncode != 0:
            return {'success': False, 'error': f'Error en git pull: {result.stderr}'}
        
        # 2. Instalar dependencias
        result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        output_log.append(f"Pip install: {result.stdout}")
        
        if result.returncode != 0:
            output_log.append(f"Pip install warning: {result.stderr}")
        
        # 3. Ejecutar migraciones
        result = subprocess.run(['flask', 'db', 'upgrade'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        output_log.append(f"Flask migrate: {result.stdout}")
        
        if result.returncode != 0:
            return {'success': False, 'error': f'Error en migraciones: {result.stderr}'}
        
        # Guardar output en el log
        update_log.migration_output = '\n'.join(output_log)
        db.session.commit()
        
        # Desactivar modo mantenimiento
        maintenance = MaintenanceMode.get_current()
        if maintenance.is_active:
            maintenance.deactivate()
        
        return {
            'success': True, 
            'commit_after': get_current_git_commit(),
            'output': '\n'.join(output_log)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
