"""
Rutas del calendario: página principal, vista de días, subida y gestión de fotos
"""

from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
import calendar
import os
import json
from PIL import Image
from app.models import Photo, db
from app.models.user import ApiIntegration, ApiData, CalendarNote
from app.utils.api_service import ApiIntegrationService
from . import bp

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

def allowed_file(filename, allowed_extensions):
    """Verificar si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def resize_image(image_path, max_size=(800, 600)):
    """Redimensiona imagen para optimizar el almacenamiento"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, optimize=True, quality=85)
    except Exception as e:
        print(f"Error redimensionando imagen: {e}")

@bp.route('/')
@login_required
@requires_privilege('can_view_calendar')
def index():
    """Página principal del calendario"""
    # Obtener mes y año actual o de los parámetros
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))
    
    # Crear calendario
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Obtener fotos para cada día del mes con conteo de estados
    photos_by_date = {}
    status_counts_by_date = {}
    api_data_by_date = {}
    notes_by_date = {}
    
    for week in cal:
        for day in week:
            if day > 0:
                date_obj = date(year, month, day)
                
                # Fotos existentes
                photos = Photo.query.filter_by(date_taken=date_obj).all()
                photos_by_date[day] = photos
                
                # Contar estados de fotos
                status_counts = {'pendiente': 0, 'hecho': 0, 'entregado': 0}
                for photo in photos:
                    if photo.status in status_counts:
                        status_counts[photo.status] += 1
                status_counts_by_date[day] = status_counts
                
                # Datos de APIs para este día
                api_data = ApiData.query.filter_by(date_for=date_obj, is_visible=True).all()
                api_data_by_date[day] = api_data
                
                # Notas para este día (solo visibles según privacidad)
                if current_user.is_admin or current_user.is_super_admin:
                    # Los admins ven todas las notas
                    notes = CalendarNote.query.filter_by(date_for=date_obj).all()
                else:
                    # Los usuarios normales solo ven sus notas privadas y las públicas
                    notes = CalendarNote.query.filter(
                        CalendarNote.date_for == date_obj,
                        (CalendarNote.is_private == False) | 
                        (CalendarNote.created_by == current_user.id)
                    ).all()
                notes_by_date[day] = notes
    
    # Navegación de meses
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render_template('calendar.html',
                         calendar=cal,
                         year=year,
                         month=month,
                         month_name=month_name,
                         photos_by_date=photos_by_date,
                         status_counts_by_date=status_counts_by_date,
                         api_data_by_date=api_data_by_date,
                         notes_by_date=notes_by_date,
                         today=today,
                         prev_month=prev_month,
                         prev_year=prev_year,
                         next_month=next_month,
                         next_year=next_year)

