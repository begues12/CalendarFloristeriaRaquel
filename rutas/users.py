"""
Rutas de gestión de usuarios: crear, editar, eliminar usuarios y cambio de contraseñas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from models import User, db
from datetime import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route('/manage_users')
@login_required
def manage_users():
    """Panel de gestión de usuarios - solo para admin"""
    if not current_user.is_admin:
        flash('Solo el administrador puede gestionar usuarios', 'error')
        return redirect(url_for('calendar.index'))
    
    # Excluir el usuario de emergencia de la gestión normal
    users = User.query.filter(User.username != 'superadmin').all()
    return render_template('manage_users.html', users=users)

@users_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Crear nuevo usuario - solo admin"""
    if not current_user.is_admin:
        flash('Solo el administrador puede crear nuevos usuarios', 'error')
        return redirect(url_for('calendar.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form.get('full_name', '')
        email = request.form.get('email', '')
        is_admin = 'is_admin' in request.form
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
        elif len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres', 'error')
        elif User.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'error')
        else:
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                is_admin=is_admin,
                must_change_password=True  # Nuevo usuario debe cambiar contraseña
            )
            user.set_password(password)
            user.set_default_privileges()  # Establecer privilegios por defecto
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Usuario {username} creado correctamente', 'success')
            return redirect(url_for('users.manage_users'))
    
    return render_template('register.html')

