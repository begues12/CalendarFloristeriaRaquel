"""
Pruebas para el sistema de integración de APIs
"""

import pytest
import json
from datetime import datetime, date
from unittest.mock import patch, Mock
from app import create_app, db
from app.models.user import User, ApiIntegration, ApiData, CalendarNote
from app.utils.api_service import ApiIntegrationService


@pytest.fixture
def app():
    """Crear instancia de la app para pruebas"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })
    
    with app.app_context():
        db.create_all()
        
        # Crear usuario de prueba
        user = User(
            username='test_user',
            email='test@example.com',
            is_admin=True
        )
        user.set_password('test_password')
        db.session.add(user)
        
        try:
            db.session.commit()
        except Exception:
            # Si el usuario ya existe, continúa
            db.session.rollback()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Cliente autenticado"""
    response = client.post('/auth/login', data={
        'username': 'test_user',
        'password': 'test_password'
    })
    return client


class TestApiIntegration:
    """Pruebas para ApiIntegration"""
    
    def test_create_api_integration(self, app):
        """Probar creación de integración de API"""
        with app.app_context():
            integration = ApiIntegration(
                name='Test Weather API',
                api_type='weather',
                url='https://api.weather.com/v1/current',
                api_key='test_key',
                mapping_config='{"display_field": "weather.description", "image_field": "weather.icon_url"}',
                is_active=True,
                created_by=1
            )
            db.session.add(integration)
            db.session.commit()
            
            assert integration.id is not None
            assert integration.name == 'Test Weather API'
            assert integration.is_active is True
    
    def test_api_integration_mapping(self, app):
        """Probar mapeo de configuración"""
        with app.app_context():
            integration = ApiIntegration(
                name='Test API',
                api_type='custom',
                url='https://api.test.com',
                mapping_config='{"display_field": "data.value", "description_field": "data.description"}',
                created_by=1
            )
            
            # Probar método get_mapped_value
            test_data = {
                'data': {
                    'value': 'Test Value',
                    'description': 'Test Description'
                }
            }
            
            display_value = integration.get_mapped_value(test_data, 'display_field')
            description_value = integration.get_mapped_value(test_data, 'description_field')
            
            assert display_value == 'Test Value'
            assert description_value == 'Test Description'


class TestApiData:
    """Pruebas para ApiData"""
    
    def test_create_api_data(self, app):
        """Probar creación de datos de API"""
        with app.app_context():
            # Crear integración primero
            integration = ApiIntegration(
                name='Test API',
                api_type='custom',
                url='https://api.test.com',
                mapping_config='{}',
                created_by=1
            )
            db.session.add(integration)
            db.session.commit()
            
            # Crear datos de API
            api_data = ApiData(
                integration_id=integration.id,
                date_for=datetime(2025, 7, 11, 12, 0, 0).date(),
                title='Test Data',
                description='Temperatura actual',
                data_json='{"temperature": 25, "humidity": 60}',
                color='#ff0000'
            )
            db.session.add(api_data)
            db.session.commit()
            
            assert api_data.id is not None
            assert api_data.display_content == '25°C'
            assert api_data.raw_data['temperature'] == 25


class TestCalendarNote:
    """Pruebas para CalendarNote"""
    
    def test_create_calendar_note(self, app):
        """Probar creación de nota de calendario"""
        with app.app_context():
            note = CalendarNote(
                title='Nota de prueba',
                content='Contenido de la nota de prueba',
                date_for=datetime(2025, 7, 11, 9, 0, 0).date(),
                created_by=1
            )
            db.session.add(note)
            db.session.commit()
            
            assert note.id is not None
            assert note.title == 'Nota de prueba'
            assert note.date_for == date(2025, 7, 11)
    
    def test_note_visibility(self, app):
        """Probar visibilidad de notas"""
        with app.app_context():
            # Nota pública
            public_note = CalendarNote(
                title='Nota pública',
                content='Contenido público',
                date_for=datetime.now().date(),
                is_private=False,
                created_by=1
            )
            
            # Nota privada
            private_note = CalendarNote(
                title='Nota privada',
                content='Contenido privado',
                date_for=datetime.now().date(),
                is_private=True,
                created_by=1
            )
            
            db.session.add_all([public_note, private_note])
            db.session.commit()
            
            assert public_note.is_private is False
            assert private_note.is_private is True