@bp.route('/day/<date_str>')
@login_required
@requires_privilege('can_view_calendar')
def view_day(date_str):
    """Ver fotos de un día específico"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        photos = Photo.query.filter_by(date_taken=date_obj).all()
        
        # Obtener datos de APIs para esta fecha
        api_data = ApiData.query.filter(
            ApiData.date_for == date_obj
        ).all()
        
        # Obtener notas para esta fecha
        notes = CalendarNote.query.filter(
            CalendarNote.date_for == date_obj
        ).order_by(CalendarNote.created_at.desc()).all()
        
        return render_template('day.html',
                             date=date_obj,
                             date_str=date_str,
                             photos=photos,
                             api_data=api_data,
                             notes=notes)
    except ValueError:
        flash('Fecha inválida', 'error')
        return redirect(url_for('calendar.index'))

@bp.route('/upload/<date_str>', methods=['GET', 'POST'])
@login_required
@requires_privilege('can_upload_photos')
def upload_photo(date_str):
    """Subir fotos para una fecha específica"""
    from flask import current_app
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Fecha inválida', 'error')
        return redirect(url_for('calendar.index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('file')
        uploaded_count = 0
        
        for file in files:
            if file.filename == '':
                continue
                
            if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                # Crear carpeta para la fecha
                date_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], date_str)
                os.makedirs(date_folder, exist_ok=True)
                
                # Generar nombre único
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%H%M%S')
                name, ext = os.path.splitext(filename)
                new_filename = f"{name}_{timestamp}{ext}"
                
                file_path = os.path.join(date_folder, new_filename)
                file.save(file_path)
                
                # Redimensionar si es imagen
                if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    resize_image(file_path)
                
                # Guardar en base de datos
                photo = Photo(
                    filename=new_filename,
                    original_filename=file.filename,
                    file_path=f'uploads/{date_str}/{new_filename}',
                    date_taken=date_obj,
                    uploaded_by=current_user.username
                )
                
                db.session.add(photo)
                uploaded_count += 1
            else:
                flash(f'Archivo no válido: {file.filename}', 'error')
        
        if uploaded_count > 0:
            db.session.commit()
            flash(f'Se subieron {uploaded_count} foto(s) correctamente', 'success')
        
        return redirect(url_for('calendar.view_day', date_str=date_str))
    
    photos = Photo.query.filter_by(date_taken=date_obj).all()
    return render_template('upload.html',
                         date=date_obj,
                         date_str=date_str,
                         photos=photos)

@bp.route('/delete_photo/<int:photo_id>')
@login_required
def delete_photo(photo_id):
    """Eliminar una foto"""
    photo = Photo.query.get_or_404(photo_id)
    date_str = photo.date_taken.strftime('%Y-%m-%d')
    
    # Verificar privilegios: el usuario puede eliminar sus propias fotos o tener privilegio de gestionar fotos o ser admin
    if not (photo.uploaded_by == current_user.username or 
            current_user.has_privilege('can_manage_photos') or 
            current_user.is_admin or 
            current_user.is_super_admin):
        abort(403)
    
    try:
        # Eliminar archivo físico
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)
        
        # Eliminar de base de datos
        db.session.delete(photo)
        db.session.commit()
        
        flash('Foto eliminada correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar la foto', 'error')
    
    return redirect(url_for('calendar.view_day', date_str=date_str))

@bp.route('/change_status/<int:photo_id>/<new_status>')
@login_required
def change_status(photo_id, new_status):
    """Cambiar el estado de una foto"""
    photo = Photo.query.get_or_404(photo_id)
    
    # Verificar privilegios: el usuario puede cambiar estado de sus propias fotos o tener privilegio de gestionar fotos o ser admin
    if not (photo.uploaded_by == current_user.username or 
            current_user.has_privilege('can_manage_photos') or 
            current_user.is_admin or 
            current_user.is_super_admin):
        abort(403)
    
    valid_statuses = ['pendiente', 'hecho', 'entregado']
    if new_status not in valid_statuses:
        flash('Estado no válido', 'error')
        return redirect(url_for('calendar.index'))

    date_str = photo.date_taken.strftime('%Y-%m-%d')
    
    photo.status = new_status
    photo.status_updated_by = current_user.username
    photo.status_updated_at = datetime.now()
    
    db.session.commit()
    
    status_names = {
        'pendiente': 'Pendiente',
        'hecho': 'Hecho',
        'entregado': 'Entregado'
    }
    flash(f'Estado cambiado a: {status_names[new_status]}', 'success')
    
    return redirect(url_for('calendar.view_day', date_str=date_str))

# =============================================================================
# RUTAS PARA INTEGRACIÓN DE APIs
# =============================================================================

@bp.route('/api-integrations')
@login_required
def api_integrations():
    """Lista de integraciones de API configuradas"""
    if not (current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    integrations = ApiIntegration.query.order_by(ApiIntegration.created_at.desc()).all()
    return render_template('api_integrations.html', integrations=integrations)

@bp.route('/api-integrations/create', methods=['GET', 'POST'])
@login_required
def create_api_integration():
    """Crear nueva integración de API"""
    if not (current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    if request.method == 'POST':
        try:
            # Validar configuración de mapeo JSON
            mapping_config = request.form.get('mapping_config', '{}')
            try:
                json.loads(mapping_config)
            except json.JSONDecodeError:
                flash('La configuración de mapeo debe ser JSON válido', 'error')
                return render_template('create_api_integration.html')
            
            integration = ApiIntegration(
                name=request.form['name'],
                api_type=request.form['api_type'],
                url=request.form['url'],
                api_key=request.form.get('api_key', '').strip() or None,
                headers=request.form.get('headers', '').strip() or None,
                request_method=request.form.get('request_method', 'GET'),
                request_body=request.form.get('request_body', '').strip() or None,
                mapping_config=mapping_config,
                refresh_interval=int(request.form.get('refresh_interval', 60)),
                is_active='is_active' in request.form,
                created_by=current_user.id
            )
            
            db.session.add(integration)
            db.session.commit()
            
            flash('Integración de API creada correctamente', 'success')
            return redirect(url_for('calendar.api_integrations'))
            
        except Exception as e:
            flash(f'Error al crear la integración: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('create_api_integration.html')

@bp.route('/api-integrations/<int:integration_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_api_integration(integration_id):
    """Editar integración de API"""
    if not (current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    integration = ApiIntegration.query.get_or_404(integration_id)
    
    if request.method == 'POST':
        try:
            # Validar configuración de mapeo JSON
            mapping_config = request.form.get('mapping_config', '{}')
            try:
                json.loads(mapping_config)
            except json.JSONDecodeError:
                flash('La configuración de mapeo debe ser JSON válido', 'error')
                return render_template('edit_api_integration.html', integration=integration)
            
            integration.name = request.form['name']
            integration.api_type = request.form['api_type']
            integration.url = request.form['url']
            integration.api_key = request.form.get('api_key', '').strip() or None
            integration.headers = request.form.get('headers', '').strip() or None
            integration.request_method = request.form.get('request_method', 'GET')
            integration.request_body = request.form.get('request_body', '').strip() or None
            integration.mapping_config = mapping_config
            integration.refresh_interval = int(request.form.get('refresh_interval', 60))
            integration.is_active = 'is_active' in request.form
            integration.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Integración de API actualizada correctamente', 'success')
            return redirect(url_for('calendar.api_integrations'))
            
        except Exception as e:
            flash(f'Error al actualizar la integración: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_api_integration.html', integration=integration)

@bp.route('/api-integrations/<int:integration_id>/test')
@login_required
def test_api_integration(integration_id):
    """Probar conexión con una integración de API"""
    if not (current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    integration = ApiIntegration.query.get_or_404(integration_id)
    result = ApiIntegrationService.test_api_connection(integration)
    
    return jsonify(result)

@bp.route('/api-integrations/<int:integration_id>/sync')
@login_required
def sync_api_integration(integration_id):
    """Sincronizar datos de una integración específica"""
    if not (current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    integration = ApiIntegration.query.get_or_404(integration_id)
    result = ApiIntegrationService.fetch_api_data(integration)
    
    if result['success']:
        flash(f'Sincronización exitosa: {result["entries_count"]} entradas procesadas', 'success')
    else:
        flash(f'Error en sincronización: {result["message"]}', 'error')
    
    return redirect(url_for('calendar.api_integrations'))

@bp.route('/api-integrations/<int:integration_id>/delete', methods=['POST'])
@login_required
def delete_api_integration(integration_id):
    """Eliminar integración de API"""
    if not (current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    integration = ApiIntegration.query.get_or_404(integration_id)
    
    try:
        # Eliminar datos asociados
        ApiData.query.filter_by(integration_id=integration_id).delete()
        
        # Eliminar integración
        db.session.delete(integration)
        db.session.commit()
        
        flash('Integración eliminada correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la integración: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('calendar.api_integrations'))

@bp.route('/sync-all-apis')
@login_required
def sync_all_apis():
    """Sincronizar todas las APIs activas"""
    if not (current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    results = ApiIntegrationService.sync_all_active_integrations()
    
    success_count = sum(1 for r in results if r['result']['success'])
    total_count = len(results)
    
    if total_count == 0:
        flash('No hay integraciones activas para sincronizar', 'info')
    elif success_count == total_count:
        flash(f'Todas las integraciones sincronizadas correctamente ({success_count}/{total_count})', 'success')
    else:
        flash(f'Sincronización parcial: {success_count}/{total_count} integraciones exitosas', 'warning')
    
    return redirect(url_for('calendar.api_integrations'))

# =============================================================================
# RUTAS PARA NOTAS DEL CALENDARIO
# =============================================================================

@bp.route('/notes/<date_str>')
@login_required
@requires_privilege('can_view_calendar')
def view_notes(date_str):
    """Ver notas de un día específico"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Filtrar notas según permisos
        if current_user.is_admin or current_user.is_super_admin:
            notes = CalendarNote.query.filter_by(date_for=date_obj).order_by(CalendarNote.priority.desc(), CalendarNote.created_at.desc()).all()
        else:
            notes = CalendarNote.query.filter(
                CalendarNote.date_for == date_obj,
                (CalendarNote.is_private == False) | 
                (CalendarNote.created_by == current_user.id)
            ).order_by(CalendarNote.priority.desc(), CalendarNote.created_at.desc()).all()
        
        return render_template('calendar_notes.html', date=date_obj, date_str=date_str, notes=notes)
        
    except ValueError:
        flash('Fecha inválida', 'error')
        return redirect(url_for('calendar.index'))

