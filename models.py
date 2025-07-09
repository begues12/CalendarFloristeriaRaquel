from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    time_entries = db.relationship('TimeEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('UserDocument', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
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
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, jpg, png, etc.
    document_type = db.Column(db.String(50), nullable=False)  # justificante, contrato, nomina, etc.
    description = db.Column(db.Text, nullable=True)
    date_related = db.Column(db.Date, nullable=True)  # Fecha relacionada con el documento
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.String(80), nullable=False)  # Usuario que subió el documento
    
    def get_document_type_display(self):
        type_map = {
            'justificante': 'Justificante',
            'contrato': 'Contrato',
            'nomina': 'Nómina',
            'vacaciones': 'Solicitud de Vacaciones',
            'medico': 'Justificante Médico',
            'otros': 'Otros'
        }
        return type_map.get(self.document_type, self.document_type)
    
    def __repr__(self):
        return f'<UserDocument {self.filename} - {self.user.username}>'

class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    date_taken = db.Column(db.Date, nullable=False)
    uploaded_by = db.Column(db.String(80), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pendiente')  # pendiente, hecho, entregado
    status_updated_by = db.Column(db.String(80), nullable=True)
    status_updated_at = db.Column(db.DateTime, nullable=True)
    
    def get_status_display(self):
        status_map = {
            'pendiente': 'Pendiente',
            'hecho': 'Hecho', 
            'entregado': 'Entregado'
        }
        return status_map.get(self.status, self.status)
    
    def __repr__(self):
        return f'<Photo {self.filename} - {self.date_taken}>'
