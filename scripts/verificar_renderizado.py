#!/usr/bin/env python
"""Verifica que el template proyectos.html se renderiza sin errores (dev)."""

import os
import sys
from pathlib import Path

import django
from django.template.loader import render_to_string


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    project_dir = root / "despacho_django"

    sys.path.insert(0, str(project_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "despacho_django.settings")
    django.setup()

    print("🔍 VERIFICACIÓN DE RENDERIZADO DE PROYECTOS")
    print("=" * 50)

    try:
        html = render_to_string("proyectos.html")
        print("✅ Template proyectos.html se renderiza correctamente")

        checks = [
            ("Contenedor proyectos-filtrados", 'id="proyectos-filtrados"' in html),
            ("Clase proyectos-filtrados", 'class="proyectos-filtrados"' in html),
            ("Carga de proyectos.css", "css/proyectos.css" in html),
            ("Carga de proyectos.js", "js/proyectos.js" in html),
            ("API_BASE definido", "window.API_BASE" in html),
        ]

        for check_name, condition in checks:
            status = "✅" if condition else "❌"
            print(f"{status} {check_name}")

        if "TemplateSyntaxError" in html or "Invalid block tag" in html:
            print("❌ Hay errores de template en el HTML renderizado")
            return 1

        print("\n✅ VERIFICACIÓN COMPLETA")
        return 0

    except Exception as e:
        print(f"❌ Error al renderizar template: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