@bp.route('/notes/<date_str>/create', methods=['GET', 'POST'])
@login_required
@requires_privilege('can_view_calendar')
def create_note(date_str):
    """Crear nueva nota para una fecha"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Fecha inválida', 'error')
        return redirect(url_for('calendar.index'))
    
    if request.method == 'POST':
        try:
            reminder_time = None
            if request.form.get('reminder_time'):
                reminder_time = datetime.strptime(request.form['reminder_time'], '%H:%M').time()
            
            note = CalendarNote(
                date_for=date_obj,
                title=request.form['title'],
                content=request.form.get('content', '').strip() or None,
                color=request.form.get('color', '#ffc107'),
                priority=request.form.get('priority', 'normal'),
                is_private='is_private' in request.form,
                is_reminder='is_reminder' in request.form,
                reminder_time=reminder_time,
                created_by=current_user.id
            )
            
            db.session.add(note)
            db.session.commit()
            
            flash('Nota creada correctamente', 'success')
            return redirect(url_for('calendar.view_notes', date_str=date_str))
            
        except Exception as e:
            flash(f'Error al crear la nota: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('create_note.html', date=date_obj, date_str=date_str)

@bp.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Editar nota existente"""
    note = CalendarNote.query.get_or_404(note_id)
    
    # Verificar permisos: solo el creador o admins pueden editar
    if not (note.created_by == current_user.id or current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    if request.method == 'POST':
        try:
            reminder_time = None
            if request.form.get('reminder_time'):
                reminder_time = datetime.strptime(request.form['reminder_time'], '%H:%M').time()
            
            note.title = request.form['title']
            note.content = request.form.get('content', '').strip() or None
            note.color = request.form.get('color', '#ffc107')
            note.priority = request.form.get('priority', 'normal')
            note.is_private = 'is_private' in request.form
            note.is_reminder = 'is_reminder' in request.form
            note.reminder_time = reminder_time
            note.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Nota actualizada correctamente', 'success')
            return redirect(url_for('calendar.view_notes', date_str=note.date_for.strftime('%Y-%m-%d')))
            
        except Exception as e:
            flash(f'Error al actualizar la nota: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_note.html', note=note)

@bp.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    """Eliminar nota"""
    note = CalendarNote.query.get_or_404(note_id)
    date_str = note.date_for.strftime('%Y-%m-%d')
    
    # Verificar permisos: solo el creador o admins pueden eliminar
    if not (note.created_by == current_user.id or current_user.is_admin or current_user.is_super_admin):
        abort(403)
    
    try:
        db.session.delete(note)
        db.session.commit()
        flash('Nota eliminada correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la nota: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('calendar.view_notes', date_str=date_str))

@bp.route('/api/notes/<date_str>')
@login_required
def api_get_notes(date_str):
    """API para obtener notas de una fecha (JSON)"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Filtrar notas según permisos
        if current_user.is_admin or current_user.is_super_admin:
            notes = CalendarNote.query.filter_by(date_for=date_obj).all()
        else:
            notes = CalendarNote.query.filter(
                CalendarNote.date_for == date_obj,
                (CalendarNote.is_private == False) | 
                (CalendarNote.created_by == current_user.id)
            ).all()
        
        notes_data = []
        for note in notes:
            notes_data.append({
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'color': note.color,
                'priority': note.priority,
                'is_private': note.is_private,
                'is_reminder': note.is_reminder,
                'reminder_time': note.reminder_time.strftime('%H:%M') if note.reminder_time else None,
                'creator': note.creator.full_name or note.creator.username,
                'created_at': note.created_at.isoformat()
            })
        
        return jsonify({'notes': notes_data})
        
    except ValueError:
        return jsonify({'error': 'Fecha inválida'}), 400
