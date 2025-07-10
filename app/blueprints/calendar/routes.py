"""
Rutas del calendario: página principal, vista de días, subida y gestión de fotos
"""

from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date
import calendar
import os
from PIL import Image
from app.models import Photo, db
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
    for week in cal:
        for day in week:
            if day > 0:
                date_obj = date(year, month, day)
                photos = Photo.query.filter_by(date_taken=date_obj).all()
                photos_by_date[day] = photos
                
                # Contar estados
                status_counts = {'pendiente': 0, 'hecho': 0, 'entregado': 0}
                for photo in photos:
                    if photo.status in status_counts:
                        status_counts[photo.status] += 1
                status_counts_by_date[day] = status_counts
    
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
        
        return render_template('day.html',
                             date=date_obj,
                             date_str=date_str,
                             photos=photos)
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
