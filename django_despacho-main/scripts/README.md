# Scripts (dev/QA)

Esta carpeta contiene scripts **solo para desarrollo/verificación**.
No forman parte del runtime de producción.

## Ejecutar
Desde la raíz del repo:

- Verificar templates:
  - `python scripts\verificar_templates.py`
- Verificar proyectos/API:
  - `python scripts\verificar_proyectos.py`
  - `python scripts\test_api.py`
- Verificar variables de entorno:
  - `python scripts\verificar_env.py`
- Verificar Font Awesome local:
  - `python scripts\verificar_fontawesome.py`
- Diagnóstico SendGrid:
  - `python scripts\debug_sendgrid.py`
  - `python scripts\verificar_sendgrid.py`
  - `python scripts\probar_email.py`

## Importante
- `importa_proyectos.py` borra y reimporta proyectos (usar solo en entornos controlados).
