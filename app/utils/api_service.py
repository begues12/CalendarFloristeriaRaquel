"""
Servicio para manejar integraciones con APIs externas
"""

import requests
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from app.models.user import db, ApiIntegration, ApiData
import logging

logger = logging.getLogger(__name__)

class ApiIntegrationService:
    """Servicio para manejar integraciones con APIs externas"""
    
    @staticmethod
    def test_api_connection(integration: ApiIntegration) -> Dict[str, Any]:
        """Prueba la conexión con una API"""
        try:
            headers = {}
            if integration.headers:
                headers = json.loads(integration.headers)
            
            if integration.api_key:
                # Agregar API key a headers o query params según el tipo
                if integration.api_type == 'weather':
                    headers['X-API-KEY'] = integration.api_key
                elif integration.api_type == 'events':
                    headers['Authorization'] = f'Bearer {integration.api_key}'
                else:
                    headers['API-KEY'] = integration.api_key
            
            response = requests.request(
                method=integration.request_method,
                url=integration.url,
                headers=headers,
                data=integration.request_body if integration.request_method != 'GET' else None,
                timeout=10
            )
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:500],
                'message': 'Conexión exitosa'
            }
            
        except requests.exceptions.Timeout:
            return {'success': False, 'message': 'Timeout - La API no respondió en 10 segundos'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'message': 'Error de conexión - No se pudo conectar a la API'}
        except requests.exceptions.HTTPError as e:
            return {'success': False, 'message': f'Error HTTP: {e}'}
        except json.JSONDecodeError:
            return {'success': False, 'message': 'Respuesta no es JSON válido'}
        except Exception as e:
            return {'success': False, 'message': f'Error inesperado: {str(e)}'}

    @staticmethod
    def fetch_api_data(integration: ApiIntegration) -> Dict[str, Any]:
        """Obtiene datos de una API y los mapea según la configuración"""
        try:
            # Preparar headers
            headers = {'User-Agent': 'Floristeria-Calendar/1.0'}
            if integration.headers:
                headers.update(json.loads(integration.headers))
            
            if integration.api_key:
                if integration.api_type == 'weather':
                    headers['X-API-KEY'] = integration.api_key
                elif integration.api_type == 'events':
                    headers['Authorization'] = f'Bearer {integration.api_key}'
                else:
                    headers['API-KEY'] = integration.api_key
            
            # Hacer la petición
            response = requests.request(
                method=integration.request_method,
                url=integration.url,
                headers=headers,
                data=integration.request_body if integration.request_method != 'GET' else None,
                timeout=30
            )
            response.raise_for_status()
            
            # Procesar respuesta
            data = response.json()
            mapping_config = json.loads(integration.mapping_config)
            
            # Mapear los datos
            mapped_entries = ApiIntegrationService._map_api_data(data, mapping_config, integration)
            
            # Guardar en base de datos
            saved_count = 0
            for entry_data in mapped_entries:
                # Verificar si ya existe una entrada para esta fecha
                existing = ApiData.query.filter_by(
                    integration_id=integration.id,
                    date_for=entry_data['date_for']
                ).first()
                
                if existing:
                    # Actualizar existente
                    existing.title = entry_data['title']
                    existing.description = entry_data.get('description')
                    existing.image_url = entry_data.get('image_url')
                    existing.icon = entry_data.get('icon')
                    existing.color = entry_data.get('color', '#007bff')
                    existing.data_json = json.dumps(entry_data.get('original_data', {}))
                    existing.updated_at = datetime.utcnow()
                else:
                    # Crear nuevo
                    api_data = ApiData(
                        integration_id=integration.id,
                        date_for=entry_data['date_for'],
                        title=entry_data['title'],
                        description=entry_data.get('description'),
                        image_url=entry_data.get('image_url'),
                        icon=entry_data.get('icon'),
                        color=entry_data.get('color', '#007bff'),
                        data_json=json.dumps(entry_data.get('original_data', {}))
                    )
                    db.session.add(api_data)
                
                saved_count += 1
            
            # Actualizar estado de la integración
            integration.last_sync = datetime.utcnow()
            integration.last_sync_status = 'success'
            integration.last_error = None
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Sincronización exitosa: {saved_count} entradas procesadas',
                'entries_count': saved_count
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f'Error de red: {str(e)}'
            integration.last_sync_status = 'error'
            integration.last_error = error_msg
            db.session.commit()
            return {'success': False, 'message': error_msg}
        
        except json.JSONDecodeError as e:
            error_msg = f'Error procesando JSON: {str(e)}'
            integration.last_sync_status = 'error'
            integration.last_error = error_msg
            db.session.commit()
            return {'success': False, 'message': error_msg}
        
        except Exception as e:
            error_msg = f'Error inesperado: {str(e)}'
            integration.last_sync_status = 'error'
            integration.last_error = error_msg
            db.session.commit()
            logger.exception(f"Error en fetch_api_data para {integration.name}")
            return {'success': False, 'message': error_msg}

    @staticmethod
    def _map_api_data(data: Dict, mapping_config: Dict, integration: ApiIntegration) -> List[Dict]:
        """Mapea los datos de la API según la configuración"""
        mapped_entries = []
        
        try:
            # Diferentes estrategias según el tipo de API
            if integration.api_type == 'weather':
                mapped_entries = ApiIntegrationService._map_weather_data(data, mapping_config)
            elif integration.api_type == 'events':
                mapped_entries = ApiIntegrationService._map_events_data(data, mapping_config)
            elif integration.api_type == 'tasks':
                mapped_entries = ApiIntegrationService._map_tasks_data(data, mapping_config)
            else:
                mapped_entries = ApiIntegrationService._map_custom_data(data, mapping_config)
            
        except Exception as e:
            logger.exception(f"Error mapeando datos para {integration.name}")
            # Fallback a mapeo genérico
            mapped_entries = ApiIntegrationService._map_custom_data(data, mapping_config)
        
        return mapped_entries

    @staticmethod
    def _map_weather_data(data: Dict, mapping_config: Dict) -> List[Dict]:
        """Mapea datos de clima"""
        entries = []
        
        # Configuración por defecto para APIs de clima
        default_mapping = {
            'data_path': 'forecast.forecastday',  # Ruta a los datos en el JSON
            'date_field': 'date',
            'title_field': 'day.condition.text',
            'icon_field': 'day.condition.icon',
            'temp_field': 'day.maxtemp_c'
        }
        
        config = {**default_mapping, **mapping_config}
        
        # Navegar a los datos usando la ruta
        forecast_data = ApiIntegrationService._get_nested_value(data, config['data_path'])
        
        if isinstance(forecast_data, list):
            for day_data in forecast_data[:7]:  # Solo 7 días
                try:
                    date_str = ApiIntegrationService._get_nested_value(day_data, config['date_field'])
                    condition = ApiIntegrationService._get_nested_value(day_data, config['title_field'])
                    temp = ApiIntegrationService._get_nested_value(day_data, config.get('temp_field', ''))
                    
                    date_for = datetime.strptime(date_str, '%Y-%m-%d').date()
                    title = f"{condition}"
                    if temp:
                        title += f" ({temp}°C)"
                    
                    entries.append({
                        'date_for': date_for,
                        'title': title,
                        'description': f"Clima: {condition}",
                        'icon': 'fas fa-cloud-sun',
                        'color': '#87CEEB',
                        'original_data': day_data
                    })
                except Exception as e:
                    logger.warning(f"Error procesando día de clima: {e}")
                    continue
        
        return entries

    @staticmethod
    def _map_events_data(data: Dict, mapping_config: Dict) -> List[Dict]:
        """Mapea datos de eventos"""
        entries = []
        
        default_mapping = {
            'data_path': 'events',
            'date_field': 'start.date',
            'title_field': 'summary',
            'description_field': 'description'
        }
        
        config = {**default_mapping, **mapping_config}
        events_data = ApiIntegrationService._get_nested_value(data, config['data_path'])
        
        if isinstance(events_data, list):
            for event in events_data:
                try:
                    date_str = ApiIntegrationService._get_nested_value(event, config['date_field'])
                    title = ApiIntegrationService._get_nested_value(event, config['title_field'])
                    description = ApiIntegrationService._get_nested_value(event, config.get('description_field', ''))
                    
                    # Parsear fecha (puede venir en diferentes formatos)
                    date_for = ApiIntegrationService._parse_date(date_str)
                    
                    entries.append({
                        'date_for': date_for,
                        'title': title or 'Evento',
                        'description': description,
                        'icon': 'fas fa-calendar-alt',
                        'color': '#28a745',
                        'original_data': event
                    })
                except Exception as e:
                    logger.warning(f"Error procesando evento: {e}")
                    continue
        
        return entries

    @staticmethod
    def _map_tasks_data(data: Dict, mapping_config: Dict) -> List[Dict]:
        """Mapea datos de tareas"""
        entries = []
        
        default_mapping = {
            'data_path': 'tasks',
            'date_field': 'due_date',
            'title_field': 'title',
            'status_field': 'status'
        }
        
        config = {**default_mapping, **mapping_config}
        tasks_data = ApiIntegrationService._get_nested_value(data, config['data_path'])
        
        if isinstance(tasks_data, list):
            for task in tasks_data:
                try:
                    date_str = ApiIntegrationService._get_nested_value(task, config['date_field'])
                    title = ApiIntegrationService._get_nested_value(task, config['title_field'])
                    status = ApiIntegrationService._get_nested_value(task, config.get('status_field', ''))
                    
                    date_for = ApiIntegrationService._parse_date(date_str)
                    
                    # Color según estado
                    color = '#ffc107'  # amarillo por defecto
                    if status in ['completed', 'done']:
                        color = '#28a745'  # verde
                    elif status in ['overdue', 'urgent']:
                        color = '#dc3545'  # rojo
                    
                    entries.append({
                        'date_for': date_for,
                        'title': title or 'Tarea',
                        'description': f"Estado: {status}" if status else None,
                        'icon': 'fas fa-tasks',
                        'color': color,
                        'original_data': task
                    })
                except Exception as e:
                    logger.warning(f"Error procesando tarea: {e}")
                    continue
        
        return entries

    @staticmethod
    def _map_custom_data(data: Dict, mapping_config: Dict) -> List[Dict]:
        """Mapeo genérico para APIs personalizadas"""
        entries = []
        
        # Configuración mínima requerida
        if 'data_path' not in mapping_config or 'date_field' not in mapping_config:
            return entries
        
        items_data = ApiIntegrationService._get_nested_value(data, mapping_config['data_path'])
        
        if isinstance(items_data, list):
            for item in items_data:
                try:
                    date_str = ApiIntegrationService._get_nested_value(item, mapping_config['date_field'])
                    title = ApiIntegrationService._get_nested_value(item, mapping_config.get('title_field', 'title'))
                    description = ApiIntegrationService._get_nested_value(item, mapping_config.get('description_field', ''))
                    
                    date_for = ApiIntegrationService._parse_date(date_str)
                    
                    entries.append({
                        'date_for': date_for,
                        'title': title or 'Elemento',
                        'description': description,
                        'icon': mapping_config.get('icon', 'fas fa-info-circle'),
                        'color': mapping_config.get('color', '#007bff'),
                        'original_data': item
                    })
                except Exception as e:
                    logger.warning(f"Error procesando elemento personalizado: {e}")
                    continue
        
        return entries

    @staticmethod
    def _get_nested_value(data: Dict, path: str) -> Any:
        """Obtiene un valor anidado usando notación de puntos"""
        if not path:
            return None
        
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    return None
            else:
                return None
        
        return value

    @staticmethod
    def _parse_date(date_str: str) -> date:
        """Parsea una fecha desde string con diferentes formatos"""
        if not date_str:
            return date.today()
        
        # Formatos comunes
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # Si no se puede parsear, usar fecha actual
        logger.warning(f"No se pudo parsear la fecha: {date_str}")
        return date.today()

    @staticmethod
    def sync_all_active_integrations():
        """Sincroniza todas las integraciones activas"""
        integrations = ApiIntegration.query.filter_by(is_active=True).all()
        results = []
        
        for integration in integrations:
            # Verificar si necesita sincronización
            if integration.last_sync:
                time_since_sync = datetime.utcnow() - integration.last_sync
                if time_since_sync.total_seconds() < (integration.refresh_interval * 60):
                    continue  # Aún no es tiempo de sincronizar
            
            result = ApiIntegrationService.fetch_api_data(integration)
            results.append({
                'integration': integration.name,
                'result': result
            })
        
        return results
