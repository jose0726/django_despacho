# Instructivo — Levantar el proyecto en otra PC y en Railway

Este documento explica cómo clonar el proyecto, correrlo localmente y desplegarlo en Railway desde cero.

**Stack tecnológico:** Django 5.2.9 · Python 3.11.9 · PostgreSQL (prod) / SQLite (local) · Cloudinary · SendGrid · Gunicorn · WhiteNoise

---

## 1. Requisitos previos (instalar en la PC)

| Herramienta | Versión mínima | Dónde descargar |
|---|---|---|
| Python | 3.11 | https://www.python.org/downloads/ |
| Git | Cualquier reciente | https://git-scm.com/downloads |
| VS Code (opcional) | Cualquier | https://code.visualstudio.com/ |

> **Windows:** al instalar Python, marca la casilla **"Add Python to PATH"**.

---

## 2. Clonar el repositorio

Abre una terminal (PowerShell o cmd) y ejecuta:

```powershell
git clone https://github.com/jose0726/django_despacho.git
cd django_despacho
```

---

## 3. Crear el entorno virtual e instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Si PowerShell te da error de permisos al activar el entorno, ejecuta primero:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## 4. Crear el archivo `.env` (variables de entorno locales)

Copia el archivo de ejemplo que ya viene en el repo:

```powershell
copy .env.example .env
```

Abre `.env` y asegúrate de tener al menos estos valores para correr en local:

```env
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=cualquier-cadena-larga-inventada-aqui
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

> Para desarrollo local **no necesitas** DATABASE_URL, CLOUDINARY_URL ni SendGrid.
> Django usará SQLite y guardará archivos en local automáticamente.
> El formulario de contacto guardará mensajes en la base de datos aunque no pueda enviar emails.

---

## 5. Correr el servidor local

```powershell
python despacho_django\manage.py migrate
python despacho_django\manage.py runserver
```

Abre en el navegador: **http://localhost:8000**

### Crear un usuario administrador local (opcional)

```powershell
python despacho_django\manage.py createsuperuser
```

Luego entra a: **http://localhost:8000/admin/**

---

## 6. Estructura del proyecto

```
django_despacho/
├── despacho_django/                # Proyecto Django principal
│   ├── despacho_django/            # Configuración (settings, urls, wsgi)
│   ├── proyectos/                  # App principal
│   │   ├── models.py              # Modelos de datos
│   │   ├── views.py               # Vistas (páginas HTML)
│   │   ├── views_api.py           # API JSON (proyectos, contacto)
│   │   ├── admin.py               # Configuración del panel admin
│   │   ├── urls.py                # Rutas de la app
│   │   ├── migrations/            # Migraciones de BD
│   │   └── templates/proyectos/   # Templates de la app
│   ├── templates/                  # Templates globales (base, index, etc.)
│   ├── static/                     # CSS, JS, imágenes, FontAwesome
│   └── media/                      # Archivos subidos (solo local)
├── scripts/
│   └── railway_start.py            # Script de inicio para Railway
├── requirements.txt
├── Procfile
├── nixpacks.toml
├── runtime.txt                     # Python 3.11.9
└── .env.example                    # Plantilla de variables de entorno
```

### Rutas disponibles

| Ruta | Descripción |
|---|---|
| `/` | Página de inicio (con video configurable) |
| `/proyectos/` | Portafolio de proyectos (filtrado por categoría/subcategoría) |
| `/contacto/` | Formulario de contacto |
| `/sobre-nosotros/` | Página "Sobre nosotros" (equipo) |
| `/admin/` | Panel de administración de Django |
| `/api/proyectos/` | API JSON de proyectos (paginada, con filtros) |

---

## 7. Obtener las API Keys necesarias para producción

### 7.1 Cloudinary (almacenamiento de imágenes, videos y modelos 3D)

1. Ve a https://cloudinary.com y crea una cuenta gratuita.
2. Una vez dentro, ve al **Dashboard**.
3. Copia el valor de **"API Environment variable"** (empieza con `cloudinary://...`).
4. Ese valor es tu `CLOUDINARY_URL`.

> **Nota:** Cloudinary se usa para que las imágenes, videos y archivos 3D persistan entre deploys en Railway. Sin Cloudinary los archivos se pierden cada vez que Railway redespliega.

### 7.2 SendGrid (envío de emails del formulario de contacto)

1. Ve a https://sendgrid.com y crea una cuenta gratuita.
2. Ve a **Settings → API Keys → Create API Key**.
3. Elige **Full Access** (o **Restricted Access** con permiso de Mail Send).
4. Copia la API Key generada — **solo se muestra una vez**.
5. También necesitas:
   - `SENDGRID_FROM_EMAIL` → el correo **verificado** en tu cuenta SendGrid (el remitente).
   - `SENDGRID_TO_EMAIL` → el correo donde quieres recibir los mensajes del formulario.

> **Importante:** el email de `SENDGRID_FROM_EMAIL` debe estar verificado en SendGrid
> (Settings → Sender Authentication → Single Sender Verification).

