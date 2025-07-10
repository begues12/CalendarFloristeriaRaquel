"""
Funciones de utilidad para la aplicación
========================================

Funciones auxiliares reutilizables en toda la aplicación.
"""

from werkzeug.utils import secure_filename
from PIL import Image
import os


def allowed_file(filename, allowed_extensions):
    """Verifica si un archivo tiene una extensión permitida"""
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


def hours_to_hhmm(hours_decimal):
    """Convierte horas decimales a formato HH:MM"""
    if not hours_decimal:
        return "00:00"
    
    total_minutes = int(hours_decimal * 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def safe_filename(filename):
    """Genera un nombre de archivo seguro"""
    return secure_filename(filename)


def calculate_work_hours(start_time, end_time):
    """Calcula las horas trabajadas entre dos tiempos"""
    if not start_time or not end_time:
        return 0
    
    # Convertir a minutos desde medianoche
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    
    # Si el tiempo de fin es menor, asumimos que es al día siguiente
    if end_minutes < start_minutes:
        end_minutes += 24 * 60
    
    # Calcular diferencia en horas decimales
    diff_minutes = end_minutes - start_minutes
    return diff_minutes / 60.0


def format_file_size(size_bytes):
    """Convierte bytes a formato legible"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_image_file(file):
    """Valida que un archivo sea una imagen válida"""
    if not file or file.filename == '':
        return False, "No se seleccionó archivo"
    
    # Verificar extensión
    if not allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
        return False, "Tipo de archivo no permitido"
    
    # Verificar que sea una imagen válida
    try:
        img = Image.open(file.stream)
        img.verify()
        file.stream.seek(0)  # Reset stream position
        return True, "Válido"
    except Exception:
        return False, "El archivo no es una imagen válida"


def validate_document_file(file, allowed_extensions):
    """Valida que un archivo de documento sea válido"""
    if not file or file.filename == '':
        return False, "No se seleccionó archivo"
    
    # Verificar extensión
    if not allowed_file(file.filename, allowed_extensions):
        return False, f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(allowed_extensions)}"
    
    return True, "Válido"
