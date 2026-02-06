# Línea del tiempo del proyecto (basada en timestamps)

Fecha de corte: **2026-02-03**.

> Este repositorio no tiene historial Git (no hay commits). Por eso, esta línea del tiempo se construye con los metadatos del sistema de archivos (**LastWriteTime**). Es lo más “auditable” que podemos obtener hoy, pero no equivale a un historial real de cambios.

## Rango temporal detectado
- **Inicio más antiguo** (assets): **2025-09-25 14:00**
- **Última modificación** (código/CSS): **2026-02-03 01:19**

## Metodología (cómo se obtuvo)
- Se listaron archivos por `LastWriteTime` y se tomaron “anclas” (archivos representativos) por fecha.
- Se excluyó ruido: `__pycache__`, `.pyc`, vendor grande (`static/fontawesome`) para los conteos diarios.
- Se separaron “assets” (imágenes/vendor) del “código” (Django/templates/CSS) para que sea claro qué cambió primero.

## Anclas cronológicas verificables

### 2025-09-25 a 2025-10-03 — Assets iniciales del sitio
- 2025-09-25 14:00 — `despacho_django/static/img/casa-moderna.jpg`
- 2025-09-26 12:28 — `despacho_django/static/img/oficina-minimalista.jpg`
- 2025-09-26 12:40 — `despacho_django/static/img/explicando.jpg`
- 2025-10-02 10:44 — `despacho_django/static/img/logo-CARCOM.png`
- 2025-10-03 10:41 — `despacho_django/static/img/casa1.jpg`

Interpretación: antes de “armar Django”, ya existían imágenes/branding del sitio.

### 2025-09-29 — Vendor: Font Awesome local
- 2025-09-29 21:06 — `despacho_django/static/fontawesome/...` (CSS y webfonts)

Interpretación: se integró Font Awesome en versión local (sin CDN) muy temprano.

### 2025-12-08 — Esqueleto Django + migración inicial
- 2025-12-08 14:39 — `despacho_django/manage.py`
- 2025-12-08 14:39 — `despacho_django/despacho_django/asgi.py`, `wsgi.py`, `__init__.py`
- 2025-12-08 14:47 — `despacho_django/proyectos/migrations/0001_initial.py`
- 2025-12-08 13:55 — `despacho_django/proyectos.json`

Interpretación: arranque del proyecto Django y primer estado de modelos/migraciones.

### 2025-12-12 — Datos/JSON de proyectos
- 2025-12-12 11:38 — `despacho_django/static/js/proyectos.json`

### 2026-01-09 — Templates de proyectos + segunda migración + rutas
- 2026-01-09 12:25 — `despacho_django/proyectos/templates/proyectos/list.html`
- 2026-01-09 12:25 — `despacho_django/proyectos/templates/proyectos/detail.html`
- 2026-01-09 13:22 — `despacho_django/proyectos/migrations/0002_proyectoimagen.py`
- 2026-01-09 14:22 — `despacho_django/despacho_django/urls.py`

### 2026-01-12 — Paquete fuerte de documentación
- 2026-01-12 12:10 — `README_FONTAWESOME.md`, `FONT_AWESOME_SETUP.md`, `RESUMEN_FINAL.md`, `CHECKLIST_PRODUCCION.md`
- 2026-01-12 12:51 — `SENDGRID_GUIA.md`

### 2026-01-16 — Configuración + scripts de verificación + requirements
- 2026-01-16 14:18 — `despacho_django/despacho_django/settings.py`
- 2026-01-16 13:37 — `requirements.txt`
- 2026-01-16 13:22–13:37 — `scripts/*` (verificación de templates, sendgrid, renderizado, etc.)
- 2026-01-16 13:37 — `DOCUMENTACION_PROYECTO.md`, `INDICE.md`, `AUDITORIA_FINAL_PRODUCCION.md`

### 2026-01-22 — Página proyectos pública + carga de media
- 2026-01-22 20:58 — `despacho_django/templates/proyectos.html`
- 2026-01-22 22:11–22:27 — `despacho_django/media/proyectos/*` (múltiples imágenes subidas)

### 2026-01-23 — Base template, contacto, auditorías y seguridad
- 2026-01-23 15:58 — `despacho_django/templates/base.html`
- 2026-01-23 16:54 — `despacho_django/templates/contacto.html`
- 2026-01-23 17:13 — `despacho_django/proyectos/views_api.py`
- 2026-01-23 16:54 — `SECURITY_AUDIT_CONTACTO.md`, `AUDIT_*`, `CSS_*`, `IMPLEMENTATION_TECHNICAL_GUIDE.md`
- 2026-01-23 18:36 — `despacho_django/static/img/equipo.JPG` (asset de equipo en static)

### 2026-02-03 — Cambios UI/CSS + Sobre Nosotros editable (Admin) + media equipo
- 2026-02-03 00:55–00:56 — `despacho_django/proyectos/models.py`, `admin.py`, `views.py`, `migrations/0003_equiposeccion_equipomiembro.py`
- 2026-02-03 00:47 — `despacho_django/templates/index.html`, `despacho_django/static/css/index.css`
- 2026-02-03 01:06 — `despacho_django/templates/sobre-nosotros.html`
- 2026-02-03 01:07 — `despacho_django/static/css/styles.css`
- 2026-02-03 01:19 — `despacho_django/static/css/proyectos.css`
- 2026-02-03 01:07 — `despacho_django/media/equipo/equipo.JPG` (subida/uso desde media)

Interpretación: día de integración fuerte (UI, CSS, refactor de “Sobre Nosotros” y habilitación de contenido editable desde Admin).

## Actividad por día (archivos de código/docs modificados)
Conteo de archivos (filtrado, sin `media/`, sin `static/fontawesome/`, sin `__pycache__`):

| Fecha | Archivos modificados |
|------:|-----------------------:|
| 2025-12-08 | 9 |
| 2025-12-12 | 1 |
| 2026-01-09 | 5 |
| 2026-01-12 | 6 |
| 2026-01-16 | 18 |
| 2026-01-22 | 1 |
| 2026-01-23 | 13 |
| 2026-02-03 | 9 |

## Limitaciones importantes (para auditoría)
- `LastWriteTime` puede alterarse al copiar/extraer archivos o al restaurar backups.
- No hay garantía de “orden real” dentro del mismo minuto.
- Sin commits Git, no se puede reconstruir quién cambió qué ni por qué; solo “qué archivo muestra una fecha”.

## Recomendación (para que la siguiente auditoría sea perfecta)
1. Inicializar Git (`git init`) y agregar `.gitignore` (incluyendo `media/`, `db.sqlite3`, `.venv/`, `__pycache__/`).
2. Hacer un commit inicial y luego commits por feature (CSS, contacto, admin equipo, etc.).
3. Etiquetar entregas (`git tag v1.0-entrega`).