@users_bp.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    """Cambiar contraseña - admin puede cambiar cualquiera, usuario solo la suya"""
    user = User.query.get_or_404(user_id)
    
    if not current_user.is_admin and current_user.id != user_id:
        flash('No tienes permisos para cambiar esta contraseña', 'error')
        return redirect(url_for('calendar.index'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
        elif len(new_password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres', 'error')
        else:
            user.set_password(new_password)
            user.must_change_password = False  # Ya cambió la contraseña
            db.session.commit()
            flash(f'Contraseña actualizada para {user.username}', 'success')
            
            if current_user.is_admin:
                return redirect(url_for('users.manage_users'))
            else:
                return redirect(url_for('calendar.index'))
    
    return render_template('change_password.html', user=user, user_id=user_id)

@users_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    """Eliminar usuario - solo admin"""
    if not current_user.is_admin:
        flash('Solo el administrador puede eliminar usuarios', 'error')
        return redirect(url_for('calendar.index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        flash('No se puede eliminar a un usuario administrador', 'error')
        return redirect(url_for('users.manage_users'))
    
    username = user.username
    user.is_active = False  # Marcar como inactivo en lugar de eliminar
    db.session.commit()
    
    flash(f'Usuario {username} desactivado. Los datos se conservan.', 'success')
    return redirect(url_for('users.manage_users'))

@users_bp.route('/user_profile/<int:user_id>')
@login_required
def user_profile(user_id):
    """Ver ficha detallada de usuario - solo admin o el mismo usuario"""
    user = User.query.get_or_404(user_id)
    
    # Solo admin o el mismo usuario pueden ver la ficha
    if not current_user.is_admin and current_user.id != user_id:
        flash('No tienes permisos para ver esta ficha de usuario', 'error')
        return redirect(url_for('calendar.index'))
    
    # Ocultar usuario de emergencia
    if user.username == 'superadmin':
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('users.manage_users'))
    
    return render_template('user_profile.html', user=user)

@users_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Editar usuario y privilegios - solo admin"""
    if not current_user.is_admin:
        flash('Solo el administrador puede editar usuarios', 'error')
        return redirect(url_for('calendar.index'))
    
    user = User.query.get_or_404(user_id)
    
    # No permitir editar usuario de emergencia
    if user.username == 'superadmin':
        flash('Este usuario no puede ser editado', 'error')
        return redirect(url_for('users.manage_users'))
    
    if request.method == 'POST':
        try:
            # Datos básicos del perfil
            user.full_name = request.form.get('full_name', '').strip()
            user.email = request.form.get('email', '').strip()
            user.phone = request.form.get('phone', '').strip()
            user.position = request.form.get('position', '').strip()
            
            # Fecha de contratación
            hire_date_str = request.form.get('hire_date')
            if hire_date_str:
                user.hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
            else:
                user.hire_date = None
            
            # Permisos principales
            user.is_admin = 'is_admin' in request.form
            user.is_active = 'is_active' in request.form
            
            # Privilegios específicos
            user.can_view_calendar = 'can_view_calendar' in request.form
            user.can_upload_photos = 'can_upload_photos' in request.form
            user.can_manage_photos = 'can_manage_photos' in request.form
            user.can_time_tracking = 'can_time_tracking' in request.form
            user.can_view_own_reports = 'can_view_own_reports' in request.form
            user.can_view_all_reports = 'can_view_all_reports' in request.form
            user.can_manage_time_entries = 'can_manage_time_entries' in request.form
            user.can_upload_documents = 'can_upload_documents' in request.form
            user.can_view_own_documents = 'can_view_own_documents' in request.form
            user.can_view_all_documents = 'can_view_all_documents' in request.form
            user.can_manage_users = 'can_manage_users' in request.form
            user.can_export_data = 'can_export_data' in request.form
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash(f'Usuario {user.username} actualizado correctamente', 'success')
            return redirect(url_for('users.user_profile', user_id=user.id))
            
        except Exception as e:
            flash(f'Error al actualizar el usuario: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_user.html', user=user)

@users_bp.route('/set_user_privileges/<int:user_id>', methods=['POST'])
@login_required
def set_user_privileges(user_id):
    """Establecer privilegios rápidos para un usuario - solo admin"""
    if not current_user.is_admin:
        flash('Solo el administrador puede cambiar privilegios', 'error')
        return redirect(url_for('calendar.index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.username == 'superadmin':
        flash('Este usuario no puede ser modificado', 'error')
        return redirect(url_for('users.manage_users'))
    
    privilege_set = request.form.get('privilege_set')
    
    if privilege_set == 'basic':
        # Privilegios básicos
        user.can_view_calendar = True
        user.can_upload_photos = True
        user.can_time_tracking = True
        user.can_view_own_reports = True
        user.can_upload_documents = True
        user.can_view_own_documents = True
        user.can_manage_photos = False
        user.can_view_all_reports = False
        user.can_manage_time_entries = False
        user.can_view_all_documents = False
        user.can_manage_users = False
        user.can_export_data = False
        
    elif privilege_set == 'supervisor':
        # Privilegios de supervisor
        user.can_view_calendar = True
        user.can_upload_photos = True
        user.can_manage_photos = True
        user.can_time_tracking = True
        user.can_view_own_reports = True
        user.can_view_all_reports = True
        user.can_manage_time_entries = True
        user.can_upload_documents = True
        user.can_view_own_documents = True
        user.can_view_all_documents = True
        user.can_manage_users = False
        user.can_export_data = True
        
    elif privilege_set == 'admin':
        # Privilegios de administrador
        user.can_view_calendar = True
        user.can_upload_photos = True
        user.can_manage_photos = True
        user.can_time_tracking = True
        user.can_view_own_reports = True
        user.can_view_all_reports = True
        user.can_manage_time_entries = True
        user.can_upload_documents = True
        user.can_view_own_documents = True
        user.can_view_all_documents = True
        user.can_manage_users = True
        user.can_export_data = True
        user.is_admin = True
    
    try:
        user.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Privilegios {privilege_set} aplicados a {user.username}', 'success')
    except Exception as e:
        flash(f'Error al aplicar privilegios: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('users.user_profile', user_id=user.id))

@users_bp.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """Activar/desactivar usuario - solo admin"""
    if not current_user.is_admin and not current_user.is_super_admin:
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('users.manage_users'))
    
    user = User.query.get_or_404(user_id)
    
    # No permitir desactivar al propio usuario
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta', 'error')
        return redirect(url_for('users.manage_users'))
    
    # No permitir desactivar al usuario superadmin de emergencia
    if user.username == 'superadmin':
        flash('No se puede desactivar el usuario de emergencia', 'error')
        return redirect(url_for('users.manage_users'))
    
    # Cambiar el estado
    user.is_active = not user.is_active
    action = "activado" if user.is_active else "desactivado"
    
    try:
        db.session.commit()
        flash(f'Usuario {user.username} {action} correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado del usuario: {str(e)}', 'error')
    
    return redirect(url_for('users.manage_users'))
