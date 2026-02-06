from django.urls import path
from .views_api import proyectos_list

urlpatterns = [
    path('api/proyectos/', proyectos_list, name='api_proyectos_list'),
]
