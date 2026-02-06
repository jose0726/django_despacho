#!/usr/bin/env python
"""Prueba de envío de email con SendGrid (dev)."""

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

    print("📧 PRUEBA DE ENVÍO DE EMAIL CON SENDGRID")
    print("=" * 50)

    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key or not api_key.startswith("SG."):
        print("❌ API Key de SendGrid no configurada correctamente")
        print("Configura SENDGRID_API_KEY en el archivo .env")
        return 1

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        sg = SendGridAPIClient(api_key)

        message = Mail(
            from_email="ccjose088@gmail.com",
            to_emails="ccjose088@gmail.com",
            subject="Prueba de SendGrid - Despacho Carcon",
            html_content=(
                "<h2>¡Prueba!</h2>"
                "<p>Este es un email de prueba enviado desde tu aplicación Django.</p>"
            ),
        )

        response = sg.send(message)
        print("✅ Email enviado exitosamente!")
        print(f"   Status Code: {response.status_code}")
        return 0

    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
