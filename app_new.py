from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

def init_default_users():
    """Crear usuarios por defecto si no existen"""
    if not User.query.first():
        # Crear admin
        admin = User(
            username=Config.DEFAULT_ADMIN_USER,
            full_name='Administrador',
            is_admin=True
        )
        admin.set_password(Config.DEFAULT_ADMIN_PASS)
        
        # Crear usuario regular
        user = User(
            username=Config.DEFAULT_USER_USER,
            full_name='Raquel',
            is_admin=False
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

# Continúa en el siguiente bloque...

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
    
    return render_template('time_reports.html',
                         entries=entries,
                         users=users,
                         selected_user_id=user_id,
                         start_date=start_date,
                         end_date=end_date)

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

@app.route('/manage_users')
@login_required
def manage_users():
    """Panel de gestión de usuarios - solo para admin"""
    if not current_user.is_admin:
        flash('Solo el administrador puede gestionar usuarios', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Crear nuevo usuario - solo admin"""
    if not current_user.is_admin:
        flash('Solo el administrador puede crear nuevos usuarios', 'error')
        return redirect(url_for('index'))
    
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
                is_admin=is_admin
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Usuario {username} creado correctamente', 'success')
            return redirect(url_for('manage_users'))
    
    return render_template('register.html')

@app.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    """Cambiar contraseña - admin puede cambiar cualquiera, usuario solo la suya"""
    user = User.query.get_or_404(user_id)
    
    if not current_user.is_admin and current_user.id != user_id:
        flash('No tienes permisos para cambiar esta contraseña', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
        elif len(new_password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres', 'error')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash(f'Contraseña actualizada para {user.username}', 'success')
            
            if current_user.is_admin:
                return redirect(url_for('manage_users'))
            else:
                return redirect(url_for('index'))
    
    return render_template('change_password.html', user=user, user_id=user_id)

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    """Eliminar usuario - solo admin"""
    if not current_user.is_admin:
        flash('Solo el administrador puede eliminar usuarios', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        flash('No se puede eliminar a un usuario administrador', 'error')
        return redirect(url_for('manage_users'))
    
    username = user.username
    user.is_active = False  # Marcar como inactivo en lugar de eliminar
    db.session.commit()
    
    flash(f'Usuario {username} desactivado. Los datos se conservan.', 'success')
    return redirect(url_for('manage_users'))

# Rutas de fotos (adaptadas a la nueva estructura)
@app.route('/day/<date_str>')
@login_required
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
        return redirect(url_for('index'))

@app.route('/upload/<date_str>', methods=['GET', 'POST'])
@login_required
def upload_photo(date_str):
    """Subir fotos para una fecha específica"""
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
        uploaded_count = 0
        
        for file in files:
            if file.filename == '':
                continue
                
            if file and allowed_file(file.filename):
                # Crear carpeta para la fecha
                date_folder = os.path.join(Config.UPLOAD_FOLDER, date_str)
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
        
        return redirect(url_for('view_day', date_str=date_str))
    
    photos = Photo.query.filter_by(date_taken=date_obj).all()
    return render_template('upload.html',
                         date=date_obj,
                         date_str=date_str,
                         photos=photos)

@app.route('/delete_photo/<int:photo_id>')
@login_required
def delete_photo(photo_id):
    """Eliminar una foto"""
    photo = Photo.query.get_or_404(photo_id)
    date_str = photo.date_taken.strftime('%Y-%m-%d')
    
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
    
    return redirect(url_for('view_day', date_str=date_str))

@app.route('/change_status/<int:photo_id>/<new_status>')
@login_required
def change_status(photo_id, new_status):
    """Cambiar el estado de una foto"""
    valid_statuses = ['pendiente', 'hecho', 'entregado']
    
    if new_status not in valid_statuses:
        flash('Estado no válido', 'error')
        return redirect(url_for('index'))
    
    photo = Photo.query.get_or_404(photo_id)
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
    
    return redirect(url_for('view_day', date_str=date_str))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_users()
    
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
