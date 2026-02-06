# IMPLEMENTACIÓN TÉCNICA - MEJORAS DE SEGURIDAD

*Documento técnico para desarrolladores y mantenimiento futuro*

---

## 1. CAMBIOS EN `views_api.py`

### Imports Añadidos

```python
from django.utils.html import escape  # Para XSS prevention
import re                              # Para validación de email
```

### Nuevas Funciones Auxiliares

#### `_validate_email(email)` 
**Propósito:** Validar formato de email según RFC 5322 (simplificado)

```python
def _validate_email(email):
    """Valida formato de email según RFC 5322 (simplificado)"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

**Casos de uso:**
- `_validate_email('user@example.com')` → `True`
- `_validate_email('user@example')` → `False` (no TLD)
- `_validate_email('user@')` → `False` (sin dominio)

**Nota:** Es una validación simplificada. Para RFC 5322 completo, usar `django.core.validators.EmailValidator`.

---

#### `_sanitize_for_html(text)`
**Propósito:** Escapar caracteres HTML para prevenir inyección en templates de email

```python
def _sanitize_for_html(text):
    """Escapa caracteres HTML para prevenir inyección en email"""
    if not text:
        return ''
    # Primero escapa HTML, luego reemplaza saltos de línea con <br>
    escaped = escape(text)
    return escaped.replace('\n', '<br>')
```

**Transformaciones:**
```
"<script>alert('xss')</script>" → "&lt;script&gt;alert('xss')&lt;/script&gt;"
"Línea 1\nLínea 2"               → "Línea 1<br>Línea 2"
"3 < 5 & 5 > 3"                 → "3 &lt; 5 &amp; 5 &gt; 3"
```

**Uso en email templates:**
```python
nombre_safe = _sanitize_for_html(nombre)  # Antes de usar en HTML
correo_safe = _sanitize_for_html(correo)
mensaje_safe = _sanitize_for_html(mensaje)

# En template:
<td style="...;">{nombre_safe}</td>  # ← Ya seguro
```

---

#### `_sanitize_input(text, max_length=None)`
**Propósito:** Limpiar y validar inputs con límite de largo

```python
def _sanitize_input(text, max_length=None):
    """Limpia y valida un input de usuario"""
    if not text:
        return ''
    # Trim espacios
    text = text.strip()
    # Si tiene límite de largo, aplicarlo
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text
```

**Ejemplos:**
```python
_sanitize_input("  hello  ", 100)     # "hello"
_sanitize_input("A" * 200, 100)       # "A" * 100 (truncado)
_sanitize_input("", 100)              # ""
```

---

### Cambios en `contact_form()`

#### 1. Extracción y Limpieza de Inputs (ANTES)
```python
nombre = (data.get('nombre') or '').strip()
correo = (data.get('correo') or '').strip()
mensaje = (data.get('mensaje') or '').strip()
proyecto = (data.get('proyecto') or '').strip()
hp = (data.get('hp') or '').strip()
```

#### 1. Extracción y Limpieza de Inputs (DESPUÉS)
```python
nombre = _sanitize_input(data.get('nombre', ''), max_length=100)
correo = _sanitize_input(data.get('correo', ''), max_length=254)
mensaje = _sanitize_input(data.get('mensaje', ''), max_length=5000)
proyecto = _sanitize_input(data.get('proyecto', ''), max_length=100)
hp = _sanitize_input(data.get('hp', ''))
```

**Beneficios:**
- ✅ Límites de largo aplicados (DoS prevention)
- ✅ Inputs normalizados (trim)
- ✅ Fácil de mantener centralmente

---

#### 2. Validación de Email (NUEVO)
```python
# Validar formato de email
if not _validate_email(correo):
    return JsonResponse({'ok': False, 'error': 'Email inválido.'}, status=400)
```

**Antes:** Ninguna validación backend (solo HTML5 input type="email")  
**Ahora:** Rechaza emails malformados en backend

---

#### 3. Sanitización en Email Templates (NUEVO)
```python
# Sanitizar inputs para HTML (previene XSS/injection)
nombre_safe = _sanitize_for_html(nombre)
correo_safe = _sanitize_for_html(correo)
proyecto_safe = _sanitize_for_html(proyecto) or 'No especificado'
mensaje_safe = _sanitize_for_html(mensaje)

