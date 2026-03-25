# Prompt de Contexto — Proyecto de Titulación

## Datos del Estudiante
- **Nombre:** José (jose0726 en GitHub)
- **Proyecto:** Sitio web para **Estudio Carcon** (despacho de arquitectura)
- **Defensa intermedia:** Abril 2026
- **Defensa final:** Octubre 2026
- **Asesor:** Ezau

---

## Descripción General
Estoy desarrollando un sitio web profesional para un despacho de arquitectura llamado **Estudio/Despacho Carcon**, ubicado en Ixtapaluca, Estado de México. El sitio web sirve como portafolio digital para mostrar proyectos arquitectónicos (habitacionales, comerciales, paisajismo, interiores), permite contacto con clientes, y presenta al equipo del estudio.

**Lo que lo hace proyecto de tesis** es la integración de tecnología innovadora para la visualización de proyectos arquitectónicos, específicamente:

---

## Funcionalidades Innovadoras (Tesis)

### 1. Visualización 3D Interactiva de Proyectos (CORE — ya implementado)
- Visor 3D en el navegador usando **Three.js + WebGL**
- Carga modelos en formato **GLB/GLTF** subidos desde el admin
- Controles interactivos: rotar, zoom, pan con OrbitControls
- Campo `modelo_3d` (FileField) en el modelo Proyecto
- Template `detail.html` con canvas Three.js + GLTFLoader vía CDN
- Falta: probar con un archivo .glb real (se puede obtener de SketchUp Pro → export GLB, o AutoCAD → Blender → GLB, o Sketchfab para pruebas)

### 2. Solicitud de Cotización (pendiente de implementar)
- Formulario donde el cliente solicita una cotización para un proyecto
- El admin recibe la solicitud y puede responder
- NO es un sistema de precios automáticos, es solicitud → revisión → respuesta manual

### 3. Panel Administrativo Profesional + Analítica (pendiente de implementar)
- Dashboard personalizado extendiendo el admin de Django
- Estadísticas de proyectos, visitas, mensajes de contacto
- Tracking de visitas por proyecto

### Funcionalidades descartadas (demasiado complejas para el alcance):
- IA de recomendación de proyectos
- Simulador de diseño arquitectónico
- Chatbot inteligente
- Realidad Aumentada (WebXR no funciona en iOS Safari; el estudiante solo tiene iPhone + laptops Windows)

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Django 5.2.9 · Python 3.11.9 |
| Base de datos | SQLite (local) · PostgreSQL (producción) |
| Hosting | Railway |
| Almacenamiento media | Cloudinary (producción) · Local filesystem (desarrollo) |
| Emails | SendGrid (formulario de contacto) |
| Servidor producción | Gunicorn + WhiteNoise |
| Frontend | HTML/CSS/JS vanilla · Three.js (visor 3D) · FontAwesome |
| Animaciones | anime.min.js · IntersectionObserver (scroll animations) |
| 3D | Three.js + GLTFLoader + OrbitControls (CDN) |

---

## Estructura del Proyecto

```
django_despacho/
├── despacho_django/                 # Proyecto Django
│   ├── despacho_django/             # Configuración (settings.py, urls.py, wsgi.py)
│   ├── proyectos/                   # App principal
│   │   ├── models.py               # Proyecto, ProyectoImagen, Contacto, HomePageConfig, EquipoSeccion, EquipoMiembro
│   │   ├── views.py                # Vistas de páginas HTML
│   │   ├── views_api.py            # API JSON (proyectos paginados, contacto POST)
│   │   ├── admin.py                # Panel admin Django
│   │   ├── urls.py                 # Rutas
│   │   ├── migrations/             # Migraciones DB
│   │   └── templates/proyectos/    # list.html, detail.html (visor 3D aquí)
│   ├── templates/                   # Templates globales
│   │   ├── base.html               # Layout base con nav + footer
│   │   ├── index.html              # Homepage con video configurable
│   │   ├── proyectos.html          # Portafolio con filtros dinámicos (JS)
│   │   ├── contacto.html           # Formulario de contacto
│   │   └── sobre-nosotros.html     # Equipo, misión, visión, valores, ubicación
│   ├── static/                      # CSS, JS, imágenes, FontAwesome
│   │   ├── css/ (index.css, proyectos.css, styles.css)
│   │   └── js/ (app.js, proyectos.js, anime.min.js)
│   └── media/                       # Archivos subidos (local)
├── scripts/                         # Scripts utilitarios (importar proyectos, start Railway, etc.)
├── requirements.txt
├── Procfile / nixpacks.toml         # Config deploy Railway
└── .env                             # Variables de entorno (no en repo)
```

