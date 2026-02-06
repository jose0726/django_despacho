from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage
from django.utils.html import escape
import json
import logging
import os
import re
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError
from .models import Proyecto, Contacto

logger = logging.getLogger(__name__)


def _validate_email(email):
    """Valida formato de email según RFC 5322 (simplificado)"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _sanitize_for_html(text):
    """Escapa caracteres HTML para prevenir inyección en email"""
    if not text:
        return ''
    # Primero escapa HTML, luego reemplaza saltos de línea con <br>
    escaped = escape(text)
    return escaped.replace('\n', '<br>')


def _sanitize_input(text, max_length=None):
    """Limpia y valida un input de usuario"""
    if not text:
        return ''
    # Trim espacios
    text = text.strip()
    # Si tiene límite de largo, aplicarlo
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text

def proyectos_list(request):
    # prefetch_related evita N+1 queries al acceder a p.imagenes.all()
    qs = Proyecto.objects.all().prefetch_related('imagenes').order_by('-fecha_creacion')

    # Filters
    categoria = request.GET.get('categoria')
    sub = request.GET.get('sub')
    q = request.GET.get('q')

    if categoria:
        qs = qs.filter(categoria__iexact=categoria)
    if sub:
        qs = qs.filter(subcategoria__iexact=sub)
    if q:
        qs = qs.filter(nombre__icontains=q)

    # Pagination
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 12))
    except ValueError:
        page, page_size = 1, 12

    paginator = Paginator(qs, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    results = []
    for p in page_obj.object_list:
        # Construir array de imágenes desde la relación ProyectoImagen
        imagenes = []
        for img in p.imagenes.all():
            if img.imagen:
                try:
                    img_url = request.build_absolute_uri(img.imagen.url)
                except Exception:
                    img_url = img.imagen.url
                imagenes.append({'imagen': img_url})
        
        # Fallback: si no hay imágenes en la galería, usar campo principal si existe
        if not imagenes and p.imagen:
            try:
                img_url = request.build_absolute_uri(p.imagen.url)
            except Exception:
                img_url = p.imagen.url
            imagenes.append({'imagen': img_url})
        
        results.append({
            'id': p.id,
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'categoria': p.categoria,
            'subcategoria': p.subcategoria,
            'imagenes': imagenes,  # ahora devuelve array
            'fecha_creacion': p.fecha_creacion.isoformat(),
        })

    return JsonResponse({
        'count': paginator.count,
        'page': page_obj.number,
        'pages': paginator.num_pages,
        'page_size': page_size,
        'results': results,
    })

def contact_form(request):
    """Vista para manejar el envío del formulario de contacto con SendGrid"""
    if request.method != 'POST':
        return JsonResponse(
            {'ok': False, 'error': 'Method not allowed. Use POST.'},
            status=405,
        )

    try:
        data = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON.'}, status=400)

    # Limpiar y validar inputs
    nombre = _sanitize_input(data.get('nombre', ''), max_length=100)
    correo = _sanitize_input(data.get('correo', ''), max_length=254)
    mensaje = _sanitize_input(data.get('mensaje', ''), max_length=5000)
    proyecto = _sanitize_input(data.get('proyecto', ''), max_length=100)
    hp = _sanitize_input(data.get('hp', ''))

    # Honeypot simple: si viene lleno, tratamos como spam.
    if hp:
        logger.warning("Contacto bloqueado por honeypot (hp no vacío)")
        return JsonResponse({'ok': False, 'error': 'Solicitud inválida.'}, status=400)

    # Validar campos requeridos
    if not nombre or not correo or not mensaje:
        return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios.'}, status=400)

    # Validar formato de email
    if not _validate_email(correo):
        return JsonResponse({'ok': False, 'error': 'Email inválido.'}, status=400)

    # Guardar en DB (con datos sin sanitizar para preservar mensaje original)
    try:
        Contacto.objects.create(
            nombre=nombre,
            email=correo,
            mensaje=mensaje,
            proyecto=proyecto,
        )
    except Exception:
        logger.exception("Error guardando Contacto en DB")
        return JsonResponse({'ok': False, 'error': 'Error guardando el mensaje.'}, status=500)

    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    if not sendgrid_api_key:
        logger.error("SENDGRID_API_KEY no configurada")
        # Si el mensaje ya se guardó en DB, retornar OK (graceful degradation)
        logger.info(f"Contacto guardado sin envío de email: {nombre} ({correo})")
        return JsonResponse({
            'ok': True,
            'message': 'Mensaje guardado. Email podría no haber sido enviado.',
            'email_sent': False,
        }, status=200)

    try:
        sg = SendGridAPIClient(sendgrid_api_key)

        sendgrid_from_email = os.getenv('SENDGRID_FROM_EMAIL')
        sendgrid_to_email = os.getenv('SENDGRID_TO_EMAIL')
        if not sendgrid_from_email or not sendgrid_to_email:
            logger.error("SENDGRID_FROM_EMAIL / SENDGRID_TO_EMAIL no configurados")
            logger.info(f"Contacto guardado sin envío de email (config incompleta): {nombre} ({correo})")
            return JsonResponse({
                'ok': True,
                'message': 'Mensaje guardado. Email podría no haber sido enviado.',
                'email_sent': False,
            }, status=200)

        # Sanitizar inputs para HTML (previene XSS/injection)
        nombre_safe = _sanitize_for_html(nombre)
        correo_safe = _sanitize_for_html(correo)
        proyecto_safe = _sanitize_for_html(proyecto) or 'No especificado'
        mensaje_safe = _sanitize_for_html(mensaje)

        admin_email = Mail(
            from_email=sendgrid_from_email,
            to_emails=sendgrid_to_email,
            subject=f'Nuevo mensaje de contacto: {nombre}',
            html_content=f"""
                        <!doctype html>
                        <html lang="es">
                            <head>
                                <meta charset="utf-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1">
                                <meta name="x-apple-disable-message-reformatting">
                                <title>Nuevo mensaje de contacto</title>
                            </head>
                            <body style="margin:0; padding:0; background-color:#f6f6f6;">
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#f6f6f6;">
                                    <tr>
                                        <td align="center" style="padding:20px 12px;">

                                            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="width:600px; max-width:600px; background-color:#ffffff; border:1px solid #e6e6e6;">
                                                <tr>
                                                    <td style="padding:18px 20px 10px; font-family:Arial, Helvetica, sans-serif;">
                                                        <div style="font-size:14px; letter-spacing:0.12em; text-transform:uppercase; color:#666;">Despacho Carcon</div>
                                                        <div style="font-size:22px; line-height:28px; color:#111; font-weight:bold; margin-top:6px;">Nuevo mensaje de contacto</div>
                                                    </td>
                                                </tr>

                                                <tr>
                                                    <td style="padding:0 20px 18px; font-family:Arial, Helvetica, sans-serif;">
                                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-top:1px solid #ededed;">
                                                            <tr>
                                                                <td style="padding-top:14px;">
                                                                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;">
                                                                        <tr>
                                                                            <td style="padding:10px 12px; background:#fafafa; border:1px solid #ededed; font-family:Arial, Helvetica, sans-serif; font-size:13px; color:#444; width:160px;">Nombre</td>
                                                                            <td style="padding:10px 12px; border:1px solid #ededed; font-family:Arial, Helvetica, sans-serif; font-size:13px; color:#111;">{nombre_safe}</td>
                                                                        </tr>
                                                                        <tr>
                                                                            <td style="padding:10px 12px; background:#fafafa; border:1px solid #ededed; font-family:Arial, Helvetica, sans-serif; font-size:13px; color:#444;">Email</td>
                                                                            <td style="padding:10px 12px; border:1px solid #ededed; font-family:Arial, Helvetica, sans-serif; font-size:13px; color:#111;">{correo_safe}</td>
                                                                        </tr>
                                                                        <tr>
                                                                            <td style="padding:10px 12px; background:#fafafa; border:1px solid #ededed; font-family:Arial, Helvetica, sans-serif; font-size:13px; color:#444;">Proyecto</td>
                                                                            <td style="padding:10px 12px; border:1px solid #ededed; font-family:Arial, Helvetica, sans-serif; font-size:13px; color:#111;">{proyecto_safe}</td>
                                                                        </tr>
                                                                    </table>
                                                                </td>
                                                            </tr>

                                                            <tr>
                                                                <td style="padding-top:16px; font-family:Arial, Helvetica, sans-serif;">
                                                                    <div style="font-size:13px; letter-spacing:0.10em; text-transform:uppercase; color:#666;">Mensaje</div>
                                                                    <div style="margin-top:8px; padding:14px 14px; background:#ffffff; border:1px solid #e6e6e6; font-size:14px; line-height:20px; color:#111; mso-line-height-rule:exactly;">
                                                                        {mensaje_safe}
                                                                    </div>
                                                                </td>
                                                            </tr>

                                                            <tr>
                                                                <td style="padding-top:16px; font-family:Arial, Helvetica, sans-serif; font-size:12px; line-height:18px; color:#777; mso-line-height-rule:exactly;">
                                                                    Recibido desde el formulario del sitio.
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </table>

                                            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="width:600px; max-width:600px;">
                                                <tr>
                                                    <td style="padding:10px 8px; font-family:Arial, Helvetica, sans-serif; font-size:11px; line-height:16px; color:#888; text-align:center;">
                                                        © 2025 Despacho Carcon
                                                    </td>
                                                </tr>
                                            </table>

                                        </td>
                                    </tr>
                                </table>
                            </body>
                        </html>
            """,
        )

        confirmation_email = Mail(
            from_email=sendgrid_from_email,
            to_emails=correo,
            subject='Hemos recibido tu mensaje - Estudio Carcon',
            html_content=f"""
                        <!doctype html>
                        <html lang="es">
                            <head>
                                <meta charset="utf-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1">
                                <meta name="x-apple-disable-message-reformatting">
                                <title>Confirmación de contacto</title>
                            </head>
                            <body style="margin:0; padding:0; background-color:#f6f6f6;">
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#f6f6f6;">
                                    <tr>
                                        <td align="center" style="padding:20px 12px;">

                                            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="width:600px; max-width:600px; background-color:#ffffff; border:1px solid #e6e6e6;">
                                                <tr>
                                                    <td style="padding:18px 20px 10px; font-family:Arial, Helvetica, sans-serif;">
                                                        <div style="font-size:14px; letter-spacing:0.12em; text-transform:uppercase; color:#666;">Estudio Carcon</div>
                                                        <div style="font-size:22px; line-height:28px; color:#111; font-weight:bold; margin-top:6px;">Hemos recibido tu mensaje</div>
                                                    </td>
                                                </tr>

                                                <tr>
                                                    <td style="padding:0 20px 18px; font-family:Arial, Helvetica, sans-serif;">
                                                        <div style="border-top:1px solid #ededed; padding-top:14px;">
                                                            <p style="margin:0; font-size:14px; line-height:20px; color:#111; mso-line-height-rule:exactly;">Hola {nombre_safe},</p>
                                                            <p style="margin:10px 0 0; font-size:14px; line-height:20px; color:#444; mso-line-height-rule:exactly;">
                                                                Gracias por escribirnos. Hemos recibido tu mensaje y te responderemos lo antes posible.
                                                            </p>

                                                            <div style="margin-top:16px; font-size:13px; letter-spacing:0.10em; text-transform:uppercase; color:#666;">Resumen</div>
                                                            <div style="margin-top:8px; padding:14px 14px; background:#ffffff; border:1px solid #e6e6e6; font-size:14px; line-height:20px; color:#111; mso-line-height-rule:exactly;">
                                                                {mensaje_safe}
                                                            </div>

                                                            <p style="margin:16px 0 0; font-size:14px; line-height:20px; color:#444; mso-line-height-rule:exactly;">
                                                                Atentamente,<br>
                                                                <span style="color:#111; font-weight:bold;">Equipo de Estudio Carcon</span>
                                                            </p>
                                                        </div>
                                                    </td>
                                                </tr>
                                            </table>

                                            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="width:600px; max-width:600px;">
                                                <tr>
                                                    <td style="padding:10px 8px; font-family:Arial, Helvetica, sans-serif; font-size:11px; line-height:16px; color:#888; text-align:center;">
                                                        Si no reconoces este mensaje, puedes ignorarlo.
                                                    </td>
                                                </tr>
                                            </table>

                                        </td>
                                    </tr>
                                </table>
                            </body>
                        </html>
            """,
        )

        admin_resp = sg.send(admin_email)
        confirm_resp = sg.send(confirmation_email)
        logger.info(
            "SendGrid OK admin=%s confirm=%s",
            getattr(admin_resp, 'status_code', None),
            getattr(confirm_resp, 'status_code', None),
        )
        return JsonResponse({'ok': True, 'message': 'Mensaje enviado correctamente.', 'email_sent': True})

    except HTTPError as e:
        status_code = getattr(e, 'status_code', None)
        body = getattr(e, 'body', None)
        headers = getattr(e, 'headers', None)
        logger.error(
            "SendGrid HTTPError status=%s body=%r headers=%r",
            status_code,
            body,
            headers,
            exc_info=True,
        )

        debug_details = None
        if getattr(settings, 'DEBUG', False):
            try:
                if isinstance(body, (bytes, bytearray)):
                    body_text = body.decode('utf-8', errors='replace')
                else:
                    body_text = str(body)
            except Exception:
                body_text = repr(body)
            debug_details = {
                'sendgrid_status': status_code,
                'sendgrid_body': (body_text or '')[:1000],
            }

        # Graceful degradation: mensaje guardado, pero email falló
        logger.warning(f"Contacto guardado pero email no enviado: {nombre} ({correo})")
        payload = {
            'ok': True,
            'message': 'Mensaje guardado. Email podría no haber sido enviado.',
            'email_sent': False,
        }
        if debug_details:
            payload['debug'] = debug_details

        return JsonResponse(payload, status=200)

    except Exception:
        logger.exception("Error inesperado enviando email con SendGrid")

        # Graceful degradation: mensaje guardado, pero email falló
        logger.warning(f"Contacto guardado pero error en email: {nombre} ({correo})")
        payload = {
            'ok': True,
            'message': 'Mensaje guardado. Email podría no haber sido enviado.',
            'email_sent': False,
        }
        if getattr(settings, 'DEBUG', False):
            import sys

            exc_type, exc, _tb = sys.exc_info()
            payload['debug'] = {
                'exception_type': getattr(exc_type, '__name__', str(exc_type)),
                'exception': repr(exc),
                'hint': 'Si ves SSLCertVerificationError, configura SSL_CERT_FILE en .env con el CA bundle correcto (proxy/antivirus).',
            }

        return JsonResponse(payload, status=200)
