from django.db import models


class HomePageConfig(models.Model):
    """Configuración de la página de inicio (contenido global).

    Por ahora solo incluye el video de la promo (Carcon).
    Puede ser:
      - un archivo subido (mp4/webm) o
      - una URL (YouTube/Vimeo/MP4 URL)
    """

    carcon_video_file = models.FileField(
        upload_to='videos/',
        blank=True,
        null=True,
        help_text='Sube un video (mp4/webm). Si existe, se usa este en lugar de la URL.',
    )
    carcon_video_url = models.URLField(
        blank=True,
        help_text='URL del video. Para YouTube puedes pegar link normal o embed.',
    )
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de Inicio'
        verbose_name_plural = 'Configuración de Inicio'

    def __str__(self) -> str:
        return 'Configuración de Inicio'

    @staticmethod
    def _youtube_embed(url: str) -> str:
        """Return a YouTube embed URL for common YouTube URL formats."""

        raw = (url or '').strip()
        if not raw:
            return ''
        if 'youtube.com/embed/' in raw:
            return raw

        # Common formats:
        # - https://youtu.be/<id>
        # - https://www.youtube.com/watch?v=<id>
        video_id = ''
        if 'youtu.be/' in raw:
            video_id = raw.split('youtu.be/', 1)[1].split('?', 1)[0].split('&', 1)[0]
        elif 'youtube.com/watch' in raw and 'v=' in raw:
            video_id = raw.split('v=', 1)[1].split('&', 1)[0]

        if video_id:
            return f'https://www.youtube.com/embed/{video_id}'
        return raw

    def carcon_video_embed_url(self) -> str:
        return self._youtube_embed(self.carcon_video_url)


class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100)
    subcategoria = models.CharField(max_length=100, blank=True)
    imagen = models.ImageField(upload_to='proyectos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class ProyectoImagen(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='proyectos/')
    orden = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return f"{self.proyecto.nombre} - imagen {self.id}"


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    proyecto = models.CharField(max_length=200, blank=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.email}"


class EquipoSeccion(models.Model):
    """Configuración de la sección Equipo (imagen grupal)."""
    imagen_grupal = models.ImageField(upload_to='equipo/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sección Equipo"
        verbose_name_plural = "Sección Equipo"

    def __str__(self):
        return "Sección Equipo"


class EquipoMiembro(models.Model):
    """Miembros del equipo para la sección Sobre Nosotros."""
    ROL_ARQUITECTO = 'arquitecto'
    ROL_COLABORADOR = 'colaborador'
    ROL_CHOICES = [
        (ROL_ARQUITECTO, 'Arquitecto'),
        (ROL_COLABORADOR, 'Colaborador'),
    ]

    nombre = models.CharField(max_length=120)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    imagen = models.ImageField(upload_to='equipo/', blank=True, null=True)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['rol', 'orden', 'id']
        verbose_name = "Miembro del equipo"
        verbose_name_plural = "Miembros del equipo"

    def __str__(self):
        return self.nombre
