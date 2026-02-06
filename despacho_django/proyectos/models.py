from django.db import models


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
