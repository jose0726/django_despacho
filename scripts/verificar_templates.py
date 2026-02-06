#!/usr/bin/env python
"""Verificación de templates Django (dev)."""

import os
import sys
from pathlib import Path

import django
from django.template.loader import get_template


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    project_dir = root / "despacho_django"

    sys.path.insert(0, str(project_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "despacho_django.settings")
    django.setup()

    templates = ["base.html", "index.html", "proyectos.html", "contacto.html", "sobre-nosotros.html"]

    print("🔍 VERIFICACIÓN DE TEMPLATES DJANGO")
    print("=" * 50)

    for template_name in templates:
        try:
            get_template(template_name)
            print(f"✅ {template_name} - OK")
        except Exception as e:
            print(f"❌ {template_name} - ERROR: {e}")
            return 1

    print("\n✅ TODOS LOS TEMPLATES SE CARGAN CORRECTAMENTE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
