# Fix: UNIQUE Constraint Error en users.email

## Problema
Error al actualizar usuarios: `sqlite3.IntegrityError: UNIQUE constraint failed: users.email`

Este error ocurría cuando se intentaba actualizar un usuario y el campo email se enviaba como cadena vacía (''), pero ya existía otro usuario con email vacío, violando la restricción UNIQUE.

## Causa
1. El modelo User tiene `email = db.Column(db.String(120), unique=True, nullable=True)`
2. Algunos usuarios tenían email = NULL o email = ''
3. Cuando se actualizaba un usuario sin proporcionar email, se enviaba '' (cadena vacía)
4. Si ya existía otro usuario con email = '', SQLite lanzaba el error UNIQUE constraint

## Solución Implementada

### 1. Actualización de la lógica de gestión de emails
**Archivo:** `app/blueprints/users/routes.py`

```python
# Email con validación para evitar constraint UNIQUE
email = request.form.get('email', '').strip()
if not email:  # Si está vacío, generar email único
    # Generar email único para evitar constraint UNIQUE
    email = f"user{user.id}@floristeria.local"
    user.email = email
else:
    # Verificar que el email no esté siendo usado por otro usuario
    existing_user = User.query.filter(User.email == email, User.id != user.id).first()
    if existing_user:
        flash(f'El email {email} ya está siendo usado por otro usuario', 'error')
        return render_template('edit_user.html', user=user)
    user.email = email
```

### 2. Validación JavaScript en el frontend
**Archivo:** `app/templates/edit_user.html`

```javascript
// Validación del formulario antes de envío
document.querySelector('form').addEventListener('submit', function(e) {
    const emailField = document.getElementById('email');
    if (!emailField.value.trim()) {
        // Si el email está vacío, generar uno automático
        const userId = '{{ user.id }}';
        emailField.value = `user${userId}@floristeria.local`;
    }
});
```

### 3. Corrección de datos existentes
Se actualizaron todos los usuarios con emails problemáticos:

```python
# admin: NULL -> admin@floristeria.local
# test_user: '' -> user3@floristeria.local
```

### 4. Scripts de verificación
- `scripts/fix_email_constraint.py` - Detecta y corrige emails duplicados
- `scripts/verify_email_integrity.py` - Verifica integridad después del fix
- `scripts/quick_check.py` - Verificación rápida de usuarios

## Estado Final
Todos los usuarios ahora tienen emails únicos y válidos:

```
ID: 1, Username: admin, Email: admin@floristeria.local
ID: 2, Username: usuario, Email: usuario@floristeria.com
ID: 3, Username: test_user, Email: user3@floristeria.local
ID: 4, Username: superadmin, Email: emergency@floristeria.local
```

## Prevención Futura
1. **Validación en el backend**: Siempre generar email único si está vacío
2. **Validación en el frontend**: JavaScript previene envío de emails vacíos
3. **Scripts de diagnóstico**: Para detectar problemas futuros
4. **Registro mejorado**: Auto-genera emails únicos en el registro de usuarios

## Archivos Modificados
- `app/blueprints/users/routes.py` - Lógica de actualización de emails
- `app/templates/edit_user.html` - Validación JavaScript
- `scripts/CREDENCIALES.py` - Actualizado con email del admin
- `scripts/verify_email_integrity.py` - Script de verificación (nuevo)
- `scripts/quick_check.py` - Verificación rápida (nuevo)

## Testing
✅ Todos los usuarios pueden ser actualizados sin error de constraint
✅ Emails únicos garantizados
✅ Interfaz web funcional
✅ Scripts de diagnóstico funcionando
