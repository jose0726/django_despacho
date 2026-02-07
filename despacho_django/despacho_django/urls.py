"""
URL configuration for despacho_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Railway/production safeguard:
# The repo root also contains a top-level `proyectos/` package which can shadow
# the real Django app living next to manage.py (despacho_django/proyectos).
# Ensure the project directory is first on sys.path before importing URLConfs.
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent
project_dir_str = str(PROJECT_DIR)
if project_dir_str not in sys.path:
    sys.path.insert(0, project_dir_str)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('proyectos.urls', 'proyectos'), namespace='proyectos')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
