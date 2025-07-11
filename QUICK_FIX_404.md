# 🔧 Solución Rápida - Error 404

## ❌ Problema
Error 404 al acceder a: `http://localhost:5000/calendar/api-integrations/1/test`

## ✅ Solución
La URL correcta es: `http://localhost:5000/api-integrations/1/test` (sin `/calendar/`)

## 🚀 Pasos para Probar

### 1. Iniciar el Servidor
```bash
# Opción A: Ejecutar script batch
start_flask_server.bat

# Opción B: Comando manual
.\venv_house\Scripts\python.exe run.py
```

### 2. Verificar URLs Correctas
- ✅ **Calendario:** http://localhost:5000/
- ✅ **Test API:** http://localhost:5000/api-integrations/1/test
- ✅ **Config WooCommerce:** http://localhost:5000/woocommerce/config
- ✅ **Webhook:** http://localhost:5000/webhook/woocommerce

### 3. Probar Funcionalidad WooCommerce

#### Opción A: Interfaz Web
1. Ir a: http://localhost:5000/woocommerce/config
2. Hacer clic en **"Probar Webhook"**
3. Verificar que se crea una nota en el calendario

#### Opción B: Demo Script
```bash
python demo_woocommerce_webhook.py
```

#### Opción C: API Manual
```bash
curl -X POST http://localhost:5000/api/woocommerce/test-webhook \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{}'
```

### 4. Verificar Resultado
1. Ir al calendario: http://localhost:5000/
2. Buscar nota con icono 🛒
3. La nota debe aparecer en la fecha actual

## 🔍 URLs de las APIs Implementadas

### APIs de Notas del Calendario
- `POST /api/notes` - Crear nota completa
- `PUT /api/notes/<id>` - Actualizar nota
- `DELETE /api/notes/<id>` - Eliminar nota
- `GET /api/notes/<fecha>` - Obtener notas de una fecha
- `POST /api/calendar/<fecha>/quick-note` - Crear nota rápida
- `GET /api/calendar/<fecha>/has-notes` - Verificar si hay notas

### APIs de WooCommerce
- `POST /webhook/woocommerce` - Webhook para recibir pedidos
- `POST /api/woocommerce/test-webhook` - Probar webhook
- `POST /api/woocommerce/manual-sync` - Sincronización manual

### APIs de Integraciones (Existentes)
- `GET /api-integrations` - Listar integraciones
- `GET /api-integrations/<id>/test` - Probar integración
- `GET /api-integrations/<id>/sync` - Sincronizar integración

## 🐛 Troubleshooting

### Error: "Module not found"
**Solución:** Usar el entorno virtual correcto
```bash
.\venv_house\Scripts\python.exe run.py
```

### Error: "Database not found"
**Solución:** Crear base de datos
```bash
.\venv_house\Scripts\python.exe -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

### Error: "Permission denied"
**Solución:** Crear usuario admin
```bash
.\venv_house\Scripts\python.exe scripts/init_users.py
```

## ✅ Estado de la Implementación

**🎉 COMPLETADO:**
- ✅ Webhook WooCommerce funcionando
- ✅ APIs de notas del calendario
- ✅ Interfaz web para configuración
- ✅ Modal para añadir notas en calendario
- ✅ Mapeo automático de estados → colores
- ✅ Documentación completa

**🎯 LISTO PARA USAR:**
- Los pedidos de WooCommerce se añaden automáticamente al calendario
- Solo hay que configurar el webhook en WooCommerce con la URL correcta
- La interfaz web permite probar toda la funcionalidad

## 📞 Siguiente Paso
1. **Iniciar servidor:** `start_flask_server.bat`
2. **Probar webhook:** http://localhost:5000/woocommerce/config
3. **Ver resultado:** http://localhost:5000/ (calendario principal)

¡La implementación está completa y funcionando! 🚀