---

## Modelos de Datos

- **Proyecto**: nombre, descripcion, categoria, subcategoria, imagen (ImageField), modelo_3d (FileField GLB/GLTF), fecha_creacion
- **ProyectoImagen**: galería de imágenes por proyecto (FK a Proyecto, imagen, orden)
- **Contacto**: mensajes del formulario (nombre, email, mensaje, proyecto, fecha_envio)
- **HomePageConfig**: video de la homepage (archivo o URL YouTube)
- **EquipoSeccion**: imagen grupal del equipo
- **EquipoMiembro**: nombre, rol (arquitecto/colaborador), imagen, orden, activo

---

## Rutas del Sitio

| Ruta | Descripción |
|---|---|
| `/` | Homepage con video configurable |
| `/proyectos/` | Portafolio con filtrado por categoría/subcategoría (JS + API) |
| `/proyecto/<id>/` | Detalle de proyecto con visor 3D si tiene modelo_3d |
| `/contacto/` | Formulario de contacto |
| `/sobre-nosotros/` | Equipo, misión, visión, valores, ubicación con mapa |
| `/admin/` | Panel de administración Django |
| `/api/proyectos/` | API JSON paginada con filtros (categoria, sub, q, page, page_size) |
| `POST /contact/` | Endpoint del formulario de contacto |

---

## Seguridad Implementada
- CSRF activo en formularios y endpoints JSON
- Sanitización XSS en inputs del formulario
- Honeypot para detectar bots
- Whitelist de dominios de email (Gmail, Outlook, Yahoo, Proton, etc.)
- HTTPS + cookies seguras + HSTS en producción
- CORS configurado con django-cors-headers
- WhiteNoise para archivos estáticos con compresión y cache

---

## Estado Actual del Proyecto

### Completado ✅
- Sitio funcionando localmente y desplegado en Railway
- Todas las páginas públicas (home, proyectos, contacto, sobre nosotros)
- API JSON de proyectos con paginación y filtros
- Formulario de contacto con SendGrid
- Panel admin con gestión de proyectos, equipo, config homepage
- Visor 3D con Three.js implementado en template de detalle
- Campo modelo_3d en modelo Proyecto (migración aplicada)
- Script de importación de proyectos desde JSON
- Preloader animado con logo
- Scroll animations con IntersectionObserver

### Pendiente ⏳
- Probar visor 3D con archivo .glb real
- Formulario de solicitud de cotización
- Dashboard admin con analítica (visitas, estadísticas)
- Tracking de visitas por proyecto

---

## Entorno de Desarrollo
- **SO:** Windows
- **IDE:** VS Code
- **Python venv:** `.venv` en raíz del proyecto
- **Activar:** `.\.venv\Scripts\Activate.ps1`
- **Servidor local:** `python despacho_django\manage.py runserver` → http://localhost:8000
- **Directorio del proyecto:** la raíz donde está `requirements.txt` y `despacho_django/`

---

## Notas Importantes
- El proyecto usa Cloudinary en producción para persistir media entre deploys de Railway
- Sin Cloudinary, funciona local con filesystem
- Sin SendGrid, el formulario guarda en BD pero no envía emails
- El visor 3D usa CDN de Three.js (unpkg.com), no instalación local
- Los archivos 3D deben ser GLB o GLTF (formatos estándar de web 3D)
- Para obtener archivos GLB: SketchUp Pro exporta directo; AutoCAD necesita pasar por Blender; para pruebas se pueden descargar de Sketchfab
