# Auditoría Final de Producción — Despacho Carcon

Fecha: 2026-01-16

## 1) Veredicto
**Apto para entregar en modo “MVP”, con condiciones.**

Condiciones mínimas antes de publicar:
- Desactivar `DEBUG`.
- Ajustar CORS para producción (no permitir todo).
- Definir estrategia de estáticos (`collectstatic`) y media persistente.
- Confirmar envío de correo (SendGrid) desde la red/hosting real (sin interceptación TLS).

## 2) Riesgos y hallazgos (priorizados)
### Must-fix (bloquean producción)
- **CORS demasiado permisivo**: actualmente `CORS_ALLOW_ALL_ORIGINS = True` en settings. En producción debe restringirse a dominios reales.
- **Static/media**: falta `STATIC_ROOT`/`collectstatic` como paso de deploy (necesario en PaaS típico).
- **SendGrid dependiente de red**: en algunos entornos falla por TLS interceptado; se debe validar en el hosting final.

### Should-fix (recomendado)
- **Eliminar scripts que exponen claves**: hay scripts que imprimen prefijos de API keys y deberían quedarse fuera del deploy.
- **Unificar `.env`**: existen `.env` en raíz y dentro de `despacho_django/`. El settings actualmente lee el `.env` de la raíz del repo.
- **Remitentes en SendGrid**: los `from_email` están hardcodeados; ideal parametrizar por env.

### Nice-to-have
- Agregar `requirements.txt` (ya incluido en este repo).
- Agregar README de despliegue por proveedor (Railway/Render/Fly).

## 3) Estado del formulario de contacto (post-fix)
- Frontend usa `/contact/` y envía `X-CSRFToken`.
- Backend requiere CSRF (se removió `csrf_exempt`).
- En error CSRF, responde JSON (evita que el frontend intente parsear HTML como JSON).
- Si falla SendGrid: guarda en DB y responde `502` con mensaje para contactar por teléfono.

## 4) Clasificación de archivos (pre-entrega)
Recomendación práctica: mover scripts a una carpeta `scripts/` y no incluirlos en el artefacto de despliegue.

### ✅ Runtime (se queda en producción)
- `despacho_django/` (proyecto Django)
- `despacho_django/proyectos/` (app principal)
- `despacho_django/templates/`, `despacho_django/static/`

### 📚 Documentación (se entrega)
- `DOCUMENTACION_PROYECTO.md`
- `SENDGRID_GUIA.md`
- Documentos FontAwesome: `README_FONTAWESOME.md`, `FONT_AWESOME_SETUP.md`, `CHECKLIST_PRODUCCION.md`, etc.

### 🧪 Scripts dev/QA (no deploy)
- `debug_sendgrid.py` (diagnóstico)
- `test_api.py`, `test_env.py`, `test_fontawesome.py`
- `verificar_env.py`, `verificar_fontawesome.py`
- `despacho_django/verificar_*.py` (verificaciones locales)

### ⚠️ Peligrosos en producción (mantener solo con advertencia)
- `importa_proyectos.py` (borra y reimporta proyectos; usar solo en entornos controlados)

### ❌ Recomendación: eliminar o asegurar
- `simple_test.py` y `test_sendgrid_connection.py` (imprimen partes de la API key; mantener solo local y con cuidado)

## 5) Proyectos sin imágenes (recomendación)
- Backend ya devuelve `imagenes: []` si no hay imágenes.
- Recomendación de UX:
  - Mostrar un placeholder (ya existe “Sin imagen” en el frontend) y mantener proporción.
  - En admin: permitir guardar proyectos sin imágenes sin romper listado.
  - En SEO: evitar imágenes rotas; no generar `<img>` si no hay URL.

## 6) Despliegue managed recomendado (alto nivel)
Opciones típicas:
- **Railway**: fácil, DB Postgres, variables de entorno, deployments rápidos.
- **Render**: similar, buena experiencia con servicios web + Postgres.

En ambos casos (recomendación mínima):
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS` con el dominio del servicio
- Ejecutar `python manage.py migrate` y `python manage.py collectstatic`
- Configurar persistencia para `MEDIA_ROOT` (o usar storage externo)

## 7) Checklist final (mínimo)
- Variables env completas (`SENDGRID_API_KEY`, `DJANGO_SECRET_KEY`, hosts)
- `DEBUG=False`
- CORS restringido
- `collectstatic` configurado
- Crear usuario admin
- Probar formulario contacto en el hosting final