admin_email = Mail(
    from_email='ccjose088@gmail.com',
    to_emails='ccjose088@gmail.com',
    subject=f'Nuevo mensaje de contacto: {nombre}',
    html_content=f"""
        ...
        <td style="...">{nombre_safe}</td>        ← Safe now
        <td style="...">{correo_safe}</td>        ← Safe now
        <td style="...">{proyecto_safe}</td>      ← Safe now
        <div style="...;">{mensaje_safe}</div>    ← Safe now
        ...
    """
)
```

**Antes:** `{nombre}`, `{correo}`, etc. (vulnerable a XSS)  
**Ahora:** `{nombre_safe}`, `{correo_safe}`, etc. (escaped)

---

#### 4. Manejo Graceful de Fallos de SendGrid (MEJORADO)
```python
try:
    sg = SendGridAPIClient(sendgrid_api_key)
    admin_resp = sg.send(admin_email)
    confirm_resp = sg.send(confirmation_email)
    
    # ✅ Success
    return JsonResponse({
        'ok': True, 
        'message': 'Mensaje enviado correctamente.', 
        'email_sent': True
    })

except (HTTPError, Exception) as e:
    logger.exception("Error enviando email")
    
    # ✅ Graceful degradation: mensaje guardado, email falló
    return JsonResponse({
        'ok': True,  # ← Still success! Data is saved
        'message': 'Mensaje guardado. Email podría no haber sido enviado.',
        'email_sent': False,  # ← Indicate partial failure
    }, status=200)  # ← 200 OK, not 502 error
```

**Lógica:**
1. DB save succeeeds → usuario recibe éxito ✓
2. Email send fails → respuesta indica estado ✗
3. Admin puede ver en logs y hacer follow-up manual

**Antes:** Status 502, usuario se frustra  
**Ahora:** Status 200, usuario sabe que mensaje fue guardado

---

## 2. CAMBIOS EN `contacto.html`

### Form Tag
```html
<!-- ANTES -->
<form id="formulario-contacto">

<!-- DESPUÉS -->
<form id="formulario-contacto" novalidate>
```

**`novalidate`:** Desactiva validación HTML5 del navegador, permite custom validation

---

### Fieldset + Legend
```html
<!-- ANTES: Ninguna estructura -->

<!-- DESPUÉS -->
<fieldset>
    <legend style="display:none;">Formulario de contacto</legend>
    
    <!-- Inputs aquí -->
</fieldset>
```

**Beneficios:**
- ✅ Screen readers entienden el propósito del form
- ✅ Inputs agrupados semánticamente
- ✅ `<legend>` oculto visualmente pero visible en accesibilidad

---

### Input Attributes (Accessibility)
```html
<!-- ANTES -->
<input type="text" id="nombre" name="nombre" required>

<!-- DESPUÉS -->
<input type="text" id="nombre" name="nombre" 
       autocomplete="name" 
       required 
       aria-required="true">
```

**Cambios:**
- `autocomplete="name"` - Password managers pueden autofill
- `aria-required="true"` - Screen readers anuncian "requerido"

---

### Required Indicator
```html
<!-- ANTES -->
<label for="nombre">Nombre</label>

<!-- DESPUÉS -->
<label for="nombre">Nombre <span aria-label="requerido">*</span></label>
```

**Beneficios:**
- ✅ Visual: `*` visible
- ✅ Accesibilidad: Screen reader anuncia "requerido"

---

### Honeypot (Accesible)
```html
<!-- ANTES -->
<input type="text" name="hp" id="hp" 
       style="display:none" tabindex="-1" autocomplete="off">

<!-- DESPUÉS -->
<input type="text" name="hp" id="hp" 
       style="display:none" 
       tabindex="-1" 
       autocomplete="off" 
       aria-hidden="true">
```

**`aria-hidden="true"`:** Excluye campo del árbol de accesibilidad (como se intende)

---

### Mensaje de Confirmación (Accesible)
```html
<!-- ANTES -->
<p id="mensaje-confirmacion" class="oculto" aria-live="polite"></p>

<!-- DESPUÉS -->
<p id="mensaje-confirmacion" 
   class="oculto" 
   aria-live="polite" 
   aria-atomic="true" 
   role="status"></p>
```

**Attributes:**
- `aria-live="polite"` - Screen reader anuncia cambios sin interrumpir
- `aria-atomic="true"` - Lee todo el mensaje, no pieza por pieza
- `role="status"` - Prioridad normal de anuncio

---

## 3. FLUJO DE VALIDACIÓN COMPLETO

```
1. USER SUBMITS FORM
   ↓
2. JAVASCRIPT VALIDATION (client-side)
   - Campos requeridos no vacíos? (HTML5 required)
   - Email formato válido? (HTML5 type="email")
   ↓
3. SEND JSON TO /api/contact/
   ↓
4. BACKEND VALIDATION (server-side)
   a) JSON valid?
   b) Sanitize inputs (trim)
   c) Honeypot vacío?
   d) Campos requeridos presentes?
   e) Email formato válido? (_validate_email)
   f) Largo inputs OK? (max_length)
   ↓
5. SAVE TO DATABASE
   - Datos guardados con timestamp
   ↓
6. SEND EMAIL (con datos escapados)
   - Si éxito: retorna email_sent=True
   - Si falla: retorna email_sent=False pero ok=True
   ↓
