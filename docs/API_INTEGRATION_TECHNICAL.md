# API Integration & Notes System - Technical Documentation

## Architecture Overview

The API Integration and Notes system extends the existing calendar application with two major components:

1. **API Integration Service**: Fetches and maps external API data
2. **Calendar Notes**: User-generated content management system

## Database Schema

### ApiIntegration Table
```sql
CREATE TABLE api_integration (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    api_url TEXT NOT NULL,
    api_key VARCHAR(255),
    headers TEXT,  -- JSON string
    mapping_config TEXT,  -- JSON string  
    sync_frequency INTEGER DEFAULT 3600,  -- seconds
    is_active BOOLEAN DEFAULT TRUE,
    last_sync DATETIME,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES user (id)
);
```

### ApiData Table
```sql
CREATE TABLE api_data (
    id INTEGER PRIMARY KEY,
    integration_id INTEGER NOT NULL,
    data_date DATETIME NOT NULL,
    raw_data TEXT,  -- JSON string
    display_content TEXT,
    description TEXT,
    image_url TEXT,
    link_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (integration_id) REFERENCES api_integration (id)
);
```

### CalendarNote Table
```sql
CREATE TABLE calendar_note (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    note_date DATETIME NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES user (id)
);
```

## Core Components

### 1. Models (`app/models/user.py`)

#### ApiIntegration Model
- Stores API configuration and credentials
- Handles JSON mapping configuration
- Provides helper methods for data extraction

**Key Methods:**
- `get_mapped_value(data, field_key)`: Extract values using JSON path
- `get_headers_dict()`: Parse headers JSON to dict
- `get_mapping_config_dict()`: Parse mapping config JSON

#### ApiData Model
- Stores fetched API data with processed display content
- Links to parent ApiIntegration
- Optimized for calendar display

#### CalendarNote Model
- User-generated notes with rich metadata
- Visibility controls (public/private)
- Relationships to User model

### 2. API Integration Service (`app/utils/api_service.py`)

The `ApiIntegrationService` class handles all API operations:

```python
class ApiIntegrationService:
    def fetch_data(self, integration: ApiIntegration) -> Tuple[bool, Optional[dict]]
    def process_api_data(self, integration: ApiIntegration, raw_data: dict, target_date: datetime) -> ApiData
    def sync_data_for_date(self, target_date: datetime) -> bool
    def sync_all_active_apis(self) -> dict
```

**Key Features:**
- Robust error handling with retries
- JSON path mapping for flexible data extraction
- Rate limiting and timeout protection
- Comprehensive logging

### 3. Routes and Views (`app/blueprints/calendar/routes.py`)

#### API Management Routes
- `/calendar/api-integrations/` - List all integrations
- `/calendar/api-integrations/create` - Create new integration
- `/calendar/api-integrations/<id>/edit` - Edit integration
- `/calendar/api-integrations/<id>/delete` - Delete integration
- `/calendar/api-integrations/sync` - Manual sync trigger

#### Notes Management Routes
- `/calendar/notes/` - List all notes
- `/calendar/notes/create` - Create new note
- `/calendar/notes/<id>/edit` - Edit note
- `/calendar/notes/<id>/delete` - Delete note

#### Enhanced Calendar Routes
- `/calendar/` - Main calendar with API data and notes
- `/calendar/day/<date>` - Day view with integrated data

## Integration Points

### Calendar Display Logic

The main calendar view (`/calendar/`) now fetches:
1. Photos (existing functionality)
2. API data for each day
3. Calendar notes for each day

```python
# In calendar index route
for day in calendar_days:
    # Existing photo logic
    photos = Photo.query.filter_by(date_taken=date_obj).all()
    
    # New API data logic
    api_data = ApiData.query.filter(
        db.func.date(ApiData.data_date) == date_obj
    ).all()
    
    # New notes logic  
    notes = CalendarNote.query.filter(
        db.func.date(CalendarNote.note_date) == date_obj
    ).all()
```

### Template Integration

#### Enhanced `calendar.html`
- Admin toolbar for API/notes management
- Visual indicators for API data and notes
- Dropdown menus for quick actions per day

#### Enhanced `day.html`
- API data cards with rich display
- Notes section with CRUD operations
- Quick actions panel for context-aware operations

#### New Template Files
- `api_integrations.html` - API management interface
- `create_api_integration.html` - API creation form
- `edit_api_integration.html` - API editing form
- `calendar_notes.html` - Notes management interface
- `create_note.html` - Note creation form
- `edit_note.html` - Note editing form

## Data Flow

### API Data Synchronization
1. **Trigger**: Manual sync or scheduled job
2. **Fetch**: `ApiIntegrationService.fetch_data()`
3. **Process**: Extract mapped values from response
4. **Store**: Create `ApiData` record with processed content
5. **Display**: Show in calendar grid and day view

```python
# Sync flow example
service = ApiIntegrationService()
integrations = ApiIntegration.query.filter_by(is_active=True).all()

for integration in integrations:
    success, raw_data = service.fetch_data(integration)
    if success:
        api_data = service.process_api_data(integration, raw_data, datetime.now())
        db.session.add(api_data)

db.session.commit()
```

### Notes Management Flow
1. **Create**: User submits note form
2. **Validate**: Check permissions and data integrity
3. **Store**: Save to `CalendarNote` table
4. **Display**: Show in calendar with visibility rules
5. **Update**: Track modification timestamps

## Security Implementation

