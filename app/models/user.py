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
    can_manage_notes = db.Column(db.Boolean, default=True)  # Gestionar notas del calendario
    
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
                'can_manage_notes': {'name': 'Gestionar notas del calendario', 'value': self.can_manage_notes},
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
        self.can_manage_notes = True
    
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
            
            # Intentar commit con reintentos para evitar database lock
            for attempt in range(3):
                try:
                    db.session.commit()
                    break
                except Exception as e:
                    if "database is locked" in str(e).lower() and attempt < 2:
                        try:
                            db.session.rollback()
                        except:
                            pass
                        import time
                        time.sleep(0.5)
                    else:
                        raise
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
        
        # Intentar commit con reintentos para evitar database lock
        for attempt in range(3):
            try:
                db.session.commit()
                break
            except Exception as e:
                if "database is locked" in str(e).lower() and attempt < 2:
                    try:
                        db.session.rollback()
                    except:
                        pass
                    import time
                    time.sleep(0.5)
                else:
                    raise
    
    def deactivate(self):
        """Desactiva el modo mantenimiento"""
        self.is_active = False
        self.started_by = None
        self.started_at = None
        self.estimated_end = None
        
        # Intentar commit con reintentos para evitar database lock
        for attempt in range(3):
            try:
                db.session.commit()
                break
            except Exception as e:
                if "database is locked" in str(e).lower() and attempt < 2:
                    try:
                        db.session.rollback()
                    except:
                        pass
                    import time
                    time.sleep(0.5)
                else:
                    raise
    
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
        
        # Intentar commit con reintentos para evitar database lock
        for attempt in range(3):
            try:
                db.session.commit()
                break
            except Exception as e:
                if "database is locked" in str(e).lower() and attempt < 2:
                    try:
                        db.session.rollback()
                    except:
                        pass
                    import time
                    time.sleep(0.5)
                else:
                    raise
    
    def mark_failed(self, error_message):
        """Marca la actualización como fallida"""
        self.status = 'failed'
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        
        # Intentar commit con reintentos para evitar database lock
        for attempt in range(3):
            try:
                db.session.commit()
                break
            except Exception as e:
                if "database is locked" in str(e).lower() and attempt < 2:
                    try:
                        db.session.rollback()
                    except:
                        pass
                    import time
                    time.sleep(0.5)
                else:
                    raise
    
    def __repr__(self):
        return f'<UpdateLog {self.started_by} - {self.status}>'

