#!/usr/bin/env python
"""Verifica que variables de entorno se cargan correctamente."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    project_dir = root / "despacho_django"

    sys.path.insert(0, str(project_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "despacho_django.settings")

    env_file = root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("✅ Archivo .env cargado correctamente")
    else:
        print("❌ Archivo .env no encontrado")

    import django

    django.setup()

    print("🔍 VERIFICACIÓN DE VARIABLES DE ENTORNO")
    print("=" * 50)

    print(f"📁 Archivo .env: {'✅ Existe' if env_file.exists() else '❌ No existe'}")
    print(f"   Ruta: {env_file}")

    variables = [
        "SENDGRID_API_KEY",
        "SENDGRID_FROM_EMAIL",
        "SENDGRID_TO_EMAIL",
        "DJANGO_SECRET_KEY",
        "DJANGO_DEBUG",
        "DJANGO_ALLOWED_HOSTS",
        "DATABASE_URL",
        "CLOUDINARY_URL",
        "CORS_ALLOWED_ORIGINS",
        "CSRF_TRUSTED_ORIGINS",
    ]

    print("\n🔧 Variables de entorno:")
    for var in variables:
        value = os.getenv(var)
        if value:
            if var == "SENDGRID_API_KEY":
                display_value = f"{value[:6]}...{value[-4:]}" if len(value) > 12 else value
            elif var in {"SENDGRID_FROM_EMAIL", "SENDGRID_TO_EMAIL"}:
                display_value = value
            elif var == "DJANGO_SECRET_KEY":
                display_value = f"{value[:6]}...{value[-4:]}" if len(value) > 12 else value
            elif var == "DATABASE_URL":
                display_value = f"{value[:18]}..." if len(value) > 18 else value
            elif var == "CLOUDINARY_URL":
                display_value = f"{value[:18]}..." if len(value) > 18 else value
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: No configurada")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
