from django.contrib import admin
from .models import Proyecto, Contacto, ProyectoImagen, EquipoMiembro, EquipoSeccion, HomePageConfig


class ProyectoImagenInline(admin.TabularInline):
    model = ProyectoImagen
    extra = 1
    fields = ('imagen', 'orden')


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'subcategoria', 'tiene_modelo_3d', 'fecha_creacion')
    search_fields = ('nombre', 'categoria', 'subcategoria')
    list_filter = ('categoria', 'subcategoria')
    inlines = [ProyectoImagenInline]
    fieldsets = (
        ('Información general', {
            'fields': ('nombre', 'descripcion', 'categoria', 'subcategoria', 'imagen')
        }),
        ('Modelo 3D interactivo', {
            'fields': ('modelo_3d',),
            'description': 'Sube un archivo .glb o .gltf para habilitar el visor 3D en la página del proyecto.'
        }),
    )

    @admin.display(boolean=True, description='Modelo 3D')
    def tiene_modelo_3d(self, obj):
        return bool(obj.modelo_3d)


admin.site.register(Contacto)


@admin.register(EquipoMiembro)
class EquipoMiembroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rol', 'orden', 'activo')
    list_filter = ('rol', 'activo')
    search_fields = ('nombre',)
    list_editable = ('orden', 'activo')
    ordering = ('rol', 'orden', 'id')


@admin.register(EquipoSeccion)
class EquipoSeccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'activo', 'actualizado')
    list_editable = ('activo',)


@admin.register(HomePageConfig)
class HomePageConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'actualizado')
    fields = ('carcon_video_file', 'carcon_video_url', 'actualizado')
    readonly_fields = ('actualizado',)

    def has_add_permission(self, request):
        # Singleton: allow add only if none exists
        if HomePageConfig.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Avoid accidental removal in production
        return False