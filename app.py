from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import json
from datetime import datetime, date
import calendar
from PIL import Image
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración desde variables de entorno
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_clave_secreta_muy_segura_aqui_cambiar_en_produccion'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    USERS_FILE = os.environ.get('USERS_FILE') or 'users.json'
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB por defecto
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(','))
    
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
app.secret_key = Config.SECRET_KEY

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Configuración
UPLOAD_FOLDER = Config.UPLOAD_FOLDER
USERS_FILE = Config.USERS_FILE
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
MAX_FILE_SIZE = Config.MAX_FILE_SIZE

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear carpetas necesarias
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Clase Usuario
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Funciones de gestión de usuarios
def load_users():
    """Cargar usuarios desde archivo JSON"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Guardar usuarios en archivo JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(user_id):
    """Obtener usuario por ID"""
    users = load_users()
    if user_id in users:
        user_data = users[user_id]
        return User(user_id, user_data['username'], user_data['password_hash'])
    return None

def create_user(username, password):
    """Crear un nuevo usuario"""
    users = load_users()
    
    # Verificar si el usuario ya existe
    for user_data in users.values():
        if user_data['username'] == username:
            return False, "El usuario ya existe"
    
    # Crear nuevo usuario
    user_id = str(len(users) + 1)
    password_hash = generate_password_hash(password)
    
    users[user_id] = {
        'username': username,
        'password_hash': password_hash
    }
    
    save_users(users)
    return True, "Usuario creado correctamente"

def authenticate_user(username, password):
    """Autenticar usuario"""
    users = load_users()
    for user_id, user_data in users.items():
        if user_data['username'] == username:
            if check_password_hash(user_data['password_hash'], password):
                return User(user_id, username, user_data['password_hash'])
    return None

@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

# Crear usuario admin por defecto si no existe
def init_default_users():
    users = load_users()
    if not users:
        create_user(Config.DEFAULT_ADMIN_USER, Config.DEFAULT_ADMIN_PASS)
        create_user(Config.DEFAULT_USER_USER, Config.DEFAULT_USER_PASS)

init_default_users()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_photos_for_date(date_str):
    """Obtiene todas las fotos para una fecha específica con información del usuario y estado"""
    date_folder = os.path.join(UPLOAD_FOLDER, date_str)
    if not os.path.exists(date_folder):
        return []
    
    photos = []
    for filename in os.listdir(date_folder):
        if allowed_file(filename):
            # Buscar archivo de metadatos
            metadata_file = os.path.join(date_folder, f"{filename}.json")
            uploaded_by = "Desconocido"
            upload_time = ""
            status = "pendiente"  # Estado por defecto
            
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        uploaded_by = metadata.get('username', 'Desconocido')
                        upload_time_str = metadata.get('upload_time', '')
                        status = metadata.get('status', 'pendiente')
                        
                        # Formatear la fecha para mostrar correctamente
                        if upload_time_str:
                            try:
                                # Convertir string a datetime y luego formatear
                                dt = datetime.strptime(upload_time_str, '%Y-%m-%d %H:%M:%S')
                                upload_time = dt.strftime('%d/%m/%Y %H:%M')
                            except:
                                upload_time = upload_time_str  # Si hay error, usar el string original
                        else:
                            upload_time = ""
                except:
                    pass
            
            photos.append({
                'filename': filename,
                'path': f'uploads/{date_str}/{filename}',
                'uploaded_by': uploaded_by,
                'upload_time': upload_time,
                'status': status
            })
    return photos

def resize_image(image_path, max_size=(800, 600)):
    """Redimensiona imagen para optimizar el almacenamiento"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, optimize=True, quality=85)
    except Exception as e:
        print(f"Error redimensionando imagen: {e}")

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
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                photos = get_photos_for_date(date_str)
                photos_by_date[day] = photos
                
                # Contar estados
                status_counts = {'pendiente': 0, 'hecho': 0, 'entregado': 0}
                for photo in photos:
                    status = photo.get('status', 'pendiente')
                    if status in status_counts:
                        status_counts[status] += 1
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
        
        user = authenticate_user(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido {username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Solo el administrador puede crear nuevos usuarios
    if current_user.username != 'admin':
        flash('Solo el administrador puede crear nuevos usuarios', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
        elif len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres', 'error')
        else:
            success, message = create_user(username, password)
            if success:
                flash(message, 'success')
                return redirect(url_for('index'))
            else:
                flash(message, 'error')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

@app.route('/day/<date_str>')
@login_required
def view_day(date_str):
    """Ver fotos de un día específico"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        photos = get_photos_for_date(date_str)
        
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
        # Verificar si se seleccionó un archivo
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('file')
        uploaded_count = 0
        
        for file in files:
            if file.filename == '':
                continue
                
            if file and allowed_file(file.filename):
                # Crear carpeta para la fecha si no existe
                date_folder = os.path.join(UPLOAD_FOLDER, date_str)
                os.makedirs(date_folder, exist_ok=True)
                
                # Generar nombre de archivo único
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%H%M%S')
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                
                file_path = os.path.join(date_folder, filename)
                file.save(file_path)
                
                # Redimensionar imagen
                resize_image(file_path)
                
                # Guardar metadatos del archivo
                metadata = {
                    'username': current_user.username,
                    'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'original_filename': file.filename,
                    'status': 'pendiente'  # Estado inicial
                }
                
                metadata_path = os.path.join(date_folder, f"{filename}.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                uploaded_count += 1
            else:
                flash(f'Archivo no válido: {file.filename}', 'error')
        
        if uploaded_count > 0:
            flash(f'Se subieron {uploaded_count} foto(s) correctamente', 'success')
        
        return redirect(url_for('view_day', date_str=date_str))
    
    photos = get_photos_for_date(date_str)
    return render_template('upload.html',
                         date=date_obj,
                         date_str=date_str,
                         photos=photos)

@app.route('/delete_photo/<date_str>/<filename>')
@login_required
def delete_photo(date_str, filename):
    """Eliminar una foto"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, date_str, secure_filename(filename))
        metadata_path = os.path.join(UPLOAD_FOLDER, date_str, f"{secure_filename(filename)}.json")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            # Eliminar también el archivo de metadatos
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            flash('Foto eliminada correctamente', 'success')
        else:
            flash('Archivo no encontrado', 'error')
    except Exception as e:
        flash('Error al eliminar la foto', 'error')
    
    return redirect(url_for('view_day', date_str=date_str))

@app.route('/change_status/<date_str>/<filename>/<new_status>')
@login_required
def change_status(date_str, filename, new_status):
    """Cambiar el estado de una foto"""
    valid_statuses = ['pendiente', 'hecho', 'entregado']
    
    if new_status not in valid_statuses:
        flash('Estado no válido', 'error')
        return redirect(url_for('view_day', date_str=date_str))
    
    try:
        metadata_path = os.path.join(UPLOAD_FOLDER, date_str, f"{secure_filename(filename)}.json")
        
        if os.path.exists(metadata_path):
            # Leer metadatos existentes
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Actualizar estado
            metadata['status'] = new_status
            metadata['status_updated_by'] = current_user.username
            metadata['status_updated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Guardar metadatos actualizados
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            status_names = {
                'pendiente': 'Pendiente',
                'hecho': 'Hecho',
                'entregado': 'Entregado'
            }
            flash(f'Estado cambiado a: {status_names[new_status]}', 'success')
        else:
            flash('Archivo de metadatos no encontrado', 'error')
    except Exception as e:
        flash('Error al cambiar el estado', 'error')
    
    return redirect(url_for('view_day', date_str=date_str))

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
