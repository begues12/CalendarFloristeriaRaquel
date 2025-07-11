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

#### 2. Quick WooCommerce Setup (Recommended)
- Click "Configurar WooCommerce" (green button)
- Enter your store details:
  - **Store URL**: Your WooCommerce site URL
  - **Consumer Key**: From WooCommerce → Settings → Advanced → REST API
  - **Consumer Secret**: From the same location
  - **Integration Type**: Choose what to display (Products, Orders, etc.)
- Click "Configurar WooCommerce" to auto-configure

#### 3. Manual API Integration
- Click "Otra API" for non-WooCommerce integrations
- Fill in the required fields:
  - **Name**: Descriptive name for your API
  - **API Type**: Select WooCommerce or other types
  - **API URL**: The endpoint URL
  - **Headers**: Authentication headers (JSON format)
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

**WooCommerce API (Products):**
```json
{
  "display_field": "name",
  "image_field": "images[0].src",
  "description_field": "price_html",
  "link_field": "permalink"
}
```

**WooCommerce API (Orders):**
```json
{
  "display_field": "billing.first_name",
  "description_field": "total",
  "status_field": "status",
  "date_field": "date_created"
}
```

#### 5. WooCommerce Integration Setup

**Step 1: Generate API Keys**
- Go to WooCommerce → Settings → Advanced → REST API
- Create new API key with Read/Write permissions
- Copy Consumer Key (ck_...) and Consumer Secret (cs_...)

**Step 2: Configure Headers**
For WooCommerce, use Basic Authentication:
```json
{
  "Authorization": "Basic [BASE64_ENCODED_CREDENTIALS]",
  "Content-Type": "application/json"
}
```

To generate the BASE64 credentials:
1. Combine: `ck_your_key:cs_your_secret`
2. Encode in Base64
3. Example: `ck_abc123:cs_def456` becomes `Y2tfYWJjMTIzOmNzX2RlZjQ1Ng==`

**Step 3: Common WooCommerce URLs**
- Products: `https://yourstore.com/wp-json/wc/v3/products`
- Orders: `https://yourstore.com/wp-json/wc/v3/orders`
- Customers: `https://yourstore.com/wp-json/wc/v3/customers`
- Categories: `https://yourstore.com/wp-json/wc/v3/products/categories`

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

### Common API Issues

**"Unexpected token '<'"** (HTML response instead of JSON)
- **Causa**: La URL no existe o requiere autenticación
- **Solución**: 
  1. Verifica que la URL esté correcta: `https://tu-tienda.com/wp-json/wc/v3/products`
  2. Asegúrate de que las credenciales estén en Base64
  3. Comprueba que WooCommerce REST API esté habilitado
  4. Prueba la URL en el navegador primero

**Ejemplo de URL correcta para WooCommerce:**
```
https://tu-tienda.com/wp-json/wc/v3/products?per_page=5
```

**Ejemplo de credenciales Base64:**
Para claves `ck_cda0de90e5b9c4ef0130a0aa98a92dc526425c78:cs_e35c00cd198e198148fbf2cdbe96d1044c5169fc`

1. Combinar con dos puntos: `ck_cda0de90e5b9c4ef0130a0aa98a92dc526425c78:cs_e35c00cd198e198148fbf2cdbe96d1044c5169fc`
2. Codificar en Base64: `Y2tfY2RhMGRlOTBlNWI5YzRlZjAxMzBhMGFhOThhOTJkYzUyNjQyNWM3ODpjc19lMzVjMDBjZDE5OGUxOTgxNDhmYjJjZGJlOTZkMTA0NGM1MTY5ZmM=`

**Headers completos para WooCommerce:**
```json
{
  "Authorization": "Basic Y2tfY2RhMGRlOTBlNWI5YzRlZjAxMzBhMGFhOThhOTJkYzUyNjQyNWM3ODpjc19lMzVjMDBjZDE5OGUxOTgxNDhmYjJjZGJlOTZkMTA0NGM1MTY5ZmM=",
  "Content-Type": "application/json",
  "User-Agent": "Floristeria-Calendar/1.0"
}
```

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