class ApiIntegration(db.Model):
    """Configuraciones de integraciones con APIs externas"""
    __tablename__ = 'api_integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nombre descriptivo
    api_type = db.Column(db.String(50), nullable=False)  # weather, events, tasks, custom, woocommerce
    url = db.Column(db.String(500), nullable=False)  # URL de la API
    api_key = db.Column(db.String(255), nullable=True)  # Clave API (encriptada)
    headers = db.Column(db.Text, nullable=True)  # Headers JSON adicionales
    request_method = db.Column(db.String(10), default='GET')  # GET, POST, etc.
    request_body = db.Column(db.Text, nullable=True)  # Body para POST
    mapping_config = db.Column(db.Text, nullable=False)  # JSON con mapeo de datos
    refresh_interval = db.Column(db.Integer, default=60)  # Minutos entre actualizaciones
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = db.Column(db.DateTime, nullable=True)
    last_sync_status = db.Column(db.String(20), default='pending')  # success, error, pending
    last_error = db.Column(db.Text, nullable=True)
    
    # Relación con el creador
    creator = db.relationship('User', backref='api_integrations')
    
    def get_mapped_value(self, data, field_key):
        """Obtener valor mapeado desde los datos de la API"""
        import json
        try:
            mapping = json.loads(self.mapping_config) if isinstance(self.mapping_config, str) else self.mapping_config
            field_path = mapping.get(field_key)
            if not field_path:
                return None
            
            # Navegar a través del objeto usando dot notation
            value = data
            for key in field_path.split('.'):
                value = value.get(key)
                if value is None:
                    return None
            return value
        except (json.JSONDecodeError, AttributeError, TypeError):
            return None
    
    @classmethod
    def create_woocommerce_integration(cls, name, store_url, consumer_key, consumer_secret, 
                                       integration_type='products', created_by=None):
        """Crear integración WooCommerce con configuración automática"""
        import json
        import base64
        
        # Configuraciones predefinidas para diferentes tipos de WooCommerce
        woocommerce_configs = {
            'products': {
                'endpoint': 'products',
                'params': 'per_page=5&status=publish',
                'mapping': {
                    'display_field': 'name',
                    'image_field': 'images[0].src',
                    'description_field': 'short_description',
                    'link_field': 'permalink',
                    'price_field': 'price_html'
                },
                'refresh_interval': 360  # 6 horas
            },
            'orders': {
                'endpoint': 'orders',
                'params': 'status=processing&per_page=10',
                'mapping': {
                    'display_field': 'billing.first_name',
                    'description_field': 'total',
                    'status_field': 'status',
                    'customer_field': 'billing.email',
                    'items_field': 'line_items[0].name'
                },
                'refresh_interval': 30  # 30 minutos
            },
            'orders_today': {
                'endpoint': 'orders',
                'params': f'after={datetime.now().strftime("%Y-%m-%d")}T00:00:00&per_page=20',
                'mapping': {
                    'display_field': 'billing.first_name',
                    'description_field': 'total',
                    'status_field': 'status',
                    'date_field': 'date_created',
                    'items_field': 'line_items[0].name'
                },
                'refresh_interval': 15  # 15 minutos
            },
            'featured_products': {
                'endpoint': 'products',
                'params': 'featured=true&per_page=3&status=publish',
                'mapping': {
                    'display_field': 'name',
                    'image_field': 'images[0].src',
                    'description_field': 'price_html',
                    'link_field': 'permalink'
                },
                'refresh_interval': 720  # 12 horas
            },
            'low_stock': {
                'endpoint': 'products',
                'params': 'stock_status=lowstock&per_page=10',
                'mapping': {
                    'display_field': 'name',
                    'description_field': 'stock_quantity',
                    'status_field': 'stock_status',
                    'sku_field': 'sku'
                },
                'refresh_interval': 60  # 1 hora
            }
        }
        
        config = woocommerce_configs.get(integration_type, woocommerce_configs['products'])
        
        # Crear credenciales Base64
        credentials = f"{consumer_key}:{consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Headers para WooCommerce
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "User-Agent": "Floristeria-Calendar/1.0"
        }
        
        # URL completa
        clean_url = store_url.rstrip('/')
        full_url = f"{clean_url}/wp-json/wc/v3/{config['endpoint']}?{config['params']}"
        
        # Crear la integración
        integration = cls(
            name=f"{name} - {integration_type.title()}",
            api_type='woocommerce',
            url=full_url,
            headers=json.dumps(headers),
            mapping_config=json.dumps(config['mapping']),
            refresh_interval=config['refresh_interval'],
            created_by=created_by or 1,
            is_active=True
        )
        
        return integration
    
    def is_woocommerce(self):
        """Verificar si es una integración WooCommerce"""
        return self.api_type == 'woocommerce'
    
    def get_woocommerce_type(self):
        """Obtener el tipo específico de WooCommerce basado en la URL"""
        if not self.is_woocommerce():
            return None
            
        if 'orders' in self.url:
            if 'after=' in self.url:
                return 'orders_today'
            return 'orders'
        elif 'featured=true' in self.url:
            return 'featured_products'
        elif 'stock_status=lowstock' in self.url:
            return 'low_stock'
        elif 'products' in self.url:
            return 'products'
        
        return 'custom'
    
    def update_woocommerce_credentials(self, consumer_key, consumer_secret):
        """Actualizar credenciales de WooCommerce"""
        import json
        import base64
        
        if not self.is_woocommerce():
            return False
        
        try:
            # Crear nuevas credenciales
            credentials = f"{consumer_key}:{consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # Actualizar headers
            headers = json.loads(self.headers) if self.headers else {}
            headers["Authorization"] = f"Basic {encoded_credentials}"
            self.headers = json.dumps(headers)
            
            return True
        except Exception:
            return False
    
    def get_woocommerce_display_config(self):
        """Obtener configuración de visualización específica para WooCommerce"""
        wc_type = self.get_woocommerce_type()
        
        display_configs = {
            'products': {
                'icon': 'fas fa-shopping-bag',
                'color': '#28a745',
                'title_template': 'Producto: {name}',
                'description_template': '{price_html}'
            },
            'orders': {
                'icon': 'fas fa-receipt',
                'color': '#ffc107',
                'title_template': 'Pedido: {billing.first_name}',
                'description_template': 'Total: {total} - Estado: {status}'
            },
            'orders_today': {
                'icon': 'fas fa-calendar-day',
                'color': '#dc3545',
                'title_template': 'Pedido Hoy: {billing.first_name}',
                'description_template': '{line_items[0].name} - {total}'
            },
            'featured_products': {
                'icon': 'fas fa-star',
                'color': '#fd7e14',
                'title_template': 'Destacado: {name}',
                'description_template': '{price_html}'
            },
            'low_stock': {
                'icon': 'fas fa-exclamation-triangle',
                'color': '#dc3545',
                'title_template': 'Stock Bajo: {name}',
                'description_template': 'Quedan: {stock_quantity}'
            }
        }
        
        return display_configs.get(wc_type, display_configs['products'])

    def __repr__(self):
        return f'<ApiIntegration {self.name} - {self.api_type}>'

