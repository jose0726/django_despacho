# Instructivo — Levantar el proyecto en otra PC y en Railway

Este documento explica cómo clonar el proyecto, correrlo localmente y desplegarlo en Railway desde cero.

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

Copia el archivo de ejemplo:

```powershell
copy .env.example .env
```

Abre `.env` y llena los valores mínimos para correr en local:

```env
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=cualquier-cadena-larga-inventada-aqui
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

> Para desarrollo local **no necesitas** DATABASE_URL, CLOUDINARY_URL ni SendGrid.
> Django usará SQLite y guardará archivos en local automáticamente.

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

## 6. Obtener las API Keys necesarias para producción

### 6.1 Cloudinary (almacenamiento de imágenes y videos)

1. Ve a https://cloudinary.com y crea una cuenta gratuita.
2. Una vez dentro, ve al **Dashboard**.
3. Copia el valor de **"API Environment variable"** (empieza con `cloudinary://...`).
4. Ese valor es tu `CLOUDINARY_URL`.

### 6.2 SendGrid (envío de emails del formulario de contacto)

1. Ve a https://sendgrid.com y crea una cuenta gratuita.
2. Ve a **Settings → API Keys → Create API Key**.
3. Elige **Full Access** (o **Restricted Access** con permiso de Mail Send).
4. Copia la API Key generada — **solo se muestra una vez**.
5. También necesitas:
   - `SENDGRID_FROM_EMAIL` → el correo **verificado** en tu cuenta SendGrid (el remitente).
   - `SENDGRID_TO_EMAIL` → el correo donde quieres recibir los mensajes del formulario.

> **Importante:** el email de `SENDGRID_FROM_EMAIL` debe estar verificado en SendGrid
> (Settings → Sender Authentication → Single Sender Verification).

---

## 7. Desplegar en Railway

### 7.1 Crear cuenta en Railway

Ve a https://railway.app y crea una cuenta (puedes usar GitHub para login rápido).

### 7.2 Crear un nuevo proyecto

1. En Railway → **New Project**.
2. Elige **Deploy from GitHub repo**.
3. Conecta tu cuenta de GitHub y selecciona el repo `django_despacho`.
4. Railway detectará el `Procfile` o `nixpacks.toml` automáticamente.

### 7.3 Agregar base de datos PostgreSQL

1. Dentro del proyecto → **Add Service → Database → PostgreSQL**.
2. Espera ~1 minuto a que se cree.
3. Haz clic en la DB → **Variables** y copia el valor de `DATABASE_URL`.

### 7.4 Configurar las Variables de entorno

En Railway → tu servicio web → **Variables**, agrega:

| Variable | Valor | Secret? |
|---|---|---|
| `DJANGO_DEBUG` | `false` | No |
| `DJANGO_SECRET_KEY` | Cadena larga aleatoria (mín 50 chars) | **Sí** |
| `DJANGO_ALLOWED_HOSTS` | `tu-app.railway.app` (la URL que da Railway) | No |
| `DATABASE_URL` | El URL copiado del paso 7.3 | **Sí** |
| `CLOUDINARY_URL` | El valor del Dashboard de Cloudinary | **Sí** |
| `SENDGRID_API_KEY` | La API Key de SendGrid | **Sí** |
| `SENDGRID_FROM_EMAIL` | Tu correo verificado en SendGrid | No |
| `SENDGRID_TO_EMAIL` | Correo donde recibes mensajes | No |

> **Secret (Seal):** al agregar una variable sensible, marca el checkbox **"Seal"** para ocultarla en los logs.

### 7.5 Crear el primer usuario administrador (solo primera vez)

Agrega estas variables temporales:

| Variable | Valor |
|---|---|
| `CREATE_SUPERUSER` | `true` |
| `DJANGO_SUPERUSER_USERNAME` | El usuario que quieras (ej: `admin`) |
| `DJANGO_SUPERUSER_EMAIL` | Tu correo |
| `DJANGO_SUPERUSER_PASSWORD` | Tu contraseña (**marcar como Secret**) |

Después del primer deploy exitoso, **borra o pon en `false`** la variable `CREATE_SUPERUSER`.

### 7.6 Hacer el deploy

Railway despliega automáticamente al conectar el repo.
Si quieres forzarlo: **Deploy → Redeploy**.

El log del deploy debe mostrar (en orden):
```
>>> Running migrations
>>> Collecting static files
>>> Starting Gunicorn
```

### 7.7 Verificar que funciona

Abre la URL que te da Railway (ej: `https://tu-app.railway.app`):

- `/` → Página de inicio
- `/proyectos/` → Portafolio
- `/admin/` → Panel de administración (con el usuario creado)

---

## 8. Cargar contenido desde el Admin

Una vez en `/admin/`:

| Sección | Para qué |
|---|---|
| **Proyectos** | Agregar proyectos con imágenes y galería |
| **Equipo Miembros** | Miembros del equipo en "Sobre nosotros" |
| **Sección Equipo** | Foto grupal del equipo |
| **Configuración de Inicio** | Video de la home (subir archivo mp4/webm o pegar URL de YouTube) |
| **Contacto** | Ver mensajes recibidos del formulario |

---

## 9. Generar un `DJANGO_SECRET_KEY` seguro

En Python (desde cualquier terminal con Python instalado):

```python
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copia el resultado y úsalo como `DJANGO_SECRET_KEY`.

---

## 10. Resumen de variables de entorno

| Variable | Obligatoria en prod | Dónde se obtiene |
|---|---|---|
| `DJANGO_SECRET_KEY` | Sí | Generar con Python (ver paso 9) |
| `DJANGO_DEBUG` | Sí (`false`) | Escribir manualmente |
| `DJANGO_ALLOWED_HOSTS` | Sí | La URL que da Railway |
| `DATABASE_URL` | Sí | Railway → DB → Variables |
| `CLOUDINARY_URL` | Sí (para imágenes/video) | Dashboard Cloudinary |
| `SENDGRID_API_KEY` | Sí (para formulario) | Dashboard SendGrid |
| `SENDGRID_FROM_EMAIL` | Sí (para formulario) | Tu correo verificado en SendGrid |
| `SENDGRID_TO_EMAIL` | Sí (para formulario) | Correo donde recibes mensajes |
| `CREATE_SUPERUSER` | Solo primera vez | `true` (luego borrar) |
| `DJANGO_SUPERUSER_USERNAME` | Solo primera vez | El usuario que quieras |
| `DJANGO_SUPERUSER_EMAIL` | Solo primera vez | Tu correo |
| `DJANGO_SUPERUSER_PASSWORD` | Solo primera vez | Tu contraseña |

---

## Soporte

Si algo falla, revisa primero los **Logs del deploy** en Railway (botón "View Logs" en el servicio web). Los errores más comunes y sus causas:

| Error en logs | Causa |
|---|---|
| `ImproperlyConfigured: DJANGO_SECRET_KEY is required` | Falta la variable `DJANGO_SECRET_KEY` |
| `ImproperlyConfigured: DATABASE_URL is required` | Falta o es incorrecta `DATABASE_URL` |
| `connection failed` / `Name or service not known` | `DATABASE_URL` incorrecta o DB no levantada |
| `ModuleNotFoundError` | Dependencia faltante en `requirements.txt` |
| Error 500 en página | Revisar logs de Gunicorn en Railway |