> **Nota:** si no configuras SendGrid, el formulario de contacto sigue funcionando — los mensajes se guardan en la base de datos, solo no se envían emails.

---

## 8. Desplegar en Railway

### 8.1 Crear cuenta en Railway

Ve a https://railway.app y crea una cuenta (puedes usar GitHub para login rápido).

### 8.2 Crear un nuevo proyecto

1. En Railway → **New Project**.
2. Elige **Deploy from GitHub repo**.
3. Conecta tu cuenta de GitHub y selecciona el repo `django_despacho`.
4. Railway detectará el `Procfile` o `nixpacks.toml` automáticamente.

### 8.3 Agregar base de datos PostgreSQL

1. Dentro del proyecto → **Add Service → Database → PostgreSQL**.
2. Espera ~1 minuto a que se cree.
3. Haz clic en la DB → **Variables** y copia el valor de `DATABASE_URL`.

### 8.4 Configurar las Variables de entorno

En Railway → tu servicio web → **Variables**, agrega:

| Variable | Valor | Secret? |
|---|---|---|
| `DJANGO_DEBUG` | `false` | No |
| `DJANGO_SECRET_KEY` | Cadena larga aleatoria (mín 50 chars) — ver paso 10 | **Sí** |
| `DJANGO_ALLOWED_HOSTS` | `tu-app.railway.app` (la URL que da Railway) | No |
| `DATABASE_URL` | El URL copiado del paso 8.3 | **Sí** |
| `CLOUDINARY_URL` | El valor del Dashboard de Cloudinary | **Sí** |
| `SENDGRID_API_KEY` | La API Key de SendGrid | **Sí** |
| `SENDGRID_FROM_EMAIL` | Tu correo verificado en SendGrid | No |
| `SENDGRID_TO_EMAIL` | Correo donde recibes mensajes | No |

> **Secret (Seal):** al agregar una variable sensible, marca el checkbox **"Seal"** para ocultarla en los logs.

### 8.5 Crear el primer usuario administrador (solo primera vez)

Agrega estas variables temporales:

| Variable | Valor |
|---|---|
| `CREATE_SUPERUSER` | `true` |
| `DJANGO_SUPERUSER_USERNAME` | El usuario que quieras (ej: `admin`) |
| `DJANGO_SUPERUSER_EMAIL` | Tu correo |
| `DJANGO_SUPERUSER_PASSWORD` | Tu contraseña (**marcar como Secret**) |

Después del primer deploy exitoso, **borra o pon en `false`** la variable `CREATE_SUPERUSER`.

### 8.6 Cargar proyectos iniciales desde JSON (opcional)

Si tienes un archivo `proyectos.json` en el repo y quieres cargar los proyectos automáticamente en el primer deploy:

| Variable | Valor |
|---|---|
| `SEED_PROJECTS` | `true` |
| `SEED_PROJECTS_FORCE` | `false` (poner `true` para borrar y recargar todo) |

> El script buscará el archivo `proyectos.json` en varias ubicaciones del proyecto.
> Después del primer deploy exitoso, puedes borrar estas variables.

### 8.7 Hacer el deploy

Railway despliega automáticamente al conectar el repo.
Si quieres forzarlo: **Deploy → Redeploy**.

El log del deploy debe mostrar (en orden):
```
>>> Running migrations
>>> Collecting static files
>>> Starting Gunicorn
```

### 8.8 Verificar que funciona

Abre la URL que te da Railway (ej: `https://tu-app.railway.app`):

- `/` → Página de inicio
- `/proyectos/` → Portafolio
- `/sobre-nosotros/` → Equipo
- `/contacto/` → Formulario de contacto
- `/admin/` → Panel de administración (con el usuario creado)

---

## 9. Cargar contenido desde el Admin

Una vez en `/admin/`:

| Sección | Para qué |
|---|---|
| **Proyectos** | Agregar proyectos con nombre, descripción, categoría, subcategoría, imagen principal y galería de imágenes |
| **Modelo 3D (en Proyectos)** | Subir archivo `.glb` o `.gltf` para visor 3D interactivo en la página del proyecto |
| **Proyecto Imágenes** | Galería de imágenes por proyecto (se agregan desde el inline dentro de cada proyecto) |
| **Equipo Miembros** | Agregar miembros del equipo (arquitectos y colaboradores) con foto, nombre y rol. Aparecen en "Sobre nosotros" |
| **Sección Equipo** | Foto grupal del equipo que aparece en "Sobre nosotros" |
| **Configuración de Inicio** | Video de la homepage: subir archivo mp4/webm **o** pegar URL de YouTube |
| **Contacto** | Ver los mensajes recibidos desde el formulario de contacto |

### Categorías de proyectos

Los proyectos se organizan por **categoría** y opcionalmente por **subcategoría**. El sistema de filtrado en `/proyectos/` las detecta automáticamente desde los datos — no necesitas configurar las categorías por separado.

---

## 10. Generar un `DJANGO_SECRET_KEY` seguro

En Python (desde cualquier terminal con Python instalado):

