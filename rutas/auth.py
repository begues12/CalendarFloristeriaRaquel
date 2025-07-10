"""
Rutas de autenticación: login, logout, cambio de contraseña obligatorio
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, MaintenanceMode, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido {username}!', 'success')
            
            # Verificar modo mantenimiento después del login
            try:
                maintenance = MaintenanceMode.get_current()
                if maintenance.is_active and not user.is_super_admin:
                    # Si está en mantenimiento y no es super admin, mostrar página de mantenimiento
                    flash('El sistema está en modo mantenimiento. Solo los super administradores pueden acceder.', 'warning')
                    logout_user()  # Cerrar sesión automáticamente
                    return render_template('maintenance.html', maintenance=maintenance), 503
            except Exception:
                pass  # Si hay error accediendo a la DB, continuar normalmente
            
            return redirect(next_page) if next_page else redirect(url_for('calendar.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/force_change_password', methods=['GET', 'POST'])
@login_required
def force_change_password():
    """Cambio obligatorio de contraseña en primer acceso"""
    # Si el usuario ya no necesita cambiar contraseña, redirigir
    if not current_user.must_change_password:
        return redirect(url_for('calendar.index'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validaciones
        if not current_user.check_password(current_password):
            flash('La contraseña actual es incorrecta', 'error')
            return render_template('force_change_password.html')
        
        if new_password != confirm_password:
            flash('Las nuevas contraseñas no coinciden', 'error')
            return render_template('force_change_password.html')
        
        if len(new_password) < 4:
            flash('La nueva contraseña debe tener al menos 4 caracteres', 'error')
            return render_template('force_change_password.html')
        
        if current_password == new_password:
            flash('La nueva contraseña debe ser diferente a la actual', 'error')
            return render_template('force_change_password.html')
        
        try:
            current_user.set_password(new_password)
            current_user.must_change_password = False  # Ya no necesita cambiar contraseña
            db.session.commit()
            flash('Contraseña cambiada correctamente. ¡Bienvenido!', 'success')
            return redirect(url_for('calendar.index'))
        except Exception as e:
            flash('Error al cambiar la contraseña. Inténtalo de nuevo.', 'error')
            db.session.rollback()
    
    return render_template('force_change_password.html')
