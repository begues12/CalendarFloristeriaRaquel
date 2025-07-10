from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    position = db.Column(db.String(100), nullable=True)  # Cargo/Posición
    hire_date = db.Column(db.Date, nullable=True)  # Fecha de contratación
    
    # Permisos principales
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)  # Super admin para actualizaciones
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=True)  # Obligar cambio en primer acceso
    
    # Privilegios específicos
    can_view_calendar = db.Column(db.Boolean, default=True)  # Ver calendario
    can_upload_photos = db.Column(db.Boolean, default=True)  # Subir fotos
    can_manage_photos = db.Column(db.Boolean, default=False)  # Gestionar fotos de otros
    can_time_tracking = db.Column(db.Boolean, default=True)  # Usar fichaje
    can_view_own_reports = db.Column(db.Boolean, default=True)  # Ver sus propios reportes
    can_view_all_reports = db.Column(db.Boolean, default=False)  # Ver reportes de todos
    can_manage_time_entries = db.Column(db.Boolean, default=False)  # Crear/editar entradas de tiempo
    can_upload_documents = db.Column(db.Boolean, default=True)  # Subir documentos propios
    can_view_own_documents = db.Column(db.Boolean, default=True)  # Ver documentos propios
    can_view_all_documents = db.Column(db.Boolean, default=False)  # Ver documentos de todos
    can_manage_users = db.Column(db.Boolean, default=False)  # Gestionar usuarios
    can_export_data = db.Column(db.Boolean, default=False)  # Exportar datos
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    time_entries = db.relationship('TimeEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('UserDocument', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_privileges_dict(self):
        """Obtener diccionario de privilegios para plantillas"""
        return {
            'Calendario': {
                'can_view_calendar': {'name': 'Ver calendario', 'value': self.can_view_calendar},
                'can_upload_photos': {'name': 'Subir fotos', 'value': self.can_upload_photos},
                'can_manage_photos': {'name': 'Gestionar fotos de otros', 'value': self.can_manage_photos},
            },
            'Control de Tiempo': {
                'can_time_tracking': {'name': 'Usar fichaje personal', 'value': self.can_time_tracking},
                'can_view_own_reports': {'name': 'Ver propios reportes', 'value': self.can_view_own_reports},
                'can_view_all_reports': {'name': 'Ver reportes de todos', 'value': self.can_view_all_reports},
                'can_manage_time_entries': {'name': 'Crear/editar entradas de tiempo', 'value': self.can_manage_time_entries},
            },
            'Documentos': {
                'can_upload_documents': {'name': 'Subir documentos propios', 'value': self.can_upload_documents},
                'can_view_own_documents': {'name': 'Ver documentos propios', 'value': self.can_view_own_documents},
                'can_view_all_documents': {'name': 'Ver documentos de todos', 'value': self.can_view_all_documents},
            },
            'Administración': {
                'can_manage_users': {'name': 'Gestionar usuarios', 'value': self.can_manage_users},
                'can_export_data': {'name': 'Exportar datos', 'value': self.can_export_data},
            }
        }
    
    def has_privilege(self, privilege_name):
        """Verificar si el usuario tiene un privilegio específico"""
        # Los admins y super admins tienen acceso completo a todo
        if self.is_admin or self.is_super_admin:
            return True
        return getattr(self, privilege_name, False)
    
    def set_default_privileges(self):
        """Establecer privilegios por defecto para nuevos usuarios"""
        self.can_view_calendar = True
        self.can_upload_photos = True
        self.can_time_tracking = True
        self.can_view_own_reports = True
        self.can_upload_documents = True
        self.can_view_own_documents = True
    
    def __repr__(self):
        return f'<User {self.username}>'

class TimeEntry(db.Model):
    __tablename__ = 'time_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    entry_time = db.Column(db.DateTime, nullable=True)  # Hora de entrada
    exit_time = db.Column(db.DateTime, nullable=True)   # Hora de salida
    break_start = db.Column(db.DateTime, nullable=True)  # Inicio descanso
    break_end = db.Column(db.DateTime, nullable=True)    # Fin descanso
    total_hours = db.Column(db.Float, default=0.0)      # Horas totales trabajadas
    break_hours = db.Column(db.Float, default=0.0)      # Horas de descanso
    notes = db.Column(db.Text, nullable=True)           # Notas del día
    status = db.Column(db.String(20), default='active') # active, completed, absent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_total_hours(self):
        """Calcula las horas totales trabajadas"""
        if self.entry_time and self.exit_time:
            total_time = self.exit_time - self.entry_time
            total_hours = total_time.total_seconds() / 3600
            
            # Restar tiempo de descanso si existe
            if self.break_start and self.break_end:
                break_time = self.break_end - self.break_start
                self.break_hours = break_time.total_seconds() / 3600
                total_hours -= self.break_hours
            
            self.total_hours = round(total_hours, 2)
        return self.total_hours
    
    def get_status_display(self):
        status_map = {
            'active': 'Activo',
            'completed': 'Completado',
            'absent': 'Ausente'
        }
        return status_map.get(self.status, self.status)
    
    def __repr__(self):
        return f'<TimeEntry {self.user.username} - {self.date}>'

class UserDocument(db.Model):
    __tablename__ = 'user_documents'
    
    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename            = db.Column(db.String(255), nullable=False)
    original_filename   = db.Column(db.String(255), nullable=False)
    file_path           = db.Column(db.String(500), nullable=False)
    file_type           = db.Column(db.String(10), nullable=False)  # pdf, jpg, png, etc.
    document_type       = db.Column(db.String(50), nullable=False)  # justificante, contrato, nomina, etc.
    description         = db.Column(db.Text, nullable=True)
    date_related        = db.Column(db.Date, nullable=True)  # Fecha relacionada con el documento
    uploaded_at         = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by         = db.Column(db.String(80), nullable=False)  # Usuario que subió el documento
    
    def get_document_type_display(self):
        type_map = {
            'justificante': 'Justificante',
            'contrato':     'Contrato',
            'nomina':       'Nómina',
            'vacaciones':   'Solicitud de Vacaciones',
            'medico':       'Justificante Médico',
            'otros':        'Otros'
        }
        return type_map.get(self.document_type, self.document_type)
    
    def __repr__(self):
        return f'<UserDocument {self.filename} - {self.user.username}>'

class Photo(db.Model):
    __tablename__ = 'photos'
    
    id                  = db.Column(db.Integer, primary_key=True)
    filename            = db.Column(db.String(255), nullable=False)
    original_filename   = db.Column(db.String(255), nullable=False)
    file_path           = db.Column(db.String(500), nullable=False)
    date_taken          = db.Column(db.Date, nullable=False)
    uploaded_by         = db.Column(db.String(80), nullable=False)
    uploaded_at         = db.Column(db.DateTime, default=datetime.utcnow)
    status              = db.Column(db.String(20), default='pendiente')  # pendiente, hecho, entregado
    status_updated_by   = db.Column(db.String(80), nullable=True)
    status_updated_at   = db.Column(db.DateTime, nullable=True)
    
    def get_status_display(self):
        status_map = {
            'pendiente':    'Pendiente',
            'hecho':        'Hecho', 
            'entregado':    'Entregado'
        }
        return status_map.get(self.status, self.status)
    
    def __repr__(self):
        return f'<Photo {self.filename} - {self.date_taken}>'

class MaintenanceMode(db.Model):
    __tablename__ = 'maintenance_mode'
    
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=False)
    message = db.Column(db.Text, nullable=True, default='Sistema en mantenimiento. Volveremos pronto.')
    started_by = db.Column(db.String(80), nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    estimated_end = db.Column(db.DateTime, nullable=True)
    
    @classmethod
    def get_current(cls):
        """Obtiene el estado actual de mantenimiento"""
        maintenance = cls.query.first()
        if not maintenance:
            maintenance = cls(is_active=False)
            db.session.add(maintenance)
            db.session.commit()
        return maintenance
    
    def activate(self, user, message=None, estimated_minutes=30):
        """Activa el modo mantenimiento"""
        self.is_active = True
        self.started_by = user.username
        self.started_at = datetime.utcnow()
        if estimated_minutes:
            self.estimated_end = self.started_at + timedelta(minutes=estimated_minutes)
        if message:
            self.message = message
        db.session.commit()
    
    def deactivate(self):
        """Desactiva el modo mantenimiento"""
        self.is_active = False
        self.started_by = None
        self.started_at = None
        self.estimated_end = None
        db.session.commit()
    
    def __repr__(self):
        return f'<MaintenanceMode {self.is_active}>'

class UpdateLog(db.Model):
    __tablename__ = 'update_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    started_by = db.Column(db.String(80), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, failed
    git_commit_before = db.Column(db.String(40), nullable=True)
    git_commit_after = db.Column(db.String(40), nullable=True)
    migration_output = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def mark_completed(self, commit_after=None):
        """Marca la actualización como completada"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        if commit_after:
            self.git_commit_after = commit_after
        db.session.commit()
    
    def mark_failed(self, error_message):
        """Marca la actualización como fallida"""
        self.status = 'failed'
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        db.session.commit()
    
    def __repr__(self):
        return f'<UpdateLog {self.started_by} - {self.status}>'
