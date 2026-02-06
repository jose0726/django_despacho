# ✅ Checklist de Producción (Railway) — despacho_django

Fecha: 2026-02-05

## 1) Cambios aplicados en el repositorio (verificado)

- Settings de Django ahora dependen de variables de entorno para producción:
  - `DJANGO_DEBUG` (por defecto `False`)
  - `DJANGO_SECRET_KEY` (obligatoria cuando `DJANGO_DEBUG=False`)
  - `DJANGO_ALLOWED_HOSTS` (obligatoria cuando `DJANGO_DEBUG=False`)
  - `DATABASE_URL` (obligatoria cuando `DJANGO_DEBUG=False`)
- Static listo para producción:
  - `STATIC_ROOT` habilitado
  - `collectstatic` probado localmente (genera `despacho_django/staticfiles/`)
  - WhiteNoise habilitado para servir estáticos en producción
- Servidor WSGI de producción:
  - `gunicorn` agregado a dependencias
  - `Procfile` agregado con comando `gunicorn`
- PostgreSQL preparado:
  - `dj-database-url` + `psycopg[binary]` agregados
  - `DATABASE_URL` soportado
- Contacto / Seguridad:
  - Se eliminó `@csrf_exempt` del endpoint `/contact/`
  - SendGrid ya no usa emails hardcodeados; usa env vars
  - CSRF failures devuelven JSON en endpoints tipo `/contact/`

## 2) Variables de entorno requeridas (Railway)

Obligatorias (producción):

- `DJANGO_DEBUG` = `False`
- `DJANGO_SECRET_KEY` = valor fuerte (mínimo 50+ chars)
- `DJANGO_ALLOWED_HOSTS` = lista separada por comas. Ejemplo:
  - `.up.railway.app,tu-dominio.com`
- `DATABASE_URL` = pega aquí la **Connection URL** del plugin PostgreSQL (Railway)
- `SENDGRID_API_KEY` = API Key de SendGrid
- `SENDGRID_FROM_EMAIL` = remitente verificado en SendGrid
- `SENDGRID_TO_EMAIL` = email administrador que recibe los contactos

Opcionales (solo si aplica):

- `DJANGO_LOG_LEVEL` = `INFO` (default) o `DEBUG`
- `CSRF_TRUSTED_ORIGINS` = orígenes con esquema `https://...` (coma-separados). Ejemplo:
  - `https://tu-dominio.com,https://tu-app.up.railway.app`
- `CORS_ALLOWED_ORIGINS` = solo si tienes frontend en otro dominio. Ejemplo:
  - `https://frontend.com`
- `DJANGO_SECURE_SSL_REDIRECT` = `True` (default en prod)
- `DJANGO_SECURE_HSTS_SECONDS` = `0` (puedes subirlo cuando estés seguro)

## 3) Configuración recomendada en Railway

1. Crear proyecto en Railway y conectar el repo.
2. Agregar plugin de PostgreSQL.
3. Copiar `DATABASE_URL` del plugin y definirla en variables del servicio.
4. Definir las variables del apartado (2).

### Build / Start

Si Railway no detecta el `Procfile`, configura manualmente:

- Build Command:
  - `python despacho_django/manage.py collectstatic --noinput`
  - `python despacho_django/manage.py migrate`
- Start Command:
  - `gunicorn despacho_django.wsgi:application --chdir despacho_django --bind 0.0.0.0:$PORT`

Nota: `migrate` puede ejecutarse también como paso manual tras el deploy.

## 4) Media / uploads (importante)

- Actualmente `MEDIA_ROOT` apunta a filesystem local.
- En Railway el filesystem **no es persistente** entre deploys/restarts.

Recomendación para producción:
- Mover uploads a un storage externo (S3/Cloudinary/etc.).
- Hasta entonces: evita depender de uploads persistentes (especialmente imágenes del equipo desde Admin).

## 5) Verificación rápida post-deploy

- Página principal carga CSS/JS (si no, revisar `collectstatic` + WhiteNoise).
- `/contact/` envía correctamente (200 JSON) y guarda en DB.
- Si hay 403 CSRF:
  - Confirmar que la página de contacto renderiza `{% csrf_token %}`
  - Confirmar que `CSRF_TRUSTED_ORIGINS` incluye el dominio HTTPS si aplica
- En Admin:
  - Validar que lectura/escritura a Postgres funciona

## 6) Archivos relevantes

- Django settings: `despacho_django/despacho_django/settings.py`
- Endpoint contacto: `despacho_django/proyectos/views_api.py`
- CSRF JSON failure: `despacho_django/proyectos/csrf.py`
- Procfile: `Procfile`
- Dependencias: `requirements.txt`
