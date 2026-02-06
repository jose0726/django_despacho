from django.contrib import admin
from .models import Proyecto, Contacto, ProyectoImagen, EquipoMiembro, EquipoSeccion


class ProyectoImagenInline(admin.TabularInline):
    model = ProyectoImagen
    extra = 1
    fields = ('imagen', 'orden')


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'subcategoria', 'fecha_creacion')
    search_fields = ('nombre', 'categoria', 'subcategoria')
    list_filter = ('categoria', 'subcategoria')
    inlines = [ProyectoImagenInline]


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