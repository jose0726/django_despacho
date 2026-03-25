#!/usr/bin/env python
"""Verifica configuración básica de SendGrid (dev)."""

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

    print("🔍 VERIFICACIÓN DE SENDGRID")
    print("=" * 40)

    api_key = os.getenv("SENDGRID_API_KEY")
    if api_key and api_key.startswith("SG."):
        print("✅ SENDGRID_API_KEY configurada (formato básico OK)")
    else:
        print("❌ SENDGRID_API_KEY no configurada o inválida")

    try:
        from sendgrid import SendGridAPIClient  # noqa: F401

        print("✅ Librería SendGrid instalada")
    except ImportError:
        print("❌ Librería SendGrid no instalada")
        return 1

    from django.urls import reverse

    try:
        url = reverse("proyectos:contact_form")
        print(f"✅ URL del formulario configurada: {url}")
    except Exception:
        print("❌ URL del formulario no encontrada")

    try:
        from proyectos.views_api import contact_form  # noqa: F401

        print("✅ Vista contact_form importada correctamente")
    except ImportError:
        print("❌ Vista contact_form no encontrada")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
