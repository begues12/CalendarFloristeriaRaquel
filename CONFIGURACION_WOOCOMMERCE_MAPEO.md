# Configuración de Mapeo WooCommerce - Floristería Raquel

## Resumen
Esta guía explica cómo configurar el mapeo de datos de WooCommerce para mostrar pedidos completos en el calendario, incluyendo dedicatorias, información de entrega y detalles del cliente.

## Estructura de Datos WooCommerce

### Información Básica del Pedido
```json
{
  "id": 2214,
  "status": "processing",
  "date_created": "2025-07-09T15:01:22",
  "total": "53.90",
  "currency": "EUR"
}
```

### Información del Cliente (Facturación)
```json
{
  "billing": {
    "first_name": "Carla",
    "last_name": "Torrandell Haro",
    "email": "carlatorrandell@gmail.com",
    "phone": "638989037",
    "address_1": "",
    "city": "",
    "postcode": "",
    "country": "ES"
  }
}
```

### Información de Entrega
```json
{
  "shipping": {
    "first_name": "Estefanía",
    "last_name": "Maldonado",
    "address_1": "Avinguda Molí, 37, 2n 2a",
    "city": "Viladecans",
    "postcode": "08840",
    "phone": "600814495",
    "country": "ES"
  }
}
```

### Productos y Dedicatorias
```json
{
  "line_items": [
    {
      "name": "Ramo de Rosas Rojas y Claveles Marsella",
      "quantity": 1,
      "total": "44.55",
      "meta_data": [
        {
          "display_key": "Dedicatoria",
          "display_value": "Estefanía, \r\n\r\nSentimos mucho que estéis pasando por este momento tan difícil. Te queremos y te pensamos todos los días..."
        },
        {
          "display_key": "Configura tu ramo",
          "display_value": "Medio"
        }
      ]
    }
  ]
}
```

### Fechas Especiales
```json
{
  "meta_data": [
    {
      "key": "ywcdd_order_delivery_date",
      "value": "2025-07-10"
    }
  ]
}
```

## Configuración de Mapeo Mejorada

### Mapeo Completo para API Integration
```json
{
  "data_path": "",
  "date_field": "date_created",
  "delivery_date_field": "meta_data[key=ywcdd_order_delivery_date].value",
  "title_template": "🌹 Pedido #{id} - {billing.first_name} {billing.last_name}",
  "customer_fields": {
    "name": "{billing.first_name} {billing.last_name}",
    "email": "billing.email",
    "phone": "billing.phone"
  },
  "delivery_fields": {
    "recipient": "{shipping.first_name} {shipping.last_name}",
    "address": "{shipping.address_1}, {shipping.city} {shipping.postcode}",
    "phone": "shipping.phone"
  },
  "order_fields": {
    "status": "status",
    "total": "total",
    "currency": "currency"
  },
  "product_fields": {
    "items_path": "line_items",
    "name": "name",
    "quantity": "quantity",
    "price": "total"
  },
  "dedication_fields": {
    "meta_path": "line_items[].meta_data[]",
    "dedication_key": "Dedicatoria",
    "value_field": "display_value"
  },
  "status_colors": {
    "pending": "#ffc107",
    "processing": "#007bff",
    "on-hold": "#fd7e14",
    "completed": "#28a745",
    "cancelled": "#dc3545",
    "refunded": "#6c757d",
    "failed": "#dc3545"
  },
  "icon": "fas fa-shopping-cart",
  "default_color": "#ffc107"
}
```

## Función de Procesamiento Mejorada

La función `process_woocommerce_order` ha sido actualizada para extraer y mostrar:

### 1. Información del Cliente
- Nombre completo (facturación)
- Email de contacto
- Teléfono

### 2. Información de Entrega
- Destinatario (si diferente del cliente)
- Dirección completa de entrega
- Teléfono de entrega
- Fecha de entrega preferida

