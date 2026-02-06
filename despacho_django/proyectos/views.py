from django.shortcuts import render, get_object_or_404
from .models import Proyecto, EquipoMiembro, EquipoSeccion

# Vista legacy de listado interno (mantener por compatibilidad interna)
def index(request):
	proyectos = Proyecto.objects.all().order_by('-fecha_creacion')
	return render(request, 'proyectos/list.html', {'proyectos': proyectos})

def proyecto_detalle(request, pk):
	proyecto = get_object_or_404(Proyecto, pk=pk)
	return render(request, 'proyectos/detail.html', {'proyecto': proyecto})

# Nuevas vistas de páginas públicas (usar templates del proyecto)
def index_page(request):
	"""Página principal. Renderiza templates/index.html"""
	return render(request, 'index.html')

def proyectos_page(request):
	"""Página de proyectos (frontend). Renderiza templates/proyectos.html"""
	return render(request, 'proyectos.html')

def contacto_page(request):
	"""Página de contacto. Renderiza templates/contacto.html"""
	return render(request, 'contacto.html')

def sobre_nosotros_page(request):
	"""Página sobre nosotros. Renderiza templates/sobre-nosotros.html"""
	equipo_config = (
		EquipoSeccion.objects.filter(activo=True)
		.order_by('-actualizado')
		.first()
	)
	miembros = EquipoMiembro.objects.filter(activo=True).order_by('rol', 'orden', 'id')
	arquitectos = miembros.filter(rol=EquipoMiembro.ROL_ARQUITECTO)
	colaboradores = miembros.filter(rol=EquipoMiembro.ROL_COLABORADOR)
	return render(
		request,
		'sobre-nosotros.html',
		{
			'equipo_config': equipo_config,
			'arquitectos': arquitectos,
			'colaboradores': colaboradores,
		},
	)