class ApiData(db.Model):
    """Datos obtenidos de las APIs que se muestran como imágenes en el calendario"""
    __tablename__ = 'api_data'
    
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('api_integrations.id'), nullable=False)
    date_for = db.Column(db.Date, nullable=False)  # Fecha para la que aplica el dato
    title = db.Column(db.String(200), nullable=False)  # Título a mostrar
    description = db.Column(db.Text, nullable=True)  # Descripción
    image_url = db.Column(db.String(500), nullable=True)  # URL de imagen externa
    icon = db.Column(db.String(50), nullable=True)  # Icono FontAwesome o emoji
    color = db.Column(db.String(7), default='#007bff')  # Color hex
    data_json = db.Column(db.Text, nullable=True)  # Datos originales en JSON
    is_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con la integración
    integration = db.relationship('ApiIntegration', backref='data_entries')
    
    def __repr__(self):
        return f'<ApiData {self.title} - {self.date_for}>'

class CalendarNote(db.Model):
    """Notas del calendario"""
    __tablename__ = 'calendar_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    date_for = db.Column(db.Date, nullable=False)  # Fecha de la nota
    title = db.Column(db.String(200), nullable=False)  # Título de la nota
    content = db.Column(db.Text, nullable=True)  # Contenido de la nota
    color = db.Column(db.String(7), default='#ffc107')  # Color hex
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent
    is_private = db.Column(db.Boolean, default=False)  # Solo visible para el creador
    is_reminder = db.Column(db.Boolean, default=False)  # Es recordatorio
    reminder_time = db.Column(db.Time, nullable=True)  # Hora del recordatorio
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con el creador
    creator = db.relationship('User', backref='calendar_notes')
    
    def get_priority_display(self):
        priority_map = {
            'low': 'Baja',
            'normal': 'Normal', 
            'high': 'Alta',
            'urgent': 'Urgente'
        }
        return priority_map.get(self.priority, self.priority)
    
    def get_priority_color(self):
        color_map = {
            'low': '#6c757d',
            'normal': '#007bff',
            'high': '#fd7e14', 
            'urgent': '#dc3545'
        }
        return color_map.get(self.priority, '#007bff')
    
    def __repr__(self):
        return f'<CalendarNote {self.title} - {self.date_for}>'
