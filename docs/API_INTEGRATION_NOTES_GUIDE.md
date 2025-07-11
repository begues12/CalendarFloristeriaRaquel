# API Integration & Notes System - User Guide

## Overview

The Calendar system now includes powerful features for integrating external APIs and managing notes. This guide covers how to use these features effectively.

## API Integration System

### What is API Integration?

The API Integration system allows you to fetch data from external APIs and display it directly in your calendar as if they were images or content. This is useful for:
- Weather data
- News feeds  
- Social media content
- IoT sensor data
- Any REST API that returns JSON data

### Setting Up API Integrations (Admin Only)

#### 1. Access API Management
- Go to Calendar view
- Click the Admin Toolbar (visible only to admins/super admins)
- Select "Gestionar APIs"

#### 2. Create New API Integration
- Click "Nueva Integración"
- Fill in the required fields:
  - **Name**: Descriptive name for your API
  - **API URL**: The endpoint URL
  - **API Key**: Authentication key (if required)
  - **Headers**: Additional HTTP headers (JSON format)
  - **Mapping Configuration**: How to extract data from API response

#### 3. Mapping Configuration

The mapping configuration tells the system how to extract useful information from the API response. Use JSON path notation:

```json
{
  "display_field": "weather.description",
  "image_field": "weather.icon_url", 
  "description_field": "weather.temp"
}
```

**Common Mapping Fields:**
- `display_field`: Main text to show
- `image_field`: URL to an image
- `description_field`: Additional description
- `link_field`: URL for clickable content

#### 4. Example Configurations

**Weather API:**
```json
{
  "display_field": "current.condition.text",
  "image_field": "current.condition.icon",
  "description_field": "current.temp_c"
}
```

**News API:**
```json
{
  "display_field": "articles[0].title",
  "image_field": "articles[0].urlToImage",
  "description_field": "articles[0].description",
  "link_field": "articles[0].url"
}
```

### Managing API Data

#### Automatic Synchronization
- APIs sync automatically based on their configured frequency
- Manual sync available from calendar view or day view

#### Manual Sync
- Calendar view: Click "Sincronizar APIs" in admin toolbar
- Day view: Click "Sincronizar APIs" in quick actions

#### Viewing API Data
- API data appears in calendar grid with special indicators
- Day view shows detailed API data cards
- Click on API data to see raw response (admin only)

## Notes System

### What are Calendar Notes?

Calendar Notes allow users to create, edit, and manage text notes associated with specific dates. Notes can be:
- Public (visible to all users)
- Private (only visible to creator and admins)
- Rich text with line breaks
- Timestamped with creation/modification info

### Creating Notes

#### From Calendar View
1. Click on any day to go to day view
2. Click "Agregar Nota" in quick actions
3. Fill in the note form:
   - **Title**: Brief description
   - **Content**: Full note content (supports line breaks)
   - **Date & Time**: When the note applies
   - **Visibility**: Public or Private

#### From Day View
1. Navigate to specific day
2. Use "Agregar Nota" button in quick actions
3. Date will be pre-filled with current day

#### Direct Access
- Go to "Gestionar Notas" from admin toolbar
- Click "Nueva Nota"

### Managing Notes

#### Viewing Notes
- **Calendar View**: Notes are indicated with special icons
- **Day View**: Full note cards with all details
- **Notes Management**: Complete list with filters

#### Editing Notes
- Click edit icon on any note you created
- Admins can edit all notes
- Changes are timestamped automatically

#### Deleting Notes
- Click delete icon with confirmation
- Only creators and admins can delete notes
- Deletion is permanent

### Note Visibility Rules

**Public Notes:**
- Visible to all authenticated users
- Shown in calendar indicators
- Displayed in day view for everyone

**Private Notes:**
- Only visible to creator
- Admins and super admins can see all notes
- Not shown in public calendar indicators

## Integration with Calendar

### Calendar Grid Display

**API Data Indicators:**
- Blue cloud icon indicates API data available
- Hover for quick preview
- Click day for full details

**Notes Indicators:**
- Yellow note icon for notes
- Different icon for public vs private notes
- Number badge shows count if multiple

### Day View Features

**API Data Section:**
- Cards showing mapped data from each API
- Images display inline
- Links are clickable
- Raw data accessible to admins

**Notes Section:**
- Chronological list of notes
- Color-coded by visibility
- Edit/delete actions for authorized users
- Rich text display with line breaks

**Quick Actions:**
- Add note for current day
- Upload photos
- Sync API data
- All context-aware based on date

## Advanced Features

### API Error Handling
- Failed API calls are logged
- Users see friendly error messages
- Retry mechanisms built-in
- Admin notification for persistent failures

### Data Retention
- API data older than 90 days auto-purged
- Notes are retained indefinitely
- Admins can configure retention policies

### Performance Optimization
- API responses are cached
- Background sync for better UX
- Pagination for large note lists
- Optimized database queries

## Security Considerations

### API Keys
- Stored encrypted in database
- Never exposed in browser
- Rotatable without data loss
- Audit trail for changes

### User Permissions
- Role-based access control
- Privilege system integration
- Notes visibility controls
- Admin oversight capabilities

### Data Privacy
- API data processing follows GDPR
- User notes are private by default
- Audit logs for sensitive operations
- Secure data transmission

## Troubleshooting

### Common API Issues

**"API not responding"**
- Check URL validity
- Verify API key
- Test endpoint manually
- Check network connectivity

**"No data in mapping"**
- Verify JSON path syntax
- Check API response structure
- Use browser developer tools
- Test with simple mappings first

**"Rate limit exceeded"**
- Reduce sync frequency
- Contact API provider
- Implement backoff strategy
- Consider premium API tier

### Common Notes Issues

**"Cannot create note"**
- Check user permissions
- Verify date format
- Ensure title is provided
- Check for special characters

**"Note not visible"**
- Check visibility settings
- Verify user permissions
- Clear browser cache
- Check date filters

## Best Practices

### API Configuration
1. Test APIs with small datasets first
2. Use descriptive names for integrations
3. Keep mapping simple initially
4. Monitor API usage and costs
5. Regular health checks

### Notes Management
1. Use clear, descriptive titles
2. Keep content concise but informative
3. Use public notes for team information
4. Regular cleanup of outdated notes
5. Consistent formatting for better readability

### Performance Tips
1. Limit number of active APIs
2. Optimize mapping configurations
3. Use appropriate sync frequencies
4. Monitor system resources
5. Regular database maintenance

## Support and Updates

For technical support or feature requests:
- Check the troubleshooting section first
- Contact system administrator
- Refer to technical documentation
- Submit feature requests through proper channels

The system is regularly updated with new features and security improvements. Check the changelog for recent updates and new capabilities.
