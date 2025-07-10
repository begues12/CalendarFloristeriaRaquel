"""
Rutas de gestión de documentos: subir, ver, descargar y eliminar documentos personales
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import UserDocument, db

documents_bp = Blueprint('documents', __name__)

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

@documents_bp.route('/upload_document', methods=['GET', 'POST'])
@login_required
@requires_privilege('can_upload_documents')
def upload_document():
    """Subir documentos personales"""
    from flask import current_app
    
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
        
        if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            # Crear carpeta para documentos del usuario
            user_folder = os.path.join(current_app.config['DOCUMENTS_FOLDER'], str(current_user.id))
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
            return redirect(url_for('documents.my_documents'))
        else:
            flash('Tipo de archivo no permitido', 'error')
    
    return render_template('upload_document.html')

@documents_bp.route('/my_documents')
@login_required
@requires_privilege('can_view_own_documents')
def my_documents():
    """Ver documentos personales"""
    documents = UserDocument.query.filter_by(user_id=current_user.id).order_by(
        UserDocument.uploaded_at.desc()
    ).all()
    
    return render_template('my_documents.html', documents=documents)

@documents_bp.route('/download_document/<int:doc_id>')
@login_required
def download_document(doc_id):
    """Descargar documento"""
    document = UserDocument.query.get_or_404(doc_id)
    
    # Verificar privilegios: el usuario puede descargar sus propios documentos o tener privilegio de ver todos o ser admin
    if not (document.user_id == current_user.id or 
            current_user.has_privilege('can_view_all_documents') or 
            current_user.is_admin or 
            current_user.is_super_admin):
        abort(403)
    
    try:
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.filename
        )
    except FileNotFoundError:
        flash('El archivo no existe en el servidor', 'error')
        return redirect(url_for('documents.my_documents'))

@documents_bp.route('/delete_document/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    """Eliminar documento"""
    document = UserDocument.query.get_or_404(doc_id)
    
    # Verificar privilegios: solo el propietario puede eliminar su documento o ser admin
    if not (document.user_id == current_user.id or 
            current_user.is_admin or 
            current_user.is_super_admin):
        abort(403)
    
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
    
    return redirect(url_for('documents.my_documents'))
