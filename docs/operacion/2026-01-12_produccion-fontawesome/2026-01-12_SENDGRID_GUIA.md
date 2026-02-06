# 📧 Guía de Configuración - SendGrid para Formulario de Contacto

## 🎯 Estado Actual

✅ **Django configurado** con vista para formulario de contacto
✅ **SendGrid instalado** (`pip install sendgrid`)
✅ **Vista contact_form** creada en `views_api.py`
✅ **URL `/contact/`** configurada
✅ **JavaScript** envía datos correctamente
✅ **Base de datos** guarda contactos

❌ **SendGrid API Key** necesita configuración
❌ **Dominio/Email** necesita verificación en SendGrid

## ❌ **PROBLEMA IDENTIFICADO: Email Remitente No Verificado**

### **¿Cuál es el problema?**

El error de conexión ocurre porque el código estaba usando `noreply@despachocarcon.com` como email remitente, pero este dominio **no está verificado** en SendGrid.

**SendGrid requiere que uses un email verificado como remitente.** Si no tienes un dominio personalizado verificado, debes usar un email que hayas verificado en tu cuenta de SendGrid.

### **¿Cómo solucionarlo?**

#### **Opción 1: Usar Email Verificado (Recomendado - YA IMPLEMENTADO)**
1. Ve a [SendGrid Dashboard](https://app.sendgrid.com/)
2. Ve a **Settings > Sender Authentication**
3. Verifica tu email: `ccjose088@gmail.com`
4. El código ya está configurado para usar este email como remitente

#### **Opción 2: Verificar un Dominio Personalizado**
Si quieres usar `noreply@despachocarcon.com`:
1. Ve a **Settings > Sender Authentication**
2. Elige **Domain Authentication**
3. Verifica que eres propietario del dominio `despachocarcon.com`
4. Una vez verificado, cambia el código para usar ese dominio

### **Configuración Actual (Ya Corregida)**

El código ahora usa:
- **From Email:** `ccjose088@gmail.com` ✅ (email verificado)
- **To Email:** `ccjose088@gmail.com` (tú) + email del usuario

### **Pasos para Solucionar:**

1. **Verifica tu email en SendGrid:**
   - Ve a https://app.sendgrid.com/
   - Settings > Sender Authentication
   - Verify a Single Sender
   - Usa: `ccjose088@gmail.com`

2. **Prueba la conexión:**
   ```bash
   python simple_test.py
   ```

3. **Inicia el servidor:**
   ```bash
   python manage.py runserver
   ```

4. **Prueba el formulario:**
   - Ve a http://127.0.0.1:8000/contacto/
   - Envía un mensaje

### **¿Por qué fallaba antes?**

- ❌ `noreply@despachocarcon.com` → dominio no verificado
- ✅ `ccjose088@gmail.com` → email verificado en SendGrid

---

## 📋 PASOS PARA CONFIGURAR SENDGRID

### 1. Crear Cuenta en SendGrid

1. Ve a [https://app.sendgrid.com/](https://app.sendgrid.com/)
2. Crea una cuenta gratuita
3. Verifica tu email principal

### 2. Verificar Dominio o Email Sencillo

**Opción A: Single Sender (Más fácil para empezar)**
1. Ve a **Settings > Sender Authentication**
2. Haz clic en **Verify a Single Sender**
3. Completa el formulario:
   - **From Email:** `noreply@despachocarcon.com` (o usa un subdominio)
   - **From Name:** `Despacho Carcon`
   - **Reply To:** `carcon.arquitectura1@gmail.com`
4. SendGrid te enviará un email de verificación

**Opción B: Domain Authentication (Recomendado para producción)**
1. Compra un dominio (ej: `despachocarcon.com`)
2. Configura DNS records en tu proveedor de dominio
3. Sigue las instrucciones de SendGrid

### 3. Crear API Key

1. Ve a **Settings > API Keys**
2. Haz clic en **Create API Key**
3. Nombre: `DespachoCarcon-ContactForm`
4. Permisos: **Full Access** (para empezar)
5. Copia la API Key (empieza con `SG.`)

### 4. Configurar en Django

1. Abre el archivo `.env` en la raíz del proyecto
2. Reemplaza la línea:
   ```env
   SENDGRID_API_KEY=tu_api_key_de_sendgrid_aqui
   ```
   Con tu API Key real:
   ```env
   SENDGRID_API_KEY=SG.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### 5. Probar la Configuración

Ejecuta el script de verificación:
```bash
cd despacho_django
python verificar_sendgrid.py
```

Deberías ver:
```
✅ SENDGRID_API_KEY configurada correctamente
✅ Librería SendGrid instalada
✅ URL del formulario configurada: /contact/
✅ Vista contact_form importada correctamente
```

### 6. Probar Envío de Email

Ejecuta el script de prueba:
```bash
python probar_email.py
```

Si funciona, recibirás un email de prueba.

---

## 🔧 Configuración Técnica Detallada

### Vista `contact_form` en `views_api.py`

```python
@csrf_exempt
@require_POST
def contact_form(request):
    """Vista para manejar el envío del formulario de contacto con SendGrid"""
    try:
        # Parsear datos JSON del frontend
        data = json.loads(request.body)

        # Validación y guardado en BD
        contacto = Contacto.objects.create(
            nombre=data['nombre'],
            email=data['correo'],
            mensaje=data['mensaje'],
            proyecto=data.get('proyecto', '')
        )

        # Configuración SendGrid
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))

        # Email para administrador
        admin_email = Mail(
            from_email='noreply@despachocarcon.com',  # ⚠️ Cambia por dominio verificado
            to_emails='carcon.arquitectura1@gmail.com',
            subject=f'Nuevo mensaje: {data["nombre"]}',
            html_content=f"""
            <h2>Nuevo contacto</h2>
            <p><strong>Nombre:</strong> {data['nombre']}</p>
            <p><strong>Email:</strong> {data['correo']}</p>
            <p><strong>Mensaje:</strong> {data['mensaje']}</p>
            """
        )

        # Email de confirmación para usuario
        confirmation_email = Mail(
            from_email='noreply@despachocarcon.com',  # ⚠️ Cambia por dominio verificado
            to_emails=data['correo'],
            subject='Mensaje recibido - Despacho Carcon',
            html_content=f"""
            <h2>¡Gracias por contactarnos!</h2>
            <p>Te responderemos pronto.</p>
            """
        )

        # Enviar ambos emails
        sg.send(admin_email)
        sg.send(confirmation_email)

        return JsonResponse({'success': True, 'message': 'Email enviado'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
```

### JavaScript en `app.js`

```javascript
// Envío del formulario
const res = await fetch('/contact', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')  // Si usas CSRF
    },
    body: JSON.stringify({
        nombre: nombre,
        correo: correo,
        mensaje: mensaje,
        proyecto: proyecto
    })
});
```

---

## 🚨 Errores Comunes y Soluciones

### ❌ "Error de conexión"

**Causa:** API Key inválida o no configurada
**Solución:** Verifica que `SENDGRID_API_KEY` esté correctamente configurada en `.env`

### ❌ "From email not verified"

**Causa:** El email `from_email` no está verificado en SendGrid
**Solución:** Verifica un Single Sender o configura Domain Authentication

### ❌ "Too many requests"

**Causa:** Límite de envío excedido (gratuito: 100 emails/día)
**Solución:** Actualiza a plan pago o reduce frecuencia de pruebas

### ❌ "Authentication failed"

**Causa:** API Key incorrecta o expirada
**Solución:** Regenera la API Key en SendGrid

---

## 📊 Flujo Completo del Formulario

1. **Usuario llena formulario** en `contacto.html`
2. **JavaScript valida** y envía datos a `/contact/`
3. **Vista contact_form** recibe datos JSON
4. **Guarda en BD** (modelo `Contacto`)
5. **Envía email** a administrador via SendGrid
6. **Envía confirmación** a usuario via SendGrid
7. **Responde JSON** con éxito/error
8. **JavaScript muestra** mensaje al usuario

---

## 🎯 Checklist de Verificación

- [ ] Cuenta SendGrid creada
- [ ] Email/Dominio verificado
- [ ] API Key generada y configurada
- [ ] Script `verificar_sendgrid.py` pasa ✅
- [ ] Script `probar_email.py` envía email ✅
- [ ] Formulario en navegador funciona
- [ ] Email llega a tu bandeja
- [ ] Email de confirmación llega al usuario

---

## 💡 Consejos para Producción

1. **Usa HTTPS** en producción
2. **Configura SPF/DKIM** para mejor deliverability
3. **Monitorea** envío de emails en SendGrid Dashboard
4. **Configura webhooks** para tracking de emails
5. **Actualiza plan** si necesitas más emails

---

## 📞 Soporte

- **SendGrid Docs:** https://docs.sendgrid.com/
- **Django SendGrid:** https://github.com/sendgrid/sendgrid-python
- **Pricing:** https://sendgrid.com/pricing/

---

*Una vez configurado SendGrid, tu formulario enviará emails automáticamente.* 🎉