### 3. Productos Detallados
- Nombre del producto
- Cantidad
- Precio individual
- Configuraciones especiales (tamaño del ramo, etc.)

### 4. Dedicatorias (¡CRÍTICO para floristerías!)
- Extracción automática de mensajes de dedicatoria
- Limpieza de formato (eliminar \r\n)
- Visualización clara con emoji 💌

### 5. Estados del Pedido
- Colores diferenciados por estado
- Prioridades automáticas
- Traducciones al español

## Formato de Visualización en el Calendario

### Título
```
🌹 Pedido #2214 - Carla Torrandell Haro → Estefanía Maldonado
```

### Contenido Estructurado
```
📋 ESTADO: Procesando
💰 TOTAL: 53.90 EUR

👤 CLIENTE:
   • Nombre: Carla Torrandell Haro
   • Email: carlatorrandell@gmail.com
   • Teléfono: 638989037

🚚 ENTREGA:
   • Destinatario: Estefanía Maldonado
   • Teléfono entrega: 600814495
   • Dirección: Avinguda Molí, 37, 2n 2a, Viladecans 08840
   • Fecha entrega: 2025-07-10

🌺 PRODUCTOS:
   • Ramo de Rosas Rojas y Claveles Marsella (x1) - 44.55€ (Configura tu ramo: Medio)

💌 DEDICATORIA:
   📝 Estefanía,
   📝 
   📝 Sentimos mucho que estéis pasando por este momento tan difícil.
   📝 Te queremos y te pensamos todos los días, nos gustaría poder
   📝 achucharte pero por ahora esperamos que con este ramo (con color
   📝 rosa of course) nos sientas un poquito más cerca.
   📝 
   📝 ¡Muchos abrazos hoy y siempre!
   📝 
   📝 Cris, Ona y Carla
```

## Configuración de Fechas

### Prioridad de Fechas para el Calendario
1. **Fecha de entrega** (`ywcdd_order_delivery_date`) - Prioridad ALTA
2. **Fecha del pedido** (`date_created`) - Si no hay fecha de entrega

Esto asegura que los pedidos aparezcan en el calendario en la fecha que realmente importa para la floristería: el día de entrega.

## Colores por Estado

| Estado | Color | Prioridad | Significado |
|--------|-------|-----------|-------------|
| `pending` | Amarillo (#ffc107) | Normal | Pendiente de pago |
| `processing` | Azul (#007bff) | Alta | En preparación |
| `on-hold` | Naranja (#fd7e14) | Alta | Esperando acción |
| `completed` | Verde (#28a745) | Normal | Entregado |
| `cancelled` | Rojo (#dc3545) | Baja | Cancelado |
| `refunded` | Gris (#6c757d) | Baja | Reembolsado |
| `failed` | Rojo (#dc3545) | Normal | Fallo en pago |

## Implementación

### 1. Webhook Automático
- URL: `/webhook/woocommerce`
- Recibe pedidos automáticamente
- Procesamiento inmediato

### 2. Sincronización Manual
- Ruta: `/api/woocommerce/manual-sync`
- Obtiene pedidos desde la API de WooCommerce
- Útil para pedidos históricos

### 3. Configuración de API Integration
- Utilizar plantilla "WooCommerce" en el editor
- Configurar URL de la API de WooCommerce
- Añadir credenciales de autenticación

## Ventajas de esta Configuración

1. **Información Completa**: Toda la información necesaria visible de un vistazo
2. **Dedicatorias Prominentes**: Los mensajes de dedicatoria son fáciles de leer
3. **Fechas Inteligentes**: Los pedidos aparecen en la fecha de entrega
4. **Colores Informativos**: Estado visual inmediato
5. **Detalles de Entrega**: Información completa para la logística
6. **Formato Limpio**: Estructura clara y profesional

Esta configuración está optimizada específicamente para el negocio de floristería, donde las dedicatorias, fechas de entrega y detalles del destinatario son información crítica.
