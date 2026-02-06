from django.urls import path
from . import views
from .views_api import proyectos_list, contact_form

app_name = 'proyectos'

urlpatterns = [
    # Páginas públicas
    path('', views.index_page, name='index'),
    path('proyectos/', views.proyectos_page, name='proyectos_page'),
    path('contacto/', views.contacto_page, name='contacto_page'),
    path('sobre-nosotros/', views.sobre_nosotros_page, name='sobre_nosotros_page'),

    # Endpoints existentes
    path('proyecto/<int:pk>/', views.proyecto_detalle, name='proyecto_detalle'),
    path('api/proyectos/', proyectos_list, name='api_proyectos_list'),

    # Nuevo endpoint para formulario de contacto
    path('contact', contact_form, name='contact_form_noslash'),
    path('contact/', contact_form, name='contact_form'),

    # Ruta legacy para listado interno (no pública)
    path('proyectos/list/', views.index, name='proyectos_list_legacy'),
]
