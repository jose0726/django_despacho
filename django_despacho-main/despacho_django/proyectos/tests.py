"""
Tests para la app 'proyectos' — Estudio Carcon.

Cubre:
  • Modelos       (creación, str, relaciones, helpers)
  • Vistas HTML   (páginas públicas devuelven 200)
  • API proyectos (GET /api/proyectos/ con filtros y paginación)
  • Contacto      (POST /contact/ — validación, honeypot, email whitelist)
  • Seguridad     (CSRF, sanitización XSS)
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from .models import (
    Proyecto,
    ProyectoImagen,
    Contacto,
    HomePageConfig,
    EquipoSeccion,
    EquipoMiembro,
)


# ═══════════════════════════════════════════════════════════════
#  MODELOS
# ═══════════════════════════════════════════════════════════════


class ProyectoModelTest(TestCase):
    """Tests del modelo Proyecto."""

    def setUp(self):
        self.proyecto = Proyecto.objects.create(
            nombre='Casa Moderna',
            descripcion='Proyecto residencial de prueba',
            categoria='habitacional',
            subcategoria='residencial',
        )

    def test_str(self):
        self.assertEqual(str(self.proyecto), 'Casa Moderna')

    def test_campos_basicos(self):
        self.assertEqual(self.proyecto.categoria, 'habitacional')
        self.assertEqual(self.proyecto.subcategoria, 'residencial')
        self.assertIsNotNone(self.proyecto.fecha_creacion)

    def test_imagen_opcional(self):
        """imagen y modelo_3d pueden estar vacíos."""
        self.assertFalse(self.proyecto.imagen)
        self.assertFalse(self.proyecto.modelo_3d)

    def test_modelo_3d_field(self):
        """Se puede asignar un archivo modelo_3d."""
        self.proyecto.modelo_3d = 'modelos3d/test.glb'
        self.proyecto.save()
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.modelo_3d.name, 'modelos3d/test.glb')


class ProyectoImagenModelTest(TestCase):
    """Tests del modelo ProyectoImagen (galería)."""

    def setUp(self):
        self.proyecto = Proyecto.objects.create(
            nombre='Oficina',
            descripcion='Proyecto comercial',
            categoria='comercial',
        )
        # Crear imagen de prueba (1x1 pixel PNG transparente)
        self.tiny_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
            b'\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def test_crear_imagen(self):
        img_file = SimpleUploadedFile('test.png', self.tiny_png, content_type='image/png')
        img = ProyectoImagen.objects.create(
            proyecto=self.proyecto,
            imagen=img_file,
            orden=1,
        )
        self.assertEqual(img.proyecto, self.proyecto)
        self.assertEqual(img.orden, 1)
        self.assertIn('test', img.imagen.name)

    def test_str(self):
        img_file = SimpleUploadedFile('test.png', self.tiny_png, content_type='image/png')
        img = ProyectoImagen.objects.create(
            proyecto=self.proyecto,
            imagen=img_file,
        )
        self.assertIn('Oficina', str(img))

    def test_ordering(self):
        """Las imágenes se ordenan por 'orden' y luego 'id'."""
        img1 = SimpleUploadedFile('a.png', self.tiny_png, content_type='image/png')
        img2 = SimpleUploadedFile('b.png', self.tiny_png, content_type='image/png')

        ProyectoImagen.objects.create(proyecto=self.proyecto, imagen=img1, orden=2)
        ProyectoImagen.objects.create(proyecto=self.proyecto, imagen=img2, orden=1)

        imgs = list(self.proyecto.imagenes.all())
        self.assertEqual(imgs[0].orden, 1)
        self.assertEqual(imgs[1].orden, 2)

    def test_cascade_delete(self):
        """Al eliminar un proyecto, se eliminan sus imágenes."""
        img_file = SimpleUploadedFile('test.png', self.tiny_png, content_type='image/png')
        ProyectoImagen.objects.create(proyecto=self.proyecto, imagen=img_file)
        self.assertEqual(ProyectoImagen.objects.count(), 1)
        self.proyecto.delete()
        self.assertEqual(ProyectoImagen.objects.count(), 0)


class ContactoModelTest(TestCase):
    """Tests del modelo Contacto."""

    def test_crear_contacto(self):
        c = Contacto.objects.create(
            nombre='Juan Pérez',
            email='juan@gmail.com',
            mensaje='Quiero una cotización',
            proyecto='Casa en Ixtapaluca',
        )
        self.assertEqual(str(c), 'Juan Pérez - juan@gmail.com')
        self.assertIsNotNone(c.fecha_envio)

    def test_proyecto_opcional(self):
        c = Contacto.objects.create(
            nombre='Ana',
            email='ana@outlook.com',
            mensaje='Consulta general',
        )
        self.assertEqual(c.proyecto, '')


class HomePageConfigModelTest(TestCase):
    """Tests del modelo HomePageConfig."""

    def test_str(self):
        config = HomePageConfig.objects.create()
        self.assertEqual(str(config), 'Configuración de Inicio')

    def test_youtube_embed_normal(self):
        config = HomePageConfig.objects.create(
            carcon_video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )
        self.assertEqual(
            config.carcon_video_embed_url(),
            'https://www.youtube.com/embed/dQw4w9WgXcQ',
        )

    def test_youtube_embed_short(self):
        config = HomePageConfig.objects.create(
            carcon_video_url='https://youtu.be/dQw4w9WgXcQ'
        )
        self.assertEqual(
            config.carcon_video_embed_url(),
            'https://www.youtube.com/embed/dQw4w9WgXcQ',
        )

    def test_youtube_embed_already_embed(self):
        url = 'https://www.youtube.com/embed/dQw4w9WgXcQ'
        config = HomePageConfig.objects.create(carcon_video_url=url)
        self.assertEqual(config.carcon_video_embed_url(), url)

    def test_youtube_embed_empty(self):
        config = HomePageConfig.objects.create(carcon_video_url='')
        self.assertEqual(config.carcon_video_embed_url(), '')

    def test_non_youtube_url_passthrough(self):
        url = 'https://example.com/video.mp4'
        config = HomePageConfig.objects.create(carcon_video_url=url)
        self.assertEqual(config.carcon_video_embed_url(), url)


class EquipoModelTest(TestCase):
    """Tests de EquipoSeccion y EquipoMiembro."""

    def test_seccion_str(self):
        sec = EquipoSeccion.objects.create()
        self.assertEqual(str(sec), 'Sección Equipo')

    def test_miembro_str(self):
        m = EquipoMiembro.objects.create(
            nombre='Arq. García',
            rol=EquipoMiembro.ROL_ARQUITECTO,
        )
        self.assertEqual(str(m), 'Arq. García')

    def test_miembro_ordering(self):
        """Arquitectos antes de colaboradores, luego por orden."""
        EquipoMiembro.objects.create(nombre='Colab B', rol='colaborador', orden=1)
        EquipoMiembro.objects.create(nombre='Arq A', rol='arquitecto', orden=2)
        EquipoMiembro.objects.create(nombre='Arq C', rol='arquitecto', orden=1)

        nombres = list(EquipoMiembro.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, ['Arq C', 'Arq A', 'Colab B'])

    def test_miembro_activo_default(self):
        m = EquipoMiembro.objects.create(nombre='Test', rol='arquitecto')
        self.assertTrue(m.activo)

    def test_filter_activos(self):
        EquipoMiembro.objects.create(nombre='Activo', rol='arquitecto', activo=True)
        EquipoMiembro.objects.create(nombre='Inactivo', rol='colaborador', activo=False)
        activos = EquipoMiembro.objects.filter(activo=True)
        self.assertEqual(activos.count(), 1)
        self.assertEqual(activos.first().nombre, 'Activo')


# ═══════════════════════════════════════════════════════════════
#  VISTAS HTML (páginas públicas)
# ═══════════════════════════════════════════════════════════════


class VistasPublicasTest(TestCase):
    """Verifica que las páginas públicas responden HTTP 200."""

    def test_index(self):
        resp = self.client.get(reverse('proyectos:index'))
        self.assertEqual(resp.status_code, 200)

    def test_proyectos_page(self):
        resp = self.client.get(reverse('proyectos:proyectos_page'))
        self.assertEqual(resp.status_code, 200)

    def test_contacto_page(self):
        resp = self.client.get(reverse('proyectos:contacto_page'))
        self.assertEqual(resp.status_code, 200)

    def test_sobre_nosotros_page(self):
        resp = self.client.get(reverse('proyectos:sobre_nosotros_page'))
        self.assertEqual(resp.status_code, 200)

    def test_proyecto_detalle(self):
        p = Proyecto.objects.create(
            nombre='Test', descripcion='Desc', categoria='test'
        )
        resp = self.client.get(reverse('proyectos:proyecto_detalle', args=[p.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test')

    def test_proyecto_detalle_404(self):
        resp = self.client.get(reverse('proyectos:proyecto_detalle', args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_detalle_con_modelo_3d(self):
        """Si un proyecto tiene modelo_3d, el template muestra el visor."""
        p = Proyecto.objects.create(
            nombre='Casa 3D',
            descripcion='Con visor',
            categoria='habitacional',
            modelo_3d='modelos3d/test.glb',
        )
        resp = self.client.get(reverse('proyectos:proyecto_detalle', args=[p.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Modelo 3D interactivo')
        self.assertContains(resp, 'visor-3d')

    def test_detalle_sin_modelo_3d(self):
        """Sin modelo_3d, no debe aparecer el visor."""
        p = Proyecto.objects.create(
            nombre='Sin 3D', descripcion='Desc', categoria='test'
        )
        resp = self.client.get(reverse('proyectos:proyecto_detalle', args=[p.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Modelo 3D interactivo')

    def test_sobre_nosotros_con_equipo(self):
        """Página sobre nosotros muestra miembros activos."""
        EquipoMiembro.objects.create(nombre='Arq. Test', rol='arquitecto')
        resp = self.client.get(reverse('proyectos:sobre_nosotros_page'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Arq. Test')


# ═══════════════════════════════════════════════════════════════
#  API DE PROYECTOS (GET /api/proyectos/)
# ═══════════════════════════════════════════════════════════════


class ApiProyectosTest(TestCase):
    """Tests de la API JSON de listado de proyectos."""

    @classmethod
    def setUpTestData(cls):
        # Crear proyectos de prueba
        for i in range(15):
            Proyecto.objects.create(
                nombre=f'Proyecto {i}',
                descripcion=f'Descripción {i}',
                categoria='habitacional' if i < 10 else 'comercial',
                subcategoria='residencial' if i < 5 else 'oficinas',
            )

    def _get_json(self, params=''):
        url = reverse('proyectos:api_proyectos_list')
        resp = self.client.get(f'{url}?{params}' if params else url)
        self.assertEqual(resp.status_code, 200)
        return resp.json()

    def test_respuesta_basica(self):
        data = self._get_json()
        self.assertIn('count', data)
        self.assertIn('results', data)
        self.assertIn('page', data)
        self.assertIn('pages', data)
        self.assertEqual(data['count'], 15)

    def test_paginacion_default(self):
        """Por defecto page_size=12, así que hay 2 páginas."""
        data = self._get_json()
        self.assertEqual(len(data['results']), 12)
        self.assertEqual(data['pages'], 2)

    def test_paginacion_custom(self):
        data = self._get_json('page_size=5&page=2')
        self.assertEqual(len(data['results']), 5)
        self.assertEqual(data['page'], 2)

    def test_paginacion_max(self):
        """page_size no puede exceder 100."""
        data = self._get_json('page_size=200')
        self.assertEqual(data['page_size'], 100)

    def test_filtro_categoria(self):
        data = self._get_json('categoria=comercial')
        self.assertEqual(data['count'], 5)
        for r in data['results']:
            self.assertEqual(r['categoria'], 'comercial')

    def test_filtro_subcategoria(self):
        data = self._get_json('sub=residencial')
        self.assertEqual(data['count'], 5)

    def test_filtro_busqueda(self):
        data = self._get_json('q=Proyecto 1')
        # Matches: "Proyecto 1", "Proyecto 10"..."Proyecto 14"
        self.assertGreaterEqual(data['count'], 1)

    def test_filtros_combinados(self):
        data = self._get_json('categoria=habitacional&sub=residencial')
        self.assertEqual(data['count'], 5)

    def test_resultado_tiene_campos(self):
        data = self._get_json('page_size=1')
        result = data['results'][0]
        self.assertIn('id', result)
        self.assertIn('nombre', result)
        self.assertIn('descripcion', result)
        self.assertIn('categoria', result)
        self.assertIn('subcategoria', result)
        self.assertIn('imagenes', result)
        self.assertIn('fecha_creacion', result)

    def test_page_invalido(self):
        """Páginas inválidas van a la última página."""
        data = self._get_json('page=999')
        self.assertEqual(data['page'], data['pages'])

    def test_page_size_invalido(self):
        """page_size no numérico usa default."""
        data = self._get_json('page_size=abc')
        self.assertEqual(data['page_size'], 12)


# ═══════════════════════════════════════════════════════════════
#  ENDPOINT DE CONTACTO (POST /contact/)
# ═══════════════════════════════════════════════════════════════


@override_settings(DEBUG=True)
class ContactFormTest(TestCase):
    """Tests del endpoint POST /contact/."""

    def setUp(self):
        self.url = reverse('proyectos:contact_form')
        self.valid_data = {
            'nombre': 'Juan Pérez',
            'correo': 'juan@gmail.com',
            'mensaje': 'Me interesa un proyecto de remodelación.',
            'proyecto': 'Casa nueva',
        }

    def _post(self, data=None, **kwargs):
        payload = data if data is not None else self.valid_data
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
            **kwargs,
        )

    # ── Casos exitosos ──────────────────────────────────

    def test_contacto_exitoso(self):
        """Mensaje válido se guarda en BD (sin SendGrid configurado)."""
        resp = self._post()
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['ok'])
        # Verificar que se guardó en BD
        self.assertEqual(Contacto.objects.count(), 1)
        c = Contacto.objects.first()
        self.assertEqual(c.nombre, 'Juan Pérez')
        self.assertEqual(c.email, 'juan@gmail.com')

    def test_contacto_sin_proyecto(self):
        """El campo proyecto es opcional."""
        payload = {**self.valid_data, 'proyecto': ''}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['ok'])

    # ── Validación de campos ────────────────────────────

    def test_campos_requeridos_vacios(self):
        for campo in ('nombre', 'correo', 'mensaje'):
            payload = {**self.valid_data, campo: ''}
            resp = self._post(payload)
            self.assertEqual(resp.status_code, 400, f'Campo {campo} vacío debería dar 400')
            self.assertFalse(resp.json()['ok'])

    def test_json_invalido(self):
        resp = self.client.post(
            self.url,
            data='esto no es json{{{',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_metodo_get_no_permitido(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 405)

    # ── Validación de email ─────────────────────────────

    def test_email_formato_invalido(self):
        payload = {**self.valid_data, 'correo': 'no-es-email'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('inválido', resp.json()['error'].lower())

    def test_email_sin_arroba(self):
        payload = {**self.valid_data, 'correo': 'juangmail.com'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)

    # ── Email whitelist ─────────────────────────────────

    def test_dominio_permitido_gmail(self):
        payload = {**self.valid_data, 'correo': 'test@gmail.com'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)

    def test_dominio_permitido_outlook(self):
        payload = {**self.valid_data, 'correo': 'test@outlook.com'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)

    def test_dominio_permitido_hotmail(self):
        payload = {**self.valid_data, 'correo': 'test@hotmail.com'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)

    def test_dominio_permitido_protonmail(self):
        payload = {**self.valid_data, 'correo': 'test@protonmail.com'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)

    def test_dominio_no_permitido(self):
        payload = {**self.valid_data, 'correo': 'hacker@empresa-random.xyz'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('proveedores conocidos', resp.json()['error'])

    def test_dominio_no_permitido_tempmail(self):
        payload = {**self.valid_data, 'correo': 'spam@tempmail.com'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)

    # ── Honeypot ────────────────────────────────────────

    def test_honeypot_bloqueado(self):
        """Si el campo hp tiene contenido, se rechaza (detección de bots)."""
        payload = {**self.valid_data, 'hp': 'soy un bot'}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        # El bot no debe guardar nada en BD
        self.assertEqual(Contacto.objects.count(), 0)

    def test_honeypot_vacio_ok(self):
        """hp vacío no bloquea."""
        payload = {**self.valid_data, 'hp': ''}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)

    # ── Sanitización ────────────────────────────────────

    def test_max_length_nombre(self):
        """Nombres largos se truncan a 100 caracteres."""
        payload = {**self.valid_data, 'nombre': 'A' * 200}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)
        c = Contacto.objects.first()
        self.assertLessEqual(len(c.nombre), 100)

    def test_max_length_mensaje(self):
        """Mensajes largos se truncan a 5000 caracteres."""
        payload = {**self.valid_data, 'mensaje': 'X' * 6000}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)
        c = Contacto.objects.first()
        self.assertLessEqual(len(c.mensaje), 5000)

    def test_trim_whitespace(self):
        """Espacios al inicio/final se eliminan."""
        payload = {**self.valid_data, 'nombre': '  Juan  '}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 200)
        c = Contacto.objects.first()
        self.assertEqual(c.nombre, 'Juan')


# ═══════════════════════════════════════════════════════════════
#  SEGURIDAD
# ═══════════════════════════════════════════════════════════════


class SeguridadTest(TestCase):
    """Tests de validaciones de seguridad."""

    def test_csrf_json_response(self):
        """El endpoint /contact/ devuelve JSON (no HTML) en error de CSRF."""
        client = Client(enforce_csrf_checks=True)
        resp = client.post(
            reverse('proyectos:contact_form'),
            data=json.dumps({'nombre': 'Test', 'correo': 'a@gmail.com', 'mensaje': 'Hi'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)
        data = resp.json()
        self.assertFalse(data['ok'])
        self.assertIn('CSRF', data['error'])

    def test_xss_en_nombre(self):
        """XSS en el nombre se guarda tal cual en BD (sanitización es al renderizar)."""
        xss_payload = '<script>alert("xss")</script>'
        c = Contacto.objects.create(
            nombre=xss_payload,
            email='test@gmail.com',
            mensaje='Test',
        )
        # Se guarda el texto original en BD
        self.assertEqual(c.nombre, xss_payload)

    def test_sanitize_for_html(self):
        """La función _sanitize_for_html escapa HTML correctamente."""
        from .views_api import _sanitize_for_html
        self.assertEqual(_sanitize_for_html('<script>alert(1)</script>'),
                         '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertEqual(_sanitize_for_html(''), '')
        self.assertEqual(_sanitize_for_html(None), '')

    def test_validate_email_function(self):
        """La función _validate_email valida formatos correctamente."""
        from .views_api import _validate_email
        self.assertTrue(_validate_email('user@gmail.com'))
        self.assertTrue(_validate_email('user.name+tag@outlook.com'))
        self.assertFalse(_validate_email('no-arroba'))
        self.assertFalse(_validate_email('@nouser.com'))
        self.assertFalse(_validate_email('user@.com'))

    def test_is_allowed_domain_function(self):
        """La función _is_allowed_domain filtra dominios correctamente."""
        from .views_api import _is_allowed_domain
        self.assertTrue(_is_allowed_domain('user@gmail.com'))
        self.assertTrue(_is_allowed_domain('user@GMAIL.COM'))  # case insensitive
        self.assertTrue(_is_allowed_domain('user@hotmail.com'))
        self.assertTrue(_is_allowed_domain('user@icloud.com'))
        self.assertFalse(_is_allowed_domain('user@evil.xyz'))
        self.assertFalse(_is_allowed_domain('noarroba'))
