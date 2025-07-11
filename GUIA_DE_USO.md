# GUÍA DE USO: Sistema de Calendario con Integración WooCommerce

## 🚀 Inicio Rápido

### 1. Ejecutar la Aplicación
```bash
python app.py
```
La aplicación estará disponible en: http://localhost:5000

### 2. Acceso al Sistema
- **Login**: Use sus credenciales de administrador
- **Calendario**: Página principal en http://localhost:5000
- **Configuración WooCommerce**: http://localhost:5000/woocommerce/config

## 📅 Funcionalidades del Calendario

### Ver Notas en el Calendario
1. En la vista del calendario, las notas aparecen como:
   - 📝 Icono amarillo con número de notas
   - Indicadores de color según la prioridad/tipo
   - Los pedidos de WooCommerce se muestran con icono 🛒

### Crear Notas Manualmente
1. Haga clic en el menú de opciones (⋮) de cualquier día
2. Seleccione "Agregar nota"
3. Complete el formulario y guarde

## 🛒 Integración WooCommerce

### Configuración Inicial
1. Vaya a: http://localhost:5000/woocommerce/config
2. Copie la URL del webhook: `http://localhost:5000/webhook/woocommerce`
3. Configure en WooCommerce:
   - **URL del Webhook**: La URL copiada
   - **Eventos**: order.created, order.updated, order.status_changed
   - **Formato**: JSON

### Sincronización Manual
En la página de configuración WooCommerce:

1. **Sincronización Inmediata**:
   - Haga clic en "Sincronizar Ahora"
   - Los pedidos simulados se añadirán al calendario

2. **Prueba de Webhook**:
   - Haga clic en "Probar Webhook"
   - Se creará un pedido de prueba en el calendario

### Tipos de Pedidos y Colores
- **Pendiente** 🟡: Amarillo (#ffc107)
- **Procesando** 🔵: Azul (#007bff)
- **En espera** 🟠: Naranja (#fd7e14)
- **Completado** 🟢: Verde (#28a745)
- **Cancelado** 🔴: Rojo (#dc3545)
- **Reembolsado** ⚫: Gris (#6c757d)

## 📋 Información de Pedidos en el Calendario

Cada pedido de WooCommerce se muestra como una nota con:
- **Título**: 🛒 Pedido #[ID] - [Nombre Cliente]
- **Información**:
  - Estado del pedido
  - Total y moneda
  - Datos del cliente (nombre, email, teléfono)
  - Lista de productos (hasta 5, con "... y X más" si hay más)

## 🔄 API Endpoints Disponibles

### Notas del Calendario
- `GET /api/notes/date/{YYYY-MM-DD}` - Obtener notas de una fecha
- `POST /api/notes` - Crear nueva nota
- `PUT /api/notes/{id}` - Actualizar nota
- `DELETE /api/notes/{id}` - Eliminar nota

### WooCommerce
- `POST /webhook/woocommerce` - Webhook para recibir pedidos
- `POST /api/woocommerce/manual-sync` - Sincronización manual
- `POST /api/woocommerce/test-webhook` - Probar webhook

## 🧪 Scripts de Prueba

### Verificar Sistema
```bash
python verify_system.py
```
Verifica que todos los componentes estén instalados correctamente.

### Probar Funcionalidades
```bash
python test_woocommerce_sync.py
```
Prueba las funcionalidades de WooCommerce (requiere app ejecutándose).

## 📊 Dashboard de Administrador

Como administrador, puede:
1. **Ver todas las notas** (privadas y públicas)
2. **Gestionar integraciones de API**
3. **Acceder a configuración WooCommerce**
4. **Sincronizar datos manualmente**

## 🔧 Configuración Avanzada

### Variables de Entorno (opcional)
Cree un archivo `.env` con:
```
FLASK_ENV=development
SECRET_KEY=su_clave_secreta
DATABASE_URL=sqlite:///floristeria.db
```

### Base de Datos
- La base de datos se crea automáticamente
- Las migraciones se aplican al inicio
- Los datos se guardan en `instance/floristeria.db`

## ⚠️ Resolución de Problemas

### Error 404 en rutas
- Verifique que la aplicación esté ejecutándose
- Confirme que está usando el puerto correcto (5000)

### Notas no aparecen en calendario
- Verifique permisos de usuario
- Confirme que las fechas coinciden
- Revise logs de errores en la consola

### Webhook no funciona
- Verifique que WooCommerce pueda alcanzar su servidor
- Use ngrok para túneles en desarrollo
- Confirme el formato JSON de los datos

## 📞 Soporte

Para problemas adicionales:
1. Revise los logs de la consola
2. Verifique la documentación en los archivos `.md`
3. Use los scripts de prueba para diagnosticar problemas

---

✅ **El sistema está completamente funcional y listo para usar!**
