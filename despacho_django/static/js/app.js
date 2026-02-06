document.addEventListener('DOMContentLoaded', () => {
  const precargador = document.getElementById('preloader');
  if (!precargador) return;
  document.body.classList.add('preloader-active');

  // UX: no bloquear por carga total de assets; mínimo fijo 250ms.
  const duracionMinima = 250;
  const inicio = Date.now();

  // tiempos internos (ajusta si quieres)
  const T_IN = 250;       // entrada lateral
  const T_APPROACH = 0; // ajuste previo al choque
  const T_COLLIDE = 200;  // choque / unión
  const T_SHOW = 400;     // logo totalmente unido visible
  const T_FADE = 200;     // salida

  function setState(state) {
    precargador.classList.remove('state-logo-in','state-logo-collision','state-logo-joined','state-fadeout');
    if (state) precargador.classList.add(state);
  }

  function hidePreloaderFinal() {
    if (precargador.classList.contains('hidden')) return;
    precargador.classList.add('hidden');
    document.body.classList.remove('preloader-active');
    setTimeout(() => {
      if (precargador.parentNode) precargador.parentNode.removeChild(precargador);
    }, 600);
  }

  function runLogoSequence() {
    // 1. mitades entran desde los lados hasta quedar cerca del centro
    setState('state-logo-in');
    setTimeout(() => {
      // 2. pequeño ajuste antes del choque (opcional, aquí lo combinamos)
      setState('state-logo-collision');
      setTimeout(() => {
        // 3. se unen (posición final)
        setState('state-logo-joined');
        setTimeout(() => {
          // 4. fade out y remover
          setState('state-fadeout');
          setTimeout(hidePreloaderFinal, T_FADE);
        }, T_SHOW);
      }, T_COLLIDE);
    }, T_IN + T_APPROACH);
  }

  function onReadyHandler() {
    const tiempoCarga = Date.now() - inicio;
    const remaining = tiempoCarga < duracionMinima ? duracionMinima - tiempoCarga : 0;
    setTimeout(runLogoSequence, remaining);
  }

  // Ejecutar desde DOMContentLoaded (este handler ya corre aquí).
  onReadyHandler();

  // fallback robusto
  setTimeout(() => { runLogoSequence(); }, 10000);
});
    const observador = new IntersectionObserver((entradas) => {
        entradas.forEach(entrada => {
            if (entrada.isIntersecting) entrada.target.classList.add('is-visible');
        });
    }, { threshold: 0.1 });

    const elementosParaAnimar = document.querySelectorAll('.animate-on-scroll');
    elementosParaAnimar.forEach(elemento => observador.observe(elemento));

  const formularioContacto = document.getElementById('formulario-contacto');
  const mensajeConfirmacion = document.getElementById('mensaje-confirmacion');

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  if (formularioContacto) {
    formularioContacto.addEventListener('submit', async function(evento) {
      evento.preventDefault();

      // simple UX: deshabilitar botón
      const submitBtn = formularioContacto.querySelector('button[type="submit"]');
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Enviando...'; }

      if (mensajeConfirmacion) {
        mensajeConfirmacion.textContent = '';
        mensajeConfirmacion.style.display = 'block';
        mensajeConfirmacion.style.color = '#333';
      }

      const formData = {
        nombre: formularioContacto.querySelector('#nombre') ? formularioContacto.querySelector('#nombre').value.trim() : '',
        correo: formularioContacto.querySelector('#correo') ? formularioContacto.querySelector('#correo').value.trim() : '',
        mensaje: formularioContacto.querySelector('#mensaje') ? formularioContacto.querySelector('#mensaje').value.trim() : '',
        hp: formularioContacto.querySelector('#hp') ? formularioContacto.querySelector('#hp').value.trim() : ''
      };

      // Validación básica
      if (!formData.nombre || !formData.correo || !formData.mensaje) {
        if (mensajeConfirmacion) {
          mensajeConfirmacion.textContent = 'Por favor completa todos los campos.';
          mensajeConfirmacion.style.color = '#d9534f';
        }
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Enviar Mensaje'; }
        return;
      }

      try {
        const csrftoken = getCookie('csrftoken');
        const res = await fetch('/contact/', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {
            'Content-Type': 'application/json',
            ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
          },
          body: JSON.stringify(formData)
        });

        const contentType = (res.headers && res.headers.get)
          ? (res.headers.get('content-type') || '')
          : '';

        let payload = null;
        if (contentType.includes('application/json')) {
          payload = await res.json();
        } else {
          const text = await res.text();
          throw new Error(`Respuesta no-JSON del backend (HTTP ${res.status}): ${text.slice(0, 200)}`);
        }

        if (res.ok && payload && payload.ok) {
          if (mensajeConfirmacion) {
            mensajeConfirmacion.textContent = '¡Mensaje enviado con éxito! Nos pondremos en contacto contigo pronto.';
            mensajeConfirmacion.style.color = '#27ae60';
          }
          formularioContacto.reset();
        } else {
          // Mostrar mensaje específico del backend si existe (por ejemplo: ¿Quisiste decir @gmail.com?)
          const msg = payload && payload.error
            ? payload.error
            : (payload && payload.message ? payload.message : 'Error al enviar. Intenta de nuevo más tarde.');

          if (mensajeConfirmacion) {
            mensajeConfirmacion.textContent = msg;
            mensajeConfirmacion.style.color = '#d9534f';
          }
        }
      } catch (err) {
        console.error('Error enviando formulario:', err);
        if (mensajeConfirmacion) {
          mensajeConfirmacion.textContent = 'Ocurrió un error de conexión. Intenta de nuevo más tarde.';
          mensajeConfirmacion.style.color = '#d9534f';
        }
      } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Enviar Mensaje'; }
      }
    });
  }

    const modal = document.getElementById("imageModal");
    if (modal) {
        const imagenModal = document.getElementById("modalImage");
        const botonCerrar = document.querySelector(".close-modal");

    const cerrarModal = () => modal.style.display = "none";

  // Importante: excluimos imágenes de highlights para que no abran el modal.
  // El modal debe abrirse solo para imágenes de proyectos (cards/lista filtrada).
  document.querySelectorAll('.proyecto-card img, .proyecto-item img').forEach(imagen => {
            imagen.addEventListener('click', () => {
                modal.style.display = "flex";
                imagenModal.src = imagen.src;
                imagenModal.alt = imagen.alt;
            });

      // Sólo efecto hover para imágenes de proyectos, no para highlights
      imagen.addEventListener('mouseenter', () => imagen.style.transform = 'scale(1.05)');
      imagen.addEventListener('mouseleave', () => imagen.style.transform = 'scale(1)');
        });

        if (botonCerrar) botonCerrar.addEventListener('click', cerrarModal);
        window.addEventListener('click', (evento) => { if (evento.target === modal) cerrarModal(); });
        window.addEventListener('keydown', (evento) => { if (evento.key === 'Escape' && modal.style.display === "flex") cerrarModal(); });
    }

    // Animación para mostrar el equipo secundario al hacer scroll
const equipoSecundario = document.querySelector(".equipo-secundario");

if (equipoSecundario) {
  const observerEquipo = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Añadimos la clase visible
        equipoSecundario.classList.add("visible");

        // Opcional: animar cada miembro con delay
        const miembros = equipoSecundario.querySelectorAll(".miembro");
        miembros.forEach((miembro, index) => {
          miembro.style.transitionDelay = `${index * 0.2}s`;
          miembro.classList.add("visible");
        });

        observerEquipo.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  observerEquipo.observe(equipoSecundario);
}

