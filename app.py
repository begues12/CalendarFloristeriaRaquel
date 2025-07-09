from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime, date, timedelta
import calendar
import os
from PIL import Image
from dotenv import load_dotenv

# Importar modelos
from models import db, User, TimeEntry, UserDocument, Photo

# Cargar variables de entorno
load_dotenv()

# Configuración desde variables de entorno
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_clave_secreta_muy_segura_aqui_cambiar_en_produccion'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    DOCUMENTS_FOLDER = os.environ.get('DOCUMENTS_FOLDER') or 'static/documents'
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB por defecto
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,pdf,doc,docx').split(','))
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///floristeria.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de la aplicación
    APP_NAME = os.environ.get('APP_NAME') or 'Floristería Raquel'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST') or '0.0.0.0'
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Usuarios por defecto
    DEFAULT_ADMIN_USER = os.environ.get('DEFAULT_ADMIN_USER') or 'admin'
    DEFAULT_ADMIN_PASS = os.environ.get('DEFAULT_ADMIN_PASS') or 'admin123'
    DEFAULT_USER_USER = os.environ.get('DEFAULT_USER_USER') or 'raquel'
    DEFAULT_USER_PASS = os.environ.get('DEFAULT_USER_PASS') or 'floreria2025'

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
migrate = Migrate(app, db)

# Registrar filtros personalizados para Jinja2
@app.template_filter('hours_to_hhmm')
def hours_to_hhmm_filter(hours_decimal):
    """Filtro Jinja2 para convertir horas decimales a HH:MM"""
    return hours_to_hhmm(hours_decimal)

@app.template_filter('strftime')
def strftime_filter(date, format='%Y-%m-%d'):
    """Filtro Jinja2 para formatear fechas"""
    if date:
        return date.strftime(format)
    return ''

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def check_password_change_required():
    """Middleware para verificar si el usuario debe cambiar su contraseña"""
    # Rutas que no requieren verificación de cambio de contraseña
    exempt_routes = [
        'login', 
        'logout', 
        'force_change_password', 
        'static'
    ]
    
    # Si es una solicitud de archivo estático, permitir
    if request.endpoint and request.endpoint in exempt_routes:
        return
    
    # Si el usuario está autenticado y debe cambiar contraseña
    if current_user.is_authenticated and hasattr(current_user, 'must_change_password'):
        if current_user.must_change_password and request.endpoint != 'force_change_password':
            return redirect(url_for('force_change_password'))