```python
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copia el resultado y úsalo como `DJANGO_SECRET_KEY`.

---

## 11. Resumen de variables de entorno

### Obligatorias en producción

| Variable | Dónde se obtiene |
|---|---|
| `DJANGO_SECRET_KEY` | Generar con Python (ver paso 10) |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_ALLOWED_HOSTS` | La URL que da Railway |
| `DATABASE_URL` | Railway → DB → Variables |
| `CLOUDINARY_URL` | Dashboard Cloudinary |

### Opcionales (para formulario de contacto con email)

| Variable | Dónde se obtiene |
|---|---|
| `SENDGRID_API_KEY` | Dashboard SendGrid |
| `SENDGRID_FROM_EMAIL` | Tu correo verificado en SendGrid |
| `SENDGRID_TO_EMAIL` | Correo donde recibes mensajes |

### Solo primera vez (deploy inicial)

| Variable | Descripción |
|---|---|
| `CREATE_SUPERUSER` | `true` (luego borrar) |
| `DJANGO_SUPERUSER_USERNAME` | El usuario que quieras |
| `DJANGO_SUPERUSER_EMAIL` | Tu correo |
| `DJANGO_SUPERUSER_PASSWORD` | Tu contraseña |
| `SEED_PROJECTS` | `true` para cargar proyectos desde JSON (opcional) |
| `SEED_PROJECTS_FORCE` | `true` para forzar recarga (opcional) |

### Configuración avanzada de Gunicorn (opcional)

| Variable | Default | Descripción |
|---|---|---|
| `PORT` | `8080` | Puerto donde escucha Gunicorn |
| `WEB_CONCURRENCY` | `2` | Número de workers de Gunicorn |
| `GUNICORN_TIMEOUT` | `60` | Timeout en segundos por request |
| `GUNICORN_LOG_LEVEL` | `info` | Nivel de log (`debug`, `info`, `warning`, `error`) |

---

## 12. API JSON

El proyecto expone una API para consumo desde el frontend:

### `GET /api/proyectos/`

Devuelve la lista paginada de proyectos.

**Parámetros de query:**

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `categoria` | Filtrar por categoría (insensible a mayúsculas) | `?categoria=habitacional` |
| `sub` | Filtrar por subcategoría | `?sub=interior` |
| `q` | Buscar por nombre | `?q=lomas` |
| `page` | Página (default: 1) | `?page=2` |
| `page_size` | Resultados por página (default: 12, máx: 100) | `?page_size=50` |

**Respuesta:**
```json
{
  "count": 15,
  "page": 1,
  "pages": 2,
  "page_size": 12,
  "results": [
    {
      "id": 1,
      "nombre": "Proyecto X",
      "descripcion": "...",
      "categoria": "Habitacional",
      "subcategoria": "Interior",
      "imagenes": [{ "imagen": "/media/..." }],
      "fecha_creacion": "2026-01-15T..."
    }
  ]
}
```

### `POST /contact/`

Envía un mensaje desde el formulario de contacto.

**Body (JSON):**
```json
{
  "nombre": "Juan Pérez",
  "correo": "juan@gmail.com",
  "mensaje": "Me interesa su servicio",
  "proyecto": "Proyecto X"
}
```

> El correo debe ser de un dominio conocido (Gmail, Outlook, Yahoo, Proton, etc.). Se usa validación de dominio para prevenir spam.

---

## Seguridad

El proyecto incluye las siguientes protecciones:

- **CSRF:** protección activa en formularios y endpoints (con vista personalizada para JSON)
- **XSS:** sanitización de HTML en entradas del formulario de contacto
- **Honeypot:** campo oculto en el formulario para detectar bots
- **Whitelist de dominios de email:** solo acepta correos de proveedores conocidos
- **HTTPS:** cookies seguras y HSTS en producción
- **CORS:** configurado vía `django-cors-headers`
- **WhiteNoise:** archivos estáticos servidos con compresión y cache headers

---

## Soporte

Si algo falla, revisa primero los **Logs del deploy** en Railway (botón "View Logs" en el servicio web). Los errores más comunes y sus causas:

| Error en logs | Causa |
|---|---|
| `ImproperlyConfigured: DJANGO_SECRET_KEY is required` | Falta la variable `DJANGO_SECRET_KEY` |
| `ImproperlyConfigured: DATABASE_URL is required` | Falta o es incorrecta `DATABASE_URL` |
| `connection failed` / `Name or service not known` | `DATABASE_URL` incorrecta o DB no levantada |
| `ModuleNotFoundError` | Dependencia faltante en `requirements.txt` |
| `DisallowedHost` | Falta el dominio en `DJANGO_ALLOWED_HOSTS` |
| Error 500 en página | Revisar logs de Gunicorn en Railway |
| Imágenes no cargan después de redeploy | Falta `CLOUDINARY_URL` (sin Cloudinary los archivos se pierden entre deploys) |
| Formulario de contacto no envía emails | Verificar `SENDGRID_API_KEY` y que el remitente esté verificado |
