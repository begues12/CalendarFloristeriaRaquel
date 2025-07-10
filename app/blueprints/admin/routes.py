"""
Rutas administrativas: gestión de documentos de todos los usuarios
"""

from flask import render_template, request, redirect, url_for, flash, send_file, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
import subprocess
import sys
import json
from app.models import UserDocument, User, MaintenanceMode, UpdateLog, db
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

def require_super_admin(f):
    """Decorador para requerir permisos de super admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin:
            flash('No tienes permisos de super administrador para acceder a esta función', 'error')
            return redirect(url_for('calendar.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin_documents')
@login_required
@requires_privilege('can_view_all_documents')
def admin_documents():
    """Ver todos los documentos"""
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
    
    # Obtener usuarios activos para el filtro (excluir usuario de emergencia)
    users = User.query.filter(User.is_active == True, User.username != 'superadmin').all()
    
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

@bp.route('/admin_download_document/<int:doc_id>')
@login_required
def admin_download_document(doc_id):
    """Descargar cualquier documento - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para descargar este documento', 'error')
        return redirect(url_for('documents.my_documents'))
    
    document = UserDocument.query.get_or_404(doc_id)
    
    try:
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=f"{document.user.username}_{document.filename}"
        )
    except FileNotFoundError:
        flash('El archivo no existe en el servidor', 'error')
        return redirect(url_for('admin.admin_documents'))

