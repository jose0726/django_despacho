#!/usr/bin/env python
"""
Script para probar el envío de emails con SendGrid
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'despacho_django.settings')
django.setup()

def probar_sendgrid():
    """Prueba el envío de un email de prueba con SendGrid"""
    print("📧 PRUEBA DE ENVÍO DE EMAIL CON SENDGRID")
    print("=" * 50)

    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('SENDGRID_FROM_EMAIL')
    to_email = os.getenv('SENDGRID_TO_EMAIL')

    if not api_key or not api_key.startswith('SG.'):
        print("❌ API Key de SendGrid no configurada correctamente")
        print("Configura SENDGRID_API_KEY en el archivo .env")
        return

    if not from_email or not to_email:
        print("❌ Faltan emails de configuración")
        print("Configura SENDGRID_FROM_EMAIL y SENDGRID_TO_EMAIL en el archivo .env")
        return

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        sg = SendGridAPIClient(api_key)

        # Email de prueba
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject='Prueba de SendGrid - Despacho Carcon',
            html_content="""
            <h2>¡Prueba exitosa!</h2>
            <p>Este es un email de prueba enviado desde tu aplicación Django.</p>
            <p>Si recibes este email, SendGrid está configurado correctamente.</p>
            <br>
            <p>Atentamente,<br>Sistema de Despacho Carcon</p>
            """
        )

        response = sg.send(message)
        print(f"✅ Email enviado exitosamente!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Body: {response.body}")
        print(f"   Headers: {response.headers}")

    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        print("\nPosibles causas:")
        print("- API Key inválida")
        print("- Email 'from' no verificado en SendGrid")
        print("- Problemas de red")
        print("- Límites de envío excedidos")

if __name__ == "__main__":
    probar_sendgrid()