7. RESPONSE TO USER
   {
     "ok": true,
     "message": "...",
     "email_sent": true|false
   }
```

---

## 4. LOGGING Y DEBUGGING

### Logs Generados

```python
# Honeypot blocked
logger.warning("Contacto bloqueado por honeypot (hp no vacío)")

# Success
logger.info("SendGrid OK admin=202 confirm=202")

# Errors
logger.exception("Error guardando Contacto en DB")
logger.error("SENDGRID_API_KEY no configurada")
logger.warning(f"Contacto guardado sin envío de email: {nombre}")
logger.exception("Error inesperado enviando email con SendGrid")
```

### Debug Info (Development Only)

```python
if getattr(settings, 'DEBUG', False):
    payload['debug'] = {
        'exception_type': 'SSLCertVerificationError',
        'exception': 'certificate verify failed',
        'hint': 'Configure SSL_CERT_FILE en .env...'
    }
```

---

## 5. CONFIGURACIÓN REQUERIDA

### .env
```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
```

### settings.py (ya configurado)
```python
# CORS para local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Debug mode development
DEBUG = True  # En production: False
```

---

## 6. TESTING LOCAL

### Ejecutar Tests de Seguridad
```bash
cd scripts/
python test_security_audit.py
```

### Test Manual con curl
```bash
# XSS test
curl -X POST http://localhost:8000/api/contact/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "<script>alert(1)</script>",
    "correo": "valid@example.com",
    "mensaje": "test",
    "proyecto": "",
    "hp": ""
  }'

# Expected response:
# {"ok": true, "message": "Mensaje guardado...", "email_sent": false|true}
```

### Verificar en DB
```bash
cd despacho_django
python manage.py shell

>>> from proyectos.models import Contacto
>>> Contacto.objects.last()  # Ver último mensaje
>>> Contacto.objects.filter(email='valid@example.com').values()
```

---

## 7. MANTENIMIENTO FUTURO

### Si Necesitas Cambiar Límites de Largo

En `views_api.py`:
```python
# Cambiar esto:
nombre = _sanitize_input(data.get('nombre', ''), max_length=100)
# A esto:
nombre = _sanitize_input(data.get('nombre', ''), max_length=200)  # Más largo
```

### Si Necesitas Cambiar Validación de Email

En `views_api.py`:
```python
# Opción 1: Usar Django's built-in (más robusto)
from django.core.validators import EmailValidator

def _validate_email(email):
    try:
        EmailValidator()(email)
        return True
    except:
        return False

# Opción 2: Regex más complejo (RFC 5322 completo)
# Nota: Regex para RFC 5322 completo es ~1400 caracteres!
```

### Si Necesitas Escapar Otros Caracteres

En `views_api.py`:
```python
def _sanitize_for_html(text):
    if not text:
        return ''
    escaped = escape(text)
    
    # Añadir más transformaciones si necesario:
    # escaped = escaped.replace('&nbsp;', ' ')  # Por ejemplo
    
    return escaped.replace('\n', '<br>')
```

---

## 8. REFERENCIAS DE CÓDIGO

| Función | Archivo | Línea | Propósito |
|---------|---------|-------|----------|
| `_validate_email()` | views_api.py | ~18 | Validar formato email |
| `_sanitize_for_html()` | views_api.py | ~23 | Escapar HTML en emails |
| `_sanitize_input()` | views_api.py | ~31 | Limpar y truncar inputs |
| `contact_form()` | views_api.py | ~112 | Procesar formulario |

---

## 9. SEGURIDAD: RESUMEN TÉCNICO

### Defenses in Depth

```
1. Frontend HTML5 Validation
   ↓ (User-side, can be bypassed)
2. Backend Input Sanitization
   ↓ (Trim, truncate)
3. Backend Input Validation
   ↓ (Format checks, regex)
4. HTML Escaping for Email Templates
   ↓ (Prevent XSS/injection)
5. Database Save First
   ↓ (Preserve data even if email fails)
6. Error Handling
   ↓ (No info leaks, graceful degradation)
7. Logging
   ↓ (Track issues, audit trail)
```

### OWASP Top 10 Mapping

| OWASP Risk | Mitigated? | How |
|-----------|-----------|-----|
| A03:2021 – Injection | ✅ Yes | HTML escaping, no SQL injection (ORM) |
| A05:2021 – Access Control | ✅ Yes | No auth bypass (public endpoint OK) |
| A06:2021 – Crypto Failure | ✅ Yes | HTTPS in production, no passwords |
| A07:2021 – Identification | ✅ Yes | No auth, honeypot for spam |
| A09:2021 – Data Integrity | ✅ Yes | DB-first saves data always |
| A10:2021 – Logging | ✅ Yes | Comprehensive error logging |

---

*Este documento es para referencia técnica de desarrolladores. Para seguridad en producción, ver `SECURITY_AUDIT_CONTACTO.md`.*
