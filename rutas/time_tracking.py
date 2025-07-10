"""
Rutas de control horario: fichaje de entrada/salida, descansos, reportes personales
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, abort
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
import csv
import io
from models import TimeEntry, User, db

time_tracking_bp = Blueprint('time_tracking', __name__)

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

def hours_to_hhmm(hours_decimal):
    """Convierte horas decimales a formato HH:MM"""
    if not hours_decimal:
        return "00:00"
    
    total_minutes = int(hours_decimal * 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"

@time_tracking_bp.route('/time_tracking')
@login_required
@requires_privilege('can_time_tracking')
def time_tracking():
    """Panel de fichaje personal"""
    today = date.today()
    
    # Entrada de hoy
    today_entry = TimeEntry.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    # Últimas entradas (últimos 7 días)
    start_date = today - timedelta(days=7)
    recent_entries = TimeEntry.query.filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.date >= start_date
    ).order_by(TimeEntry.date.desc()).all()
    
    return render_template('time_tracking.html',
                         today_entry=today_entry,
                         recent_entries=recent_entries,
                         today=today)

@time_tracking_bp.route('/clock_in')
@login_required
@requires_privilege('can_time_tracking')
def clock_in():
    """Fichar entrada"""
    today = date.today()
    
    # Buscar entrada existente para hoy
    time_entry = TimeEntry.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if time_entry and time_entry.entry_time:
        flash('Ya has fichado la entrada hoy', 'warning')
    else:
        if not time_entry:
            time_entry = TimeEntry(user_id=current_user.id, date=today)
        
        time_entry.entry_time = datetime.now()
        time_entry.status = 'active'
        db.session.add(time_entry)
        db.session.commit()
        flash('Entrada registrada correctamente', 'success')
    
    return redirect(url_for('time_tracking.time_tracking'))

@time_tracking_bp.route('/clock_out')
@login_required
@requires_privilege('can_time_tracking')
def clock_out():
    """Fichar salida"""
    today = date.today()
    
    time_entry = TimeEntry.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if not time_entry or not time_entry.entry_time:
        flash('Debes fichar la entrada primero', 'error')
    elif time_entry.exit_time:
        flash('Ya has fichado la salida hoy', 'warning')
    else:
        time_entry.exit_time = datetime.now()
        time_entry.status = 'completed'
        time_entry.calculate_total_hours()
        db.session.commit()
        flash('Salida registrada correctamente', 'success')
    
    return redirect(url_for('time_tracking.time_tracking'))

@time_tracking_bp.route('/break_start')
@login_required
@requires_privilege('can_time_tracking')
def break_start():
    """Iniciar descanso"""
    today = date.today()
    
    time_entry = TimeEntry.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if not time_entry or not time_entry.entry_time:
        flash('Debes fichar la entrada primero', 'error')
    elif time_entry.break_start and not time_entry.break_end:
        flash('Ya has iniciado el descanso', 'warning')
    else:
        time_entry.break_start = datetime.now()
        time_entry.break_end = None  # Resetear fin de descanso
        db.session.commit()
        flash('Descanso iniciado', 'success')
    
    return redirect(url_for('time_tracking.time_tracking'))

@time_tracking_bp.route('/break_end')
@login_required
@requires_privilege('can_time_tracking')
def break_end():
    """Finalizar descanso"""
    today = date.today()
    
    time_entry = TimeEntry.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if not time_entry or not time_entry.break_start:
        flash('Debes iniciar el descanso primero', 'error')
    elif time_entry.break_end:
        flash('Ya has finalizado el descanso', 'warning')
    else:
        time_entry.break_end = datetime.now()
        time_entry.calculate_total_hours()
        db.session.commit()
        flash('Descanso finalizado', 'success')
    
    return redirect(url_for('time_tracking.time_tracking'))

@time_tracking_bp.route('/time_reports')
@login_required
def time_reports():
    """Reportes de horarios"""
    # Verificar si puede ver reportes de todos o solo los propios
    can_view_all = (current_user.has_privilege('can_view_all_reports') or 
                   current_user.is_admin or 
                   current_user.is_super_admin)
    can_view_own = current_user.has_privilege('can_view_own_reports')
    
    if not can_view_all and not can_view_own:
        abort(403)
    
    # Obtener filtros
    user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Configurar fechas por defecto (último mes)
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = date.today().strftime('%Y-%m-%d')
    
    # Construir query
    query = TimeEntry.query
    
    # Si solo puede ver sus propios reportes, filtrar por usuario actual
    if not can_view_all and can_view_own:
        query = query.filter(TimeEntry.user_id == current_user.id)
        user_id = current_user.id  # Forzar para que no pueda cambiar el filtro
    elif user_id:
        query = query.filter(TimeEntry.user_id == user_id)
    
    query = query.filter(
        TimeEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
        TimeEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
    )
    
    entries = query.order_by(TimeEntry.date.desc()).all()
    
    # Solo mostrar usuarios si puede ver reportes de todos
    if can_view_all:
        users = User.query.filter(User.is_active == True, User.username != 'superadmin').all()
    else:
        users = [current_user]  # Solo mostrar el usuario actual
    
    return render_template('time_reports.html',
                         entries=entries,
                         users=users,
                         selected_user_id=user_id,
                         start_date=start_date,
                         end_date=end_date,
                         can_view_all=can_view_all)

@time_tracking_bp.route('/export_time_report')
@login_required
@requires_privilege('can_export_data')
def export_time_report():
    """Exportar reporte de horarios a CSV"""
    # Obtener los mismos filtros que en time_reports
    user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Configurar fechas por defecto (último mes)
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = date.today().strftime('%Y-%m-%d')
    
    # Construir query
    query = TimeEntry.query
    
    if user_id:
        query = query.filter(TimeEntry.user_id == user_id)
    
    query = query.filter(
        TimeEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
        TimeEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
    )
    
    entries = query.order_by(TimeEntry.date.desc()).all()
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir cabeceras
    writer.writerow(['Usuario', 'Fecha', 'Entrada', 'Salida', 'Horas Totales', 'Estado'])
    
    # Escribir datos
    for entry in entries:
        entry_time = entry.entry_time.strftime('%H:%M') if entry.entry_time else '-'
        exit_time = entry.exit_time.strftime('%H:%M') if entry.exit_time else '-'
        total_hours = f"{entry.total_hours:.2f}h" if entry.total_hours else '-'
        
        writer.writerow([
            entry.user.username,
            entry.date.strftime('%d/%m/%Y'),
            entry_time,
            exit_time,
            total_hours,
            entry.status.title() if entry.status else 'Activo'
        ])
    
    # Crear respuesta
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_horarios_{start_date}_a_{end_date}.csv'
    
    return response


@time_tracking_bp.route('/create_time_entry', methods=['GET', 'POST'])
@login_required
@requires_privilege('can_manage_time_entries')
def create_time_entry():
    """Crear nuevo registro de tiempo"""
    
    if request.method == 'POST':
        try:
            user_id = request.form.get('user_id', type=int)
            date_str = request.form.get('date')
            entry_time_str = request.form.get('entry_time')
            exit_time_str = request.form.get('exit_time')
            break_start_str = request.form.get('break_start')
            break_end_str = request.form.get('break_end')
            notes = request.form.get('notes', '').strip()
            status = request.form.get('status', 'active')
            
            if not user_id or not date_str:
                flash('Usuario y fecha son obligatorios', 'error')
                return render_template('create_time_entry.html', users=User.query.filter(User.is_active == True, User.username != 'superadmin').all())
            
            # Verificar que no existe ya un registro para esa fecha y usuario
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            existing = TimeEntry.query.filter_by(user_id=user_id, date=entry_date).first()
            if existing:
                flash(f'Ya existe un registro para ese usuario en la fecha {entry_date.strftime("%d/%m/%Y")}', 'error')
                return render_template('create_time_entry.html', users=User.query.filter(User.is_active == True, User.username != 'superadmin').all())
            
            # Crear nuevo registro
            entry = TimeEntry(
                user_id=user_id,
                date=entry_date,
                notes=notes,
                status=status
            )
            
            # Asignar horarios si se proporcionan
            if entry_time_str:
                entry.entry_time = datetime.strptime(f"{entry_date} {entry_time_str}", '%Y-%m-%d %H:%M')
            if exit_time_str:
                entry.exit_time = datetime.strptime(f"{entry_date} {exit_time_str}", '%Y-%m-%d %H:%M')
            if break_start_str:
                entry.break_start = datetime.strptime(f"{entry_date} {break_start_str}", '%Y-%m-%d %H:%M')
            if break_end_str:
                entry.break_end = datetime.strptime(f"{entry_date} {break_end_str}", '%Y-%m-%d %H:%M')
            
            # Calcular horas totales
            entry.calculate_total_hours()
            
            db.session.add(entry)
            db.session.commit()
            
            flash('Registro creado correctamente', 'success')
            return redirect(url_for('time_tracking.time_reports'))
            
        except ValueError as e:
            flash(f'Error en el formato de fecha/hora: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error al crear el registro: {str(e)}', 'error')
            db.session.rollback()
    
    users = User.query.filter(User.is_active == True, User.username != 'superadmin').all()
    today = date.today()
    return render_template('create_time_entry.html', users=users, today=today)


@time_tracking_bp.route('/edit_time_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
@requires_privilege('can_manage_time_entries')
def edit_time_entry(entry_id):
    """Editar registro de tiempo"""
    entry = TimeEntry.query.get_or_404(entry_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            entry_time_str = request.form.get('entry_time')
            exit_time_str = request.form.get('exit_time')
            break_start_str = request.form.get('break_start')
            break_end_str = request.form.get('break_end')
            notes = request.form.get('notes', '').strip()
            status = request.form.get('status', 'active')
            
            # Convertir horarios
            if entry_time_str:
                entry_time = datetime.strptime(f"{entry.date} {entry_time_str}", '%Y-%m-%d %H:%M')
                entry.entry_time = entry_time
            else:
                entry.entry_time = None
                
            if exit_time_str:
                exit_time = datetime.strptime(f"{entry.date} {exit_time_str}", '%Y-%m-%d %H:%M')
                entry.exit_time = exit_time
            else:
                entry.exit_time = None
                
            if break_start_str:
                break_start = datetime.strptime(f"{entry.date} {break_start_str}", '%Y-%m-%d %H:%M')
                entry.break_start = break_start
            else:
                entry.break_start = None
                
            if break_end_str:
                break_end = datetime.strptime(f"{entry.date} {break_end_str}", '%Y-%m-%d %H:%M')
                entry.break_end = break_end
            else:
                entry.break_end = None
                
            # Actualizar otros campos
            entry.notes = notes
            entry.status = status
            entry.updated_at = datetime.utcnow()
            
            # Recalcular horas totales
            entry.calculate_total_hours()
            
            db.session.commit()
            flash('Registro actualizado correctamente', 'success')
            return redirect(url_for('time_tracking.time_reports'))
            
        except ValueError as e:
            flash(f'Error en el formato de hora: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error al actualizar el registro: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_time_entry.html', entry=entry)


@time_tracking_bp.route('/delete_time_entry/<int:entry_id>', methods=['POST'])
@login_required
@requires_privilege('can_manage_time_entries')
def delete_time_entry(entry_id):
    """Eliminar registro de tiempo"""
    entry = TimeEntry.query.get_or_404(entry_id)
    
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Registro eliminado correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el registro: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('time_tracking.time_reports'))