### API Key Protection
- API keys encrypted in database using Flask app secret
- Never exposed in frontend JavaScript
- Masked in admin interfaces ("api_key": "****...1234")

### Access Control
- Role-based permissions for API management
- Note visibility controls (public/private)
- Audit logging for sensitive operations

### Input Validation
- JSON schema validation for mapping configs
- URL validation for API endpoints
- XSS protection for note content

## Performance Optimizations

### Database Indexing
```sql
-- Indexes for optimal query performance
CREATE INDEX idx_api_data_date ON api_data(data_date);
CREATE INDEX idx_api_data_integration ON api_data(integration_id);
CREATE INDEX idx_calendar_note_date ON calendar_note(note_date);
CREATE INDEX idx_calendar_note_public ON calendar_note(is_public);
```

### Caching Strategy
- API responses cached for configurable duration
- Database query optimization with selective loading
- Frontend caching for static API data

### Background Processing
- Async API synchronization to prevent UI blocking
- Queue system for batch operations
- Rate limiting to respect API provider limits

## Configuration

### Environment Variables
```env
# API Integration Settings
API_CACHE_DURATION=3600  # seconds
API_REQUEST_TIMEOUT=30   # seconds
API_MAX_RETRIES=3
API_RETRY_DELAY=5        # seconds

# Notes Settings  
NOTES_MAX_LENGTH=10000   # characters
NOTES_AUTO_CLEANUP=90    # days

# Background Jobs
ENABLE_AUTO_SYNC=true
SYNC_INTERVAL=3600       # seconds
```

### Application Configuration
```python
# In config/settings.py
class Config:
    # API Integration
    API_CACHE_DURATION = int(os.environ.get('API_CACHE_DURATION', 3600))
    API_REQUEST_TIMEOUT = int(os.environ.get('API_REQUEST_TIMEOUT', 30))
    API_MAX_RETRIES = int(os.environ.get('API_MAX_RETRIES', 3))
    
    # Notes
    NOTES_MAX_LENGTH = int(os.environ.get('NOTES_MAX_LENGTH', 10000))
    NOTES_AUTO_CLEANUP = int(os.environ.get('NOTES_AUTO_CLEANUP', 90))
```

## Testing Strategy

### Unit Tests (`tests/test_api_integration.py`)
- Model functionality testing
- API service testing with mocked responses
- Data mapping and validation testing

### Integration Tests
- Full workflow testing (create integration → sync → display)
- Database transaction testing
- Permission and access control testing

### Performance Tests
- Load testing for multiple API integrations
- Stress testing for large note datasets
- Memory usage monitoring

## Deployment Considerations

### Database Migrations
```python
# Migration for new tables
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('api_integration', ...)
    op.create_table('api_data', ...)
    op.create_table('calendar_note', ...)
    
    # Create indexes
    op.create_index('idx_api_data_date', 'api_data', ['data_date'])
    # ... more indexes
```

### Background Jobs Setup
```python
# Using APScheduler for background sync
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=sync_all_apis,
    trigger="interval",
    seconds=app.config.get('SYNC_INTERVAL', 3600)
)
scheduler.start()
```

### Monitoring and Logging
- API request/response logging
- Performance metrics collection  
- Error rate monitoring
- User activity tracking

## Error Handling

### API Integration Errors
```python
try:
    response = requests.get(url, timeout=self.timeout)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"API request failed: {str(e)}")
    return False, None
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {str(e)}")
    return False, None
```

### User-Facing Error Messages
- Friendly error messages for API failures
- Validation error feedback for forms
- Graceful degradation when APIs are unavailable

## Future Enhancements

### Planned Features
1. **Webhook Support**: Real-time data updates
2. **API Rate Limiting**: Per-integration limits
3. **Data Transformation**: Custom JavaScript transforms
4. **Note Templates**: Predefined note formats
5. **Bulk Operations**: Mass note creation/editing

### Scalability Improvements
1. **Redis Caching**: Distributed cache for API data
2. **Message Queues**: Async processing with Celery
3. **Database Sharding**: Horizontal scaling for large datasets
4. **CDN Integration**: Static asset optimization

## API Reference

### REST Endpoints for External Integration

#### Get Calendar Data
```http
GET /api/calendar/data?date=2025-07-11
Authorization: Bearer <token>

Response:
{
  "photos": [...],
  "api_data": [...],
  "notes": [...]
}
```

#### Trigger API Sync
```http
POST /api/calendar/sync
Authorization: Bearer <token>
Content-Type: application/json

{
  "integration_ids": [1, 2, 3],
  "date_range": {
    "start": "2025-07-01",
    "end": "2025-07-31"
  }
}
```

### Webhook Endpoints (Future)
```http
POST /webhooks/api-data/<integration_id>
Content-Type: application/json

{
  "timestamp": "2025-07-11T12:00:00Z",
  "data": { ... }
}
```

## Maintenance and Operations

### Regular Maintenance Tasks
1. **Data Cleanup**: Remove old API data based on retention policy
2. **Index Optimization**: Rebuild indexes for performance
3. **Log Rotation**: Archive and cleanup application logs
4. **Cache Invalidation**: Clear stale cached data

### Monitoring Checklist
- [ ] API response times and success rates
- [ ] Database query performance
- [ ] User activity patterns
- [ ] Error rates and types
- [ ] Storage usage growth

### Backup Strategy
- Database backups include all new tables
- API configuration export/import capability
- Notes backup with user data anonymization option

This technical documentation should be updated as the system evolves and new features are added.