class TestApiIntegrationService:
    """Pruebas para ApiIntegrationService"""
    
    def test_fetch_data_success(self, app):
        """Probar fetch exitoso de datos"""
        with app.app_context():
            integration = ApiIntegration(
                name='Test API',
                api_type='custom',
                url='https://httpbin.org/json',
                mapping_config='{"display_field": "slideshow.title"}',
                created_by=1
            )
            db.session.add(integration)
            db.session.commit()
            
            service = ApiIntegrationService()
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'slideshow': {
                        'title': 'Sample Slide Show'
                    }
                }
                mock_get.return_value = mock_response
                
                success, data = service.fetch_api_data(integration)
                
                assert success is True
                assert data is not None
                assert 'slideshow' in data
    
    def test_fetch_data_failure(self, app):
        """Probar manejo de errores en fetch"""
        with app.app_context():
            integration = ApiIntegration(
                name='Test API',
                api_type='custom',
                url='https://invalid-url.com',
                mapping_config='{}',
                created_by=1
            )
            
            service = ApiIntegrationService()
            
            with patch('requests.get') as mock_get:
                mock_get.side_effect = Exception("Connection error")
                
                success, data = service.fetch_api_data(integration)
                
                assert success is False
                assert data is None
    
    def test_sync_data_for_date(self, app):
        """Probar sincronización de datos para una fecha"""
        with app.app_context():
            integration = ApiIntegration(
                name='Test API',
                api_type='custom',
                url='https://httpbin.org/json',
                mapping_config='{"display_field": "slideshow.title", "description_field": "slideshow.author"}',
                is_active=True,
                created_by=1
            )
            db.session.add(integration)
            db.session.commit()
            
            service = ApiIntegrationService()
            
            with patch.object(service, 'fetch_api_data') as mock_fetch:
                mock_fetch.return_value = (True, {
                    'slideshow': {
                        'title': 'Test Title',
                        'author': 'Test Author'
                    }
                })
                
                target_date = datetime(2025, 7, 11, 12, 0, 0)
                result = service.sync_data_for_date(target_date)
                
                assert result is True
                
                # Verificar que se creó el registro ApiData
                api_data = ApiData.query.filter_by(
                    integration_id=integration.id
                ).first()
                
                assert api_data is not None
                assert api_data.display_content == 'Test Title'
                assert api_data.description == 'Test Author'


class TestCalendarRoutes:
    """Pruebas para rutas del calendario con APIs y notas"""
    
    def test_calendar_view_with_api_data(self, auth_client, app):
        """Probar vista de calendario con datos de API"""
        with app.app_context():
            # Crear datos de prueba
            integration = ApiIntegration(
                name='Test API',
                api_type='custom',
                url='https://api.test.com',
                mapping_config='{}',
                created_by=1,
                is_active=True
            )
            db.session.add(integration)
            db.session.commit()
            
            api_data = ApiData(
                integration_id=integration.id,
                date_for=datetime.now().date(),
                title='Test Content',
                data_json='{"test": "data"}'
            )
            db.session.add(api_data)
            db.session.commit()
            
            response = auth_client.get('/calendar/')
            assert response.status_code == 200
            assert b'Test Content' in response.data or b'Datos de APIs' in response.data
    
    def test_day_view_with_notes(self, auth_client, app):
        """Probar vista de día con notas"""
        with app.app_context():
            # Crear nota de prueba
            note = CalendarNote(
                title='Nota de prueba',
                content='Contenido de prueba',
                date_for=datetime(2025, 7, 11).date(),
                created_by=1
            )
            db.session.add(note)
            db.session.commit()
            
            response = auth_client.get('/calendar/day/2025-07-11')
            assert response.status_code == 200
            assert b'Nota de prueba' in response.data or b'Notas del d' in response.data
    
    def test_create_note_route(self, auth_client, app):
        """Probar ruta de creación de nota"""
        response = auth_client.get('/calendar/notes/create')
        assert response.status_code == 200
        
        # Probar POST para crear nota
        response = auth_client.post('/calendar/notes/create', data={
            'title': 'Nueva nota',
            'content': 'Contenido de la nueva nota',
            'date_for': '2025-07-11',
            'note_time': '14:30',
            'is_private': False
        })
        
        # Debería redirigir después de crear
        assert response.status_code == 302
        
        # Verificar que se creó la nota
        with app.app_context():
            note = CalendarNote.query.filter_by(title='Nueva nota').first()
            assert note is not None
            assert note.content == 'Contenido de la nueva nota'


if __name__ == '__main__':
    pytest.main([__file__])
