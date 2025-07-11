# 🛒 Integración WooCommerce → Calendario

## Descripción
Esta funcionalidad permite que los pedidos de WooCommerce se añadan automáticamente como notas en el calendario de la floristería. Cada pedido se convierte en una nota del calendario con información completa del cliente y productos.

## 🚀 Funcionalidades Principales

### ✅ Webhook Automático
- **URL del webhook:** `/webhook/woocommerce`
- **Eventos soportados:** `order.created`, `order.updated`, `order.status_changed`
- **Procesamiento automático** de pedidos nuevos y actualizaciones
- **Mapeo inteligente** de estados → colores y prioridades

### ✅ Página de Configuración
- **URL:** `/woocommerce/config`
- **Prueba de webhook** con datos de ejemplo
- **Sincronización manual** por rango de fechas
- **Visualización de mapeo** de estados y colores

### ✅ API de Gestión
- **Test endpoint:** `/api/woocommerce/test-webhook`
- **Sincronización manual:** `/api/woocommerce/manual-sync`
- **Integración completa** con sistema de notas existente

## 🔧 Configuración en WooCommerce

### 1. Crear Webhook en WooCommerce
1. Ir a **WooCommerce → Configuración → API → Webhooks**
2. Hacer clic en **Añadir webhook**
3. Configurar:
   - **Nombre:** Floristería Raquel - Pedidos
   - **Estado:** Activo
   - **Tema:** Order created, Order updated
   - **URL de entrega:** `https://tu-dominio.com/webhook/woocommerce`
   - **Secreto:** (opcional, para mayor seguridad)

### 2. Eventos Recomendados
```
order.created    → Se crea un nuevo pedido
order.updated    → Se actualiza un pedido existente
order.status_changed → Cambia el estado del pedido
```

## 📊 Mapeo de Estados