@bp.route('/admin_delete_document/<int:doc_id>', methods=['POST'])
@login_required
def admin_delete_document(doc_id):
    """Eliminar cualquier documento - solo admin"""
    if not current_user.is_admin:
        flash('No tienes permisos para eliminar documentos', 'error')
        return redirect(url_for('documents.my_documents'))
    
    document = UserDocument.query.get_or_404(doc_id)
    
    try:
        # Eliminar archivo físico
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Eliminar registro de la base de datos
        filename = document.filename
        db.session.delete(document)
        db.session.commit()
        
        flash(f'Documento {filename} eliminado correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar el documento', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.admin_documents'))

# ===============================================
# RUTAS DE SUPER ADMINISTRADOR
# ===============================================

@bp.route('/super_admin_panel')
@login_required
@require_super_admin
def super_admin_panel():
    """Panel de control del super administrador"""
    maintenance = MaintenanceMode.get_current()
    recent_updates = UpdateLog.query.order_by(UpdateLog.started_at.desc()).limit(10).all()
    
    # Obtener información del git
    git_info = get_git_info()
    
    return render_template('super_admin_panel.html', 
                         maintenance=maintenance,
                         recent_updates=recent_updates,
                         git_info=git_info)

@bp.route('/toggle_maintenance', methods=['POST'])
@login_required
@require_super_admin
def toggle_maintenance():
    """Activar/desactivar modo mantenimiento"""
    maintenance = MaintenanceMode.get_current()
    
    if maintenance.is_active:
        maintenance.deactivate()
        flash('Modo mantenimiento desactivado', 'success')
    else:
        message = request.form.get('message', 'Sistema en mantenimiento. Volveremos pronto.')
        estimated_minutes = request.form.get('estimated_minutes', 30, type=int)
        maintenance.activate(current_user, message, estimated_minutes)
        flash('Modo mantenimiento activado', 'success')
    
    return redirect(url_for('admin.super_admin_panel'))

@bp.route('/update_system', methods=['POST'])
@login_required
@require_super_admin
def update_system():
    """Actualizar el sistema desde git y ejecutar migraciones"""
    update_log = None
    
    try:
        # Intentar crear log de actualización con múltiples intentos
        log_created = False
        for attempt in range(3):  # 3 intentos
            try:
                # Limpiar cualquier transacción pendiente
                try:
                    db.session.rollback()
                    db.session.close()  # Cerrar conexión para forzar nueva
                except:
                    pass
                
                # Esperar un momento entre intentos
                if attempt > 0:
                    import time
                    time.sleep(0.5)
                
                update_log = UpdateLog(
                    started_by=current_user.username,
                    git_commit_before=get_current_git_commit()
                )
                db.session.add(update_log)
                db.session.commit()
                log_created = True
                break
                
            except Exception as db_error:
                if "database is locked" in str(db_error).lower() or "readonly" in str(db_error).lower():
                    # Error de BD bloqueada/solo lectura, intentar de nuevo
                    try:
                        db.session.rollback()
                        db.session.close()
                    except:
                        pass
                    
                    if attempt == 2:  # Último intento
                        flash(f'Warning: Base de datos bloqueada, continuando sin log: {str(db_error)}', 'warning')
                        update_log = None
                        break
                else:
                    # Otro tipo de error, no reintentar
                    flash(f'Warning: No se pudo crear log de actualización: {str(db_error)}', 'warning')
                    update_log = None
                    try:
                        db.session.rollback()
                        db.session.close()
                    except:
                        pass
                    break
        
        # Activar modo mantenimiento automáticamente con reintentos
        maintenance_activated = False
        for attempt in range(3):
            try:
                maintenance = MaintenanceMode.get_current()
                if not maintenance.is_active:
                    maintenance.activate(current_user, 'Actualizando sistema...', 15)
                    maintenance_activated = True
                break
            except Exception as maintenance_error:
                if "database is locked" in str(maintenance_error).lower():
                    try:
                        db.session.rollback()
                        db.session.close()
                    except:
                        pass
                    
                    if attempt < 2:  # No es el último intento
                        import time
                        time.sleep(0.5)
                        continue
                
                flash(f'Warning: No se pudo activar modo mantenimiento: {str(maintenance_error)}', 'warning')
                break
        
        # Ejecutar actualización (esta es la parte crítica)
        result = perform_system_update(update_log)
        
        if result['success']:
            # Intentar actualizar el log si existe con reintentos
            if update_log:
                log_updated = False
                for attempt in range(3):
                    try:
                        # Asegurar que tenemos una sesión limpia
                        db.session.refresh(update_log)
                        update_log.mark_completed(result.get('commit_after'))
                        db.session.commit()
                        log_updated = True
                        break
                    except Exception as log_error:
                        if "database is locked" in str(log_error).lower():
                            try:
                                db.session.rollback()
                                db.session.close()
                            except:
                                pass
                            
                            if attempt < 2:  # No es el último intento
                                import time
                                time.sleep(0.5)
                                continue
                        
                        # Log falló pero actualización fue exitosa
                        try:
                            db.session.rollback()
                            db.session.close()
                        except:
                            pass
                        break
                
                if log_updated:
                    flash('Sistema actualizado correctamente', 'success')
                else:
                    flash('Sistema actualizado correctamente (Warning: Log no actualizado por BD bloqueada)', 'success')
            else:
                flash('Sistema actualizado correctamente (sin log)', 'success')
        else:
            # Intentar marcar log como fallido si existe con reintentos
            if update_log:
                for attempt in range(3):
                    try:
                        db.session.refresh(update_log)
                        update_log.mark_failed(result['error'])
                        db.session.commit()
                        break
                    except Exception:
                        if attempt < 2:  # No es el último intento
                            try:
                                db.session.rollback()
                                db.session.close()
                            except:
                                pass
                            import time
                            time.sleep(0.5)
                        else:
                            try:
                                db.session.rollback()
                                db.session.close()
                            except:
                                pass
            
            flash(f'Error en la actualización: {result["error"]}', 'error')
            
    except Exception as e:
        # Intentar marcar log como fallido si existe con reintentos
        if update_log:
            for attempt in range(3):
                try:
                    db.session.refresh(update_log)
                    update_log.mark_failed(f'Error inesperado: {str(e)}')
                    db.session.commit()
                    break
                except Exception:
                    if attempt < 2:  # No es el último intento
                        try:
                            db.session.rollback()
                            db.session.close()
                        except:
                            pass
                        import time
                        time.sleep(0.5)
                    else:
                        try:
                            db.session.rollback()
                            db.session.close()
                        except:
                            pass
        
        flash(f'Error inesperado durante la actualización: {str(e)}', 'error')
    
    finally:
        # Asegurar que desactivamos mantenimiento si fue activado
        try:
            maintenance = MaintenanceMode.get_current()
            if maintenance.is_active:
                maintenance.deactivate()
        except Exception:
            pass  # Ignorar errores al desactivar mantenimiento
    
    return redirect(url_for('admin.super_admin_panel'))

@bp.route('/check_updates')
@login_required
@require_super_admin
def check_updates():
    """Verificar si hay actualizaciones disponibles"""
    try:
        result = subprocess.run(['git', 'fetch'], capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            return jsonify({'error': 'Error al verificar actualizaciones'})
        
        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD..origin/main'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            updates_available = int(result.stdout.strip()) > 0
            return jsonify({'updates_available': updates_available, 'count': result.stdout.strip()})
        else:
            return jsonify({'error': 'Error al verificar actualizaciones'})
            
    except Exception as e:
        return jsonify({'error': str(e)})

@bp.route('/update_log/<int:log_id>')
@login_required
@require_super_admin
def view_update_log(log_id):
    """Ver detalles de un log de actualización"""
    update_log = UpdateLog.query.get_or_404(log_id)
    return render_template('update_log_detail.html', update_log=update_log)

# ===============================================
# FUNCIONES AUXILIARES
# ===============================================

def get_git_info():
    """Obtener información del repositorio git"""
    try:
        # Obtener commit actual
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        current_commit = result.stdout.strip()[:8] if result.returncode == 0 else 'Unknown'
        
        # Obtener branch actual
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        current_branch = result.stdout.strip() if result.returncode == 0 else 'Unknown'
        
        # Obtener último mensaje de commit
        result = subprocess.run(['git', 'log', '-1', '--pretty=%s'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        last_commit_message = result.stdout.strip() if result.returncode == 0 else 'Unknown'
        
        return {
            'current_commit': current_commit,
            'current_branch': current_branch,
            'last_commit_message': last_commit_message
        }
    except Exception:
        return {
            'current_commit': 'Error',
            'current_branch': 'Error', 
            'last_commit_message': 'Error al obtener información'
        }

def get_current_git_commit():
    """Obtener el hash del commit current"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def perform_system_update(update_log=None):
    """Realizar la actualización del sistema usando script dedicado"""
    try:
        # Usar el script dedicado para actualizaciones
        python_executable = sys.executable
        script_path = os.path.join(os.getcwd(), 'scripts', 'system_update.py')
        
        # Ejecutar script de actualización con salida JSON
        result = subprocess.run(
            [python_executable, script_path, '--json'],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=600  # 10 minutos timeout
        )
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'Script de actualización falló: {result.stderr}',
                'output': result.stdout
            }
        
        # Parsear resultado JSON
        try:
            script_result = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': 'Error parseando resultado del script de actualización',
                'output': result.stdout
            }
        
        # Preparar logs para la base de datos
        output_lines = []
        if 'logs' in script_result:
            output_lines.extend(script_result['logs'])
        
        # Agregar detalles de cada paso
        for step in ['git', 'dependencies', 'migrations']:
            if step in script_result and script_result[step]:
                step_result = script_result[step]
                output_lines.append(f"\n--- {step.upper()} ---")
                output_lines.append(f"Success: {step_result.get('success', False)}")
                output_lines.append(f"Message: {step_result.get('message', 'N/A')}")
                if step_result.get('output'):
                    output_lines.append(f"Output: {step_result['output']}")
        
        # Guardar output en el log solo si existe y está disponible
        if update_log:
            try:
                # Limpiar sesión antes de escribir
                try:
                    db.session.rollback()
                except:
                    pass
                
                # Refrescar el objeto para asegurar que esté en la sesión actual
                db.session.refresh(update_log)
                update_log.migration_output = '\n'.join(output_lines)
                db.session.commit()
            except Exception as db_error:
                # Si no se puede escribir en BD, continuar sin log
                print(f"Warning: No se pudo guardar log en BD: {str(db_error)}")
                try:
                    db.session.rollback()
                except:
                    pass
        
        # Verificar si la actualización fue exitosa
        overall_success = script_result.get('overall_success', False)
        
        if overall_success:
            # Desactivar modo mantenimiento solo si todo fue exitoso
            try:
                maintenance = MaintenanceMode.get_current()
                if maintenance.is_active:
                    maintenance.deactivate()
            except Exception as maintenance_error:
                print(f"Warning: No se pudo desactivar modo mantenimiento: {str(maintenance_error)}")
        
        return {
            'success': overall_success,
            'commit_after': get_current_git_commit(),
            'output': '\n'.join(output_lines),
            'error': None if overall_success else 'Falló al menos un paso de la actualización'
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False, 
            'error': 'Timeout en actualización del sistema (>10 minutos)'
        }
    except Exception as e:
        return {
            'success': False, 
            'error': f'Error inesperado en actualización: {str(e)}'
        }
