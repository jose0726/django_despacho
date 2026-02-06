from django.http import JsonResponse
from proyectos.models import Proyecto


def proyectos_list(request):
    """Devuelve lista de proyectos en el formato esperado por el frontend.

    Cada proyecto tendrá las claves que usa el JS original:
    - titulo (desde nombre)
    - descripcion
    - categoria
    - sub (desde subcategoria)
    - imagenes (lista con la ruta en 'imagen')
    - id
    - fecha_creacion si está disponible
    """
    qs = Proyecto.objects.all().order_by('-id')
    result = []
    for p in qs:
        item = {
            'id': p.id,
            'titulo': getattr(p, 'nombre', '') or '',
            'descripcion': getattr(p, 'descripcion', '') or '',
            'categoria': getattr(p, 'categoria', '') or '',
            'sub': getattr(p, 'subcategoria', '') or '',
            'imagenes': [getattr(p, 'imagen', '')] if getattr(p, 'imagen', '') else [],
        }
        # incluir fecha de creación si el modelo la tiene
        if hasattr(p, 'fecha_creacion'):
            item['fecha_creacion'] = p.fecha_creacion
        result.append(item)
    return JsonResponse(result, safe=False)