# Crear carpetas necesarias
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.DOCUMENTS_FOLDER, exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('templates', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(800, 600)):
    """Redimensiona imagen para optimizar el almacenamiento"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, optimize=True, quality=85)
    except Exception as e:
        print(f"Error redimensionando imagen: {e}")

def hours_to_hhmm(hours_decimal):
    """Convierte horas decimales a formato HH:MM"""
    if not hours_decimal:
        return "00:00"
    
    total_minutes = int(hours_decimal * 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"

def init_default_users():
    """Crear usuarios por defecto si no existen"""
    if not User.query.first():
        # Crear admin
        admin = User(
            username=Config.DEFAULT_ADMIN_USER,
            full_name='Administrador',
            is_admin=True,
            must_change_password=False  # Admin por defecto no necesita cambiar contraseña
        )
        admin.set_password(Config.DEFAULT_ADMIN_PASS)
        
        # Crear usuario regular
        user = User(
            username=Config.DEFAULT_USER_USER,
            full_name='Raquel',
            is_admin=False,
            must_change_password=True  # Usuario debe cambiar contraseña en primer acceso
        )
        user.set_password(Config.DEFAULT_USER_PASS)
        
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

# Rutas principales
@app.route('/')
@login_required
def index():
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            login_user(user)
            
            # Verificar si debe cambiar contraseña
            if user.must_change_password:
                flash('Debes cambiar tu contraseña antes de continuar', 'warning')
                return redirect(url_for('force_change_password'))
            
            next_page = request.args.get('next')
            flash(f'¡Bienvenido {username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/force_change_password', methods=['GET', 'POST'])
@login_required
def force_change_password():
    """Cambio obligatorio de contraseña en primer acceso"""
    # Si el usuario ya no necesita cambiar contraseña, redirigir
    if not current_user.must_change_password:
        return redirect(url_for('index'))
    
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
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('force_change_password.html')

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Crear nuevo usuario - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para crear usuarios', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validaciones
        if not username or not password:
            flash('El nombre de usuario y contraseña son obligatorios', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        if len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres', 'error')
            return render_template('register.html')
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return render_template('register.html')
        
        try:
            # Crear nuevo usuario
            new_user = User(
                username=username,
                full_name=username.title(),  # Usar username como nombre completo por defecto
                is_admin=False,
                must_change_password=True  # Obligar cambio de contraseña en primer acceso
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'Usuario {username} creado correctamente', 'success')
            return redirect(url_for('manage_users'))
            
        except Exception as e:
            flash(f'Error al crear el usuario: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('register.html')

@app.route('/manage_users')
@login_required
def manage_users():
    """Gestión de usuarios - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para gestionar usuarios', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """Activar/desactivar usuario - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para modificar usuarios', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # No permitir desactivar el propio usuario admin
    if user.id == current_user.id:
        flash('No puedes desactivar tu propio usuario', 'error')
        return redirect(url_for('manage_users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activado' if user.is_active else 'desactivado'
        flash(f'Usuario {user.username} {status} correctamente', 'success')
        
    except Exception as e:
        flash(f'Error al modificar el usuario: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('manage_users'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña del usuario actual"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validaciones
        if not current_user.check_password(current_password):
            flash('La contraseña actual es incorrecta', 'error')
            return render_template('change_password.html', user=current_user)
        
        if new_password != confirm_password:
            flash('Las nuevas contraseñas no coinciden', 'error')
            return render_template('change_password.html', user=current_user)
        
        if len(new_password) < 4:
            flash('La nueva contraseña debe tener al menos 4 caracteres', 'error')
            return render_template('change_password.html', user=current_user)
        
        try:
            current_user.set_password(new_password)
            current_user.must_change_password = False  # Ya no necesita cambiar contraseña
            db.session.commit()
            flash('Contraseña cambiada correctamente', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('change_password.html', user=current_user)

@app.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password_admin(user_id):
    """Cambiar contraseña de cualquier usuario - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para cambiar contraseñas de otros usuarios', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validaciones
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('change_password.html', user=user, admin_mode=True)
        
        if len(new_password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres', 'error')
            return render_template('change_password.html', user=user, admin_mode=True)
        
        try:
            user.set_password(new_password)
            db.session.commit()
            flash(f'Contraseña de {user.username} cambiada correctamente', 'success')
            return redirect(url_for('manage_users'))
            
        except Exception as e:
            flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('change_password.html', user=user, admin_mode=True)

@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    """Eliminar usuario - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para eliminar usuarios', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # No permitir eliminar el usuario admin principal o el propio usuario
    if user.username == 'admin' or user.id == current_user.id:
        flash('No puedes eliminar este usuario', 'error')
        return redirect(url_for('manage_users'))
    
    if request.method == 'POST':
        try:
            # Antes de eliminar, actualizar registros relacionados para mantener integridad
            # Cambiar el propietario de documentos a "usuario eliminado"
            UserDocument.query.filter_by(user_id=user.id).update({
                'uploaded_by': f'[Usuario eliminado: {user.username}]'
            })
            
            # Cambiar el propietario de fotos a "usuario eliminado"
            Photo.query.filter_by(uploaded_by=user.username).update({
                'uploaded_by': f'[Usuario eliminado: {user.username}]'
            })
            
            # Mantener los registros de tiempo pero marcar usuario como eliminado
            TimeEntry.query.filter_by(user_id=user.id).update({
                'notes': TimeEntry.notes + f' [Usuario {user.username} eliminado]'
            })
            
            # Eliminar el usuario
            db.session.delete(user)
            db.session.commit()
            
            flash(f'Usuario {user.username} eliminado correctamente', 'success')
            
        except Exception as e:
            flash(f'Error al eliminar el usuario: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('manage_users'))
    
    # Mostrar confirmación
    return render_template('confirm_delete_user.html', user=user)

# Rutas de fichaje
@app.route('/clock_in')
@login_required
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
    
    return redirect(url_for('time_tracking'))

@app.route('/clock_out')
@login_required
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
    
    return redirect(url_for('time_tracking'))

@app.route('/break_start')
@login_required
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
    
    return redirect(url_for('time_tracking'))

@app.route('/break_end')
@login_required
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
    
    return redirect(url_for('time_tracking'))

@app.route('/time_tracking')
@login_required
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

@app.route('/time_reports')
@login_required
def time_reports():
    """Reportes de horarios - solo admin puede ver todos los usuarios"""
    if not current_user.is_admin:
        flash('No tienes permisos para ver esta página', 'error')
        return redirect(url_for('time_tracking'))
    
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
    
    if user_id:
        query = query.filter(TimeEntry.user_id == user_id)
    
    query = query.filter(
        TimeEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
        TimeEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
    )
    
    entries = query.order_by(TimeEntry.date.desc()).all()
    users = User.query.filter_by(is_active=True).all()
    
    # Calcular resumen por usuario si hay datos
    summary = []
    if entries:
        from collections import defaultdict
        user_stats = defaultdict(lambda: {'total_hours': 0, 'total_days': 0, 'username': ''})
        
        for entry in entries:
            user_stats[entry.user_id]['username'] = entry.user.username
            if entry.total_hours:
                user_stats[entry.user_id]['total_hours'] += entry.total_hours
            if entry.entry_time:  # Solo contar días que fichó entrada
                user_stats[entry.user_id]['total_days'] += 1
        
        # Convertir a lista para el template
        summary_list = []
        for user_id, stats in user_stats.items():
            summary_list.append({
                'username': stats['username'],
                'total_hours': hours_to_hhmm(stats['total_hours']),
                'total_hours_decimal': stats['total_hours'],  # Para ordenar
                'total_days': stats['total_days']
            })
        
        # Ordenar por horas trabajadas (descendente)
        summary = sorted(summary_list, key=lambda x: x['total_hours_decimal'], reverse=True)
    
    return render_template('time_reports.html',
                         entries=entries,
                         users=users,
                         summary=summary,
                         selected_user_id=user_id,
                         start_date=start_date,
                         end_date=end_date)

@app.route('/edit_time_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_time_entry(entry_id):
    """Editar registro de tiempo - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para editar registros', 'error')
        return redirect(url_for('time_tracking'))
    
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
            return redirect(url_for('time_reports'))
            
        except ValueError as e:
            flash(f'Error en el formato de hora: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error al actualizar el registro: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_time_entry.html', entry=entry)

@app.route('/delete_time_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_time_entry(entry_id):
    """Eliminar registro de tiempo - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para eliminar registros', 'error')
        return redirect(url_for('time_tracking'))
    
    entry = TimeEntry.query.get_or_404(entry_id)
    
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Registro eliminado correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el registro: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('time_reports'))

@app.route('/export_time_report')
@login_required
def export_time_report():
    """Exportar reporte de horarios a CSV - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para exportar reportes', 'error')
        return redirect(url_for('time_tracking'))
    
    import csv
    import io
    from flask import make_response
    
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
        total_hours = hours_to_hhmm(entry.total_hours) if entry.total_hours else '-'
        
        writer.writerow([
            entry.user.username,
            entry.date.strftime('%d/%m/%Y'),
            entry_time,
            exit_time,
            total_hours,
            entry.get_status_display()
        ])
    
    # Crear respuesta
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_horarios_{start_date}_a_{end_date}.csv'
    
    return response

@app.route('/upload_document', methods=['GET', 'POST'])
@login_required
def upload_document():
    """Subir documentos personales"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        document_type = request.form.get('document_type')
        description = request.form.get('description', '')
        date_related = request.form.get('date_related')
        
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Crear carpeta para documentos del usuario
            user_folder = os.path.join(Config.DOCUMENTS_FOLDER, str(current_user.id))
            os.makedirs(user_folder, exist_ok=True)
            
            # Generar nombre único
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            new_filename = f"{document_type}_{timestamp}_{name}{ext}"
            
            file_path = os.path.join(user_folder, new_filename)
            file.save(file_path)
            
            # Guardar en base de datos
            document = UserDocument(
                user_id=current_user.id,
                filename=new_filename,
                original_filename=filename,
                file_path=file_path,
                file_type=ext[1:].lower(),
                document_type=document_type,
                description=description,
                date_related=datetime.strptime(date_related, '%Y-%m-%d').date() if date_related else None,
                uploaded_by=current_user.username
            )
            
            db.session.add(document)
            db.session.commit()
            
            flash('Documento subido correctamente', 'success')
            return redirect(url_for('my_documents'))
        else:
            flash('Tipo de archivo no permitido', 'error')
    
    return render_template('upload_document.html')

@app.route('/my_documents')
@login_required
def my_documents():
    """Ver documentos personales"""
    documents = UserDocument.query.filter_by(user_id=current_user.id).order_by(
        UserDocument.uploaded_at.desc()
    ).all()
    
    return render_template('my_documents.html', documents=documents)

@app.route('/download_document/<int:doc_id>')
@login_required
def download_document(doc_id):
    """Descargar documento propio"""
    document = UserDocument.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    
    try:
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.original_filename
        )
    except FileNotFoundError:
        flash('El archivo no existe en el servidor', 'error')
        return redirect(url_for('my_documents'))

@app.route('/delete_document/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    """Eliminar documento propio"""
    document = UserDocument.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    
    try:
        # Eliminar archivo físico
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Eliminar registro de la base de datos
        db.session.delete(document)
        db.session.commit()
        
        flash('Documento eliminado correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar el documento', 'error')
        db.session.rollback()
    
    return redirect(url_for('my_documents'))

@app.route('/admin_documents')
@login_required
def admin_documents():
    """Ver todos los documentos - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para ver esta página', 'error')
        return redirect(url_for('my_documents'))
    
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
    
    # Obtener usuarios activos para el filtro
    users = User.query.filter_by(is_active=True).all()
    
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

@app.route('/admin_download_document/<int:doc_id>')
@login_required
def admin_download_document(doc_id):
    """Descargar cualquier documento - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para descargar este documento', 'error')
        return redirect(url_for('my_documents'))
    
    document = UserDocument.query.get_or_404(doc_id)
    
    try:
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=f"{document.user.username}_{document.filename}"
        )
    except FileNotFoundError:
        flash('El archivo no existe en el servidor', 'error')
        return redirect(url_for('admin_documents'))

@app.route('/admin_delete_document/<int:doc_id>', methods=['POST'])
@login_required
def admin_delete_document(doc_id):
    """Eliminar cualquier documento - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para eliminar documentos', 'error')
        return redirect(url_for('my_documents'))
    
    document = UserDocument.query.get_or_404(doc_id)
    
    try:
        # Eliminar archivo físico
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Eliminar registro de la base de datos
        db.session.delete(document)
        db.session.commit()
        
        flash(f'Documento de {document.user.username} eliminado correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar el documento', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_documents'))

@app.route('/create_time_entry', methods=['GET', 'POST'])
@login_required
def create_time_entry():
    """Crear nuevo registro de tiempo - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para crear registros', 'error')
        return redirect(url_for('time_tracking'))
    
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
                return render_template('create_time_entry.html', users=User.query.filter_by(is_active=True).all())
            
            # Verificar que no existe ya un registro para esa fecha y usuario
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            existing = TimeEntry.query.filter_by(user_id=user_id, date=entry_date).first()
            if existing:
                flash(f'Ya existe un registro para ese usuario en la fecha {entry_date.strftime("%d/%m/%Y")}', 'error')
                return render_template('create_time_entry.html', users=User.query.filter_by(is_active=True).all())
            
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
            return redirect(url_for('time_reports'))
            
        except ValueError as e:
            flash(f'Error en el formato de fecha/hora: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error al crear el registro: {str(e)}', 'error')
            db.session.rollback()
    
    users = User.query.filter_by(is_active=True).all()
    today = date.today()
    return render_template('create_time_entry.html', users=users, today=today)

@app.route('/day/<string:date_str>')
@login_required
def view_day(date_str):
    """Ver fotos de un día específico"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Fecha inválida', 'error')
        return redirect(url_for('index'))
    
    photos = Photo.query.filter_by(date_taken=date_obj).order_by(Photo.uploaded_at.desc()).all()
    
    return render_template('day.html', 
                         date=date_obj,
                         date_str=date_str,
                         photos=photos)

@app.route('/upload/<string:date_str>', methods=['GET', 'POST'])
@login_required
def upload_photo(date_str):
    """Subir fotos para un día específico"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Fecha inválida', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('file')
        if not files or files[0].filename == '':
            flash('No se seleccionaron archivos', 'error')
            return redirect(request.url)
        
        uploaded_count = 0
        for file in files:
            if file and allowed_file(file.filename):
                # Crear carpeta para la fecha
                date_folder = date_obj.strftime('%Y-%m-%d')
                upload_path = os.path.join(Config.UPLOAD_FOLDER, date_folder)
                os.makedirs(upload_path, exist_ok=True)
                
                # Generar nombre único
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%H%M%S')
                name, ext = os.path.splitext(filename)
                new_filename = f"image_{len(os.listdir(upload_path)) + 1}_{timestamp}{ext}"
                
                file_path = os.path.join(upload_path, new_filename)
                file.save(file_path)
                
                # Redimensionar imagen
                resize_image(file_path)
                
                # Guardar en base de datos
                photo = Photo(
                    filename=new_filename,
                    original_filename=filename,  # Agregar el nombre original del archivo
                    file_path=os.path.join('uploads', date_folder, new_filename).replace('\\', '/'),
                    date_taken=date_obj,
                    uploaded_by=current_user.username,
                    status='pendiente'
                )
                
                db.session.add(photo)
                uploaded_count += 1
        
        if uploaded_count > 0:
            db.session.commit()
            flash(f'{uploaded_count} foto(s) subida(s) correctamente', 'success')
        else:
            flash('No se pudieron subir las fotos. Verifica el formato.', 'error')
        
        return redirect(url_for('view_day', date_str=date_str))
    
    return render_template('upload.html', 
                         date=date_obj, 
                         date_str=date_str)

@app.route('/update_photo_status/<int:photo_id>', methods=['POST'])
@login_required
def update_photo_status(photo_id):
    """Actualizar estado de una foto"""
    photo = Photo.query.get_or_404(photo_id)
    new_status = request.form.get('status')
    
    if new_status in ['pendiente', 'hecho', 'entregado']:
        photo.status = new_status
        db.session.commit()
        flash('Estado actualizado correctamente', 'success')
    else:
        flash('Estado inválido', 'error')
    
    return redirect(url_for('view_day', date_str=photo.date_taken.strftime('%Y-%m-%d')))

@app.route('/change_status/<int:photo_id>/<string:new_status>')
@login_required
def change_status(photo_id, new_status):
    """Cambiar estado de una foto via GET"""
    photo = Photo.query.get_or_404(photo_id)
    
    if new_status in ['pendiente', 'hecho', 'entregado']:
        photo.status = new_status
        db.session.commit()
        flash(f'Foto marcada como {new_status}', 'success')
    else:
        flash('Estado inválido', 'error')
    
    return redirect(url_for('view_day', date_str=photo.date_taken.strftime('%Y-%m-%d')))

@app.route('/delete_photo/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def delete_photo(photo_id):
    """Eliminar una foto"""
    photo = Photo.query.get_or_404(photo_id)
    date_str = photo.date_taken.strftime('%Y-%m-%d')
    
    if request.method == 'GET':
        # Mostrar página de confirmación
        return render_template('confirm_delete_photo.html', photo=photo, date_str=date_str)
    
    # POST - proceder con la eliminación
    try:
        # Eliminar archivo físico
        full_path = os.path.join(Config.UPLOAD_FOLDER, photo.file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        
        # Eliminar de la base de datos
        db.session.delete(photo)
        db.session.commit()
        
        flash('Foto eliminada correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar la foto', 'error')
        db.session.rollback()
    
    return redirect(url_for('view_day', date_str=date_str))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_users()
    
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
