#!/usr/bin/env python
"""Verificación completa de la carga de proyectos (dev)."""

import os
import sys
from pathlib import Path

import django


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    project_dir = root / "despacho_django"

    sys.path.insert(0, str(project_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "despacho_django.settings")
    django.setup()

    from proyectos.models import Proyecto

    print("🔍 VERIFICACIÓN DE CARGA DE PROYECTOS")
    print("=" * 50)

    total_proyectos = Proyecto.objects.count()
    print(f"📊 Proyectos en base de datos: {total_proyectos}")
    if total_proyectos == 0:
        print("❌ No hay proyectos en la base de datos")
        return 1

    proyectos_con_imagenes = Proyecto.objects.exclude(imagen="").count()
    proyectos_con_galeria = Proyecto.objects.filter(imagenes__isnull=False).distinct().count()

    print(f"🖼️  Proyectos con imagen principal: {proyectos_con_imagenes}")
    print(f"🎠 Proyectos con galería: {proyectos_con_galeria}")

    categorias = Proyecto.objects.values_list("categoria", flat=True).distinct()
    print(f"📂 Categorías encontradas: {list(categorias)}")

    from proyectos.views_api import proyectos_list
    from django.test import RequestFactory

    rf = RequestFactory()
    request = rf.get("/api/proyectos/?page_size=5")
    response = proyectos_list(request)
    print(f"🔗 API Response Status: {response.status_code}")

    if response.status_code == 200:
        import json

        data = json.loads(response.content)
        print(f"📄 API devuelve {data.get('count', 0)} proyectos")
        print(f"📋 Primeros resultados: {len(data.get('results', []))}")
        if data.get("results"):
            primer_proyecto = data["results"][0]
            print(f"🏗️  Primer proyecto: {primer_proyecto.get('nombre', 'Sin nombre')}")
            print(f"📸 Imágenes: {len(primer_proyecto.get('imagenes', []))}")

    static_dir = project_dir / "static"
    js_file = static_dir / "js" / "proyectos.js"
    css_file = static_dir / "css" / "proyectos.css"

    print(f"📜 proyectos.js existe: {js_file.exists()}")
    print(f"🎨 proyectos.css existe: {css_file.exists()}")

    from django.template.loader import get_template

    try:
        get_template("proyectos.html")
        print("✅ Template proyectos.html carga correctamente")
    except Exception as e:
        print(f"❌ Error en template: {e}")
        return 1

    print("\n✅ VERIFICACIÓN COMPLETA")
    print("Los proyectos deberían cargar correctamente ahora.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
