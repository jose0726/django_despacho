# Documentación del Proyecto — Despacho Carcon (Django)

## 1) Resumen
Este proyecto es un sitio web tipo portafolio para un despacho (páginas públicas + listado/detalle de proyectos) e incluye un formulario de contacto que:
- Guarda el mensaje en la base de datos.
- Intenta enviar notificación por email con SendGrid.

## 2) Stack
- Python 3.11
- Django 5.2
- Base de datos: SQLite (desarrollo)
- Envío de correo: SendGrid (`sendgrid`)
- Variables de entorno: `python-dotenv` (solo para desarrollo local)
- CORS: `django-cors-headers` (ojo en producción)
- Imágenes: Pillow (`pillow`)

## 3) Estructura del repositorio
- `despacho_django/`
  - `manage.py`
  - `despacho_django/` (settings/urls/wsgi/asgi)
  - `proyectos/` (app principal: modelos, vistas, API)
  - `templates/` (templates del sitio)
  - `static/` (CSS/JS/FontAwesome local)
  - `media/` (subidas/imagenes en desarrollo)

Nota: existe una carpeta `proyectos/` también en la raíz del repo; el runtime real del proyecto está dentro de `despacho_django/proyectos/`.

## 4) Variables de entorno (.env)
El proyecto lee variables desde un archivo `.env` en la **raíz del repo** (porque `settings.py` carga `BASE_DIR.parent / '.env'`).

Variables recomendadas:
- `DJANGO_SECRET_KEY`: secret key (obligatoria en producción)
- `DJANGO_DEBUG`: `False` en producción
- `DJANGO_ALLOWED_HOSTS`: hosts permitidos (dominio/URL)
- `DJANGO_LOG_LEVEL`: `INFO`/`WARNING`/`ERROR`
- `SENDGRID_API_KEY`: API Key de SendGrid
- `SSL_CERT_FILE`: ruta a un bundle `.pem` (solo si tu red/proxy/antivirus intercepta TLS)

Archivo de ejemplo: `.env.example`.

## 5) Dependencias
Instalación recomendada:
```bash
python -m pip install -r requirements.txt
```

El archivo `requirements.txt` está incluido para que el despliegue sea reproducible.

## 6) Ejecución local
Desde la raíz del repo:
```bash
python despacho_django\manage.py migrate
python despacho_django\manage.py runserver
```

### Admin
- URL: `/admin/`
- Crear superusuario:
```bash
python despacho_django\manage.py createsuperuser
```

## 7) Funcionalidad
### Páginas
- `/` inicio
- `/proyectos/` listado
- `/proyecto/<id>/` detalle
- `/contacto/` formulario
- `/sobre-nosotros/` página informativa

### API
- `GET /api/proyectos/`
  - Parámetros: `page`, `page_size`, `categoria`, `sub`, `q`
  - Respuesta: `count`, `page`, `pages`, `page_size`, `results`

### Contacto (JSON)
- `POST /contact/` (también existe alias `POST /contact`)
- Body JSON:
  - `nombre`, `correo`, `mensaje`, `proyecto` (opcional), `hp` (honeypot)
- Respuestas:
  - `200`: `{ ok: true, message: ... }`
  - `400`: validación / honeypot
  - `405`: método incorrecto
  - `502`: guardó en DB, pero falló envío SendGrid

**CSRF**: el formulario incluye `{% csrf_token %}` y el frontend envía `X-CSRFToken`. Si falla CSRF, el backend responde JSON con status `403`.

## 8) Envío de emails (SendGrid)
El endpoint de contacto intenta enviar:
- 1 email interno al admin
- 1 email de confirmación al usuario

Si SendGrid falla por temas de red/TLS (por ejemplo `SSLCertVerificationError` con “self-signed certificate in certificate chain”), normalmente es por:
- Proxy corporativo / antivirus interceptando HTTPS

Solución típica:
- Exportar el certificado raíz de tu organización/proxy en un `.pem`
- Definir `SSL_CERT_FILE` apuntando a ese `.pem`

Script útil de diagnóstico: `debug_sendgrid.py` (solo desarrollo).

## 9) Static/Media en producción
- En desarrollo Django sirve `STATIC_URL` y `MEDIA_URL`.
- En producción normalmente se usa:
  - `collectstatic` + servidor de estáticos (Nginx) o servicio de estáticos del PaaS
  - Para media (subidas) idealmente un storage externo (S3/Cloudinary) o volumen persistente

## 10) Checklist mínimo de producción (resumen)
- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY` fuerte y privada
- `DJANGO_ALLOWED_HOSTS` correcto (dominio real)
- Restringir CORS (no dejar allow-all)
- Logs en `INFO`/`WARNING`
- Revisar SendGrid: remitente verificado y API key con permisos mínimos
- Estrategia de `STATIC_ROOT` + `collectstatic`
- Estrategia de media persistente

## 11) Troubleshooting rápido
- `403 CSRF`: recargar página; verificar cookies; revisar que el JS envía `X-CSRFToken`.
- `502 guardado pero no envía email`: revisar logs; revisar TLS/proxy; probar `debug_sendgrid.py`.
- Imágenes no cargan: revisar `MEDIA_URL/MEDIA_ROOT` y que el servidor sirva `/media/`.