### Estados → Colores del Calendario
| Estado WooCommerce | Color | Descripción |
|-------------------|-------|-------------|
| `pending` | 🟡 Amarillo (#ffc107) | Pedido pendiente de pago |
| `processing` | 🔵 Azul (#007bff) | Pedido en proceso |
| `on-hold` | 🟠 Naranja (#fd7e14) | Pedido en espera |
| `completed` | 🟢 Verde (#28a745) | Pedido completado |
| `cancelled` | 🔴 Rojo (#dc3545) | Pedido cancelado |
| `refunded` | ⚫ Gris (#6c757d) | Pedido reembolsado |
| `failed` | 🔴 Rojo (#dc3545) | Pago fallido |

### Estados → Prioridades
| Estados | Prioridad | Motivo |
|---------|-----------|--------|
| `processing`, `on-hold` | **Alta** | Requieren atención inmediata |
| `pending`, `completed` | **Normal** | Flujo normal de trabajo |
| `cancelled`, `refunded` | **Baja** | No requieren acción |
| `failed` | **Normal** | Pueden necesitar seguimiento |

## 📝 Formato de Notas Generadas

### Título
```
🛒 Pedido #12345 - Juan Pérez
```

### Contenido
```
Estado: Procesando
Total: 89.50 EUR
Cliente: Juan Pérez
Email: juan.perez@email.com
Teléfono: +34 666 777 888

Productos:
• Ramo de rosas rojas (x1)
• Centro de mesa primaveral (x2)
```

## 🔗 Endpoints de la API

### 1. Webhook Principal
```
POST /webhook/woocommerce
Content-Type: application/json
```

**Datos de entrada (automático desde WooCommerce):**
```json
{
  "id": 12345,
  "status": "processing",
  "total": "89.50",
  "currency": "EUR",
  "date_created": "2025-07-11T10:30:00",
  "billing": {
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan.perez@email.com",
    "phone": "+34 666 777 888"
  },
  "line_items": [
    {
      "name": "Ramo de rosas rojas",
      "quantity": 1
    }
  ]
}
```

### 2. Test del Webhook
```
POST /api/woocommerce/test-webhook
Authorization: Required (login)
```

### 3. Sincronización Manual
```
POST /api/woocommerce/manual-sync
Content-Type: application/json
Authorization: Required (login)

{
  "start_date": "2025-07-01",
  "end_date": "2025-07-11"
}
```

## 🎯 Casos de Uso

### Caso 1: Nuevo Pedido
1. **Cliente realiza pedido** en la tienda online
2. **WooCommerce envía webhook** a la floristería
3. **Sistema crea nota automáticamente** en el calendario
4. **Floristería ve el pedido** en la fecha correspondiente

### Caso 2: Cambio de Estado
1. **Estado cambia** de "pendiente" a "procesando"
2. **WooCommerce envía webhook** de actualización
3. **Sistema actualiza la nota existente** con nuevo color/prioridad
4. **Floristería ve el cambio** reflejado inmediatamente

### Caso 3: Múltiples Pedidos
1. **Varios pedidos el mismo día** se muestran como múltiples notas
2. **Cada nota mantiene** su color según estado
3. **Indicador visual** muestra cantidad total de notas
4. **Fácil gestión** desde el calendario

## 🛠️ Instalación y Pruebas

### 1. Verificar Funcionamiento
```bash
# Ejecutar demo de prueba
python demo_woocommerce_webhook.py
```

### 2. Acceder a Configuración
1. Ir a `http://localhost:5000/woocommerce/config`
2. Hacer clic en **"Probar Webhook"**
3. Verificar que se crea la nota en el calendario

### 3. Configurar URL Real
1. En producción, usar dominio real: `https://tu-floristeria.com/webhook/woocommerce`
2. Verificar que el servidor puede recibir webhooks
3. Configurar HTTPS para mayor seguridad

## 🔐 Seguridad

### Validaciones Implementadas
- ✅ **Verificación de JSON** válido
- ✅ **Validación de campos** requeridos
- ✅ **Manejo de errores** robusto
- ✅ **Logs de seguridad** para auditoría

### Recomendaciones Adicionales
- 🔒 **Usar HTTPS** en producción
- 🔑 **Configurar secreto** en WooCommerce webhook
- 🛡️ **Limitar acceso** por IP si es posible
- 📊 **Monitorear logs** regularmente

## 🔧 Solución de Problemas

### Error 404 en `/calendar/api-integrations/1/test`
**Problema:** URL incorrecta
**Solución:** Usar `/api-integrations/1/test` (sin `/calendar/`)

### Webhook no recibe datos
**Posibles causas:**
1. URL incorrecta en WooCommerce
2. Servidor no accesible desde internet
3. Firewall bloqueando conexiones

**Solución:**
1. Verificar URL: `https://tu-dominio.com/webhook/woocommerce`
2. Usar herramientas como ngrok para pruebas locales
3. Verificar logs del servidor

### Notas no aparecen en calendario
**Posibles causas:**
1. Usuario sin permisos `can_manage_notes`
2. Error en formato de fecha
3. Nota marcada como privada

**Solución:**
1. Verificar permisos de usuario
2. Revisar logs de la aplicación
3. Usar endpoint de test para diagnosticar

## 📈 Extensiones Futuras

### Posibles Mejoras
- 🔔 **Notificaciones push** para pedidos urgentes
- 📧 **Emails automáticos** de confirmación
- 📊 **Dashboard de estadísticas** de pedidos
- 🔄 **Sincronización bidireccional** (calendario → WooCommerce)
- 📱 **App móvil** para gestión en tiempo real

### Integraciones Adicionales
- 💳 **Pasarelas de pago** (Stripe, PayPal)
- 🚚 **Sistemas de envío** (Correos, MRW)
- 📞 **CRM** (HubSpot, Salesforce)
- 📱 **WhatsApp Business** API

---

## 🎉 Beneficios

### Para la Floristería
- ⏰ **Gestión automática** de pedidos
- 📅 **Visión unificada** en el calendario
- 🎨 **Clasificación visual** por estado
- 📊 **Mejor organización** del trabajo diario

### Para los Clientes
- ✅ **Confirmación automática** de pedidos
- 🔄 **Seguimiento en tiempo real** del estado
- 📞 **Comunicación directa** con datos actualizados
- 💐 **Mejor experiencia** de compra

---

**¡La integración está lista para usar!** 🚀

Para más detalles técnicos, revisar:
- Código fuente: `app/blueprints/calendar/routes.py`
- Plantilla: `templates/woocommerce_config.html`
- Demo: `demo_woocommerce_webhook.py`
