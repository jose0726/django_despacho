
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar window.proyectos inmediatamente (vacío hasta que cargue)
    window.proyectos = [];
    window.proyectosLoaded = false;
    
    console.log('[INIT] Script iniciado, DOMContentLoaded disparado');
    
    async function init() {
        console.log('[INIT] Función init() comenzó');
        
        const proyectosFiltradosContainer = document.getElementById('proyectos-filtrados');
        const panelCategorias = document.querySelector('.proyectos-panel');
        
        let proyectos = [];
        let intervalos = [];
        
        // Normalizador sencillo para comparar etiquetas (quita acentos, espacios, pasa a lowercase)
        // Nota: evitamos \p{Diacritic} por compatibilidad (algunos browsers rompen el script).
        const normalizeString = (s) => String(s || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/\s+/g, ' ')
            .trim()
            .toLowerCase()
            .replace(/\s+/g, '-');
        
        // Observer para animar cards que entran al viewport (una sola vez por elemento)
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                // Solo animar si está entrando Y no ha sido animado previamente
                if (entry.isIntersecting && !entry.target.dataset.animated) {
                    entry.target.dataset.animated = 'true';
                    anime({
                        targets: entry.target,
                        translateY: [30, 0],
                        opacity: [0, 1],
                        duration: 800,
                        easing: 'easeOutExpo'
                    });
                    // Dejar de observar este elemento (ya cumplió su propósito)
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        // Cargar proyectos desde la API de Django
        console.log('[FETCH] Iniciando fetch a API...');
        try {
            // API_BASE se define en el template. Si es '' o no existe, usamos same-origin.
            const API_BASE = (typeof window.API_BASE === 'string') ? window.API_BASE : '';
            const apiBaseTrimmed = API_BASE.replace(/\/$/, '');
            const apiUrl = apiBaseTrimmed
                ? (apiBaseTrimmed + '/api/proyectos/?page_size=1000')
                : '/api/proyectos/?page_size=1000';
            console.log('[FETCH] URL:', apiUrl);

            const response = await fetch(apiUrl);
            console.log('[FETCH] Respuesta recibida, status:', response.status);
            
            if (!response.ok) throw new Error('HTTP error! status: ' + response.status);
            const data = await response.json();
            console.log('[FETCH] Datos parseados, tipo:', Array.isArray(data) ? 'array' : 'object', 'keys:', Object.keys(data));
            
            // Soportar diferentes formatos de respuesta:
            // - paginada: { count, results: [...] }
            // - lista directa: [...]
            // - envuelta: { proyectos: [...] }
            let raw = [];
            if (Array.isArray(data)) raw = data;
            else if (Array.isArray(data.results)) raw = data.results;
            else if (Array.isArray(data.proyectos)) raw = data.proyectos;
            else raw = [];

            console.log('[FETCH] Proyectos extraídos:', raw.length);

            // Placeholder inline para evitar 404s
            const PLACEHOLDER = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="100%" height="100%" fill="%23e5e7eb"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="Arial, Helvetica, sans-serif" font-size="24">Sin imagen</text></svg>';

            // Normalizar campos al contrato de Django (nombre, descripcion, categoria, subcategoria, imagenes[])
            const API_ORIGIN = apiBaseTrimmed || window.location.origin;
            const resolveImageUrl = (u) => {
                if (!u) return '';
                const s = String(u);
                if (/^https?:\/\//i.test(s)) return s;
                if (s.startsWith('/')) return API_ORIGIN + s;
                return s;
            };
            proyectos = raw.map(p => {
                // Extraer array de imágenes desde la API
                const imgs = Array.isArray(p.imagenes) ? p.imagenes : [];
                const firstImg = imgs.length && imgs[0].imagen ? resolveImageUrl(imgs[0].imagen) : '';
                
                const nombre = (p && p.nombre != null) ? p.nombre : ((p && p.titulo != null) ? p.titulo : '');
                const descripcion = (p && p.descripcion != null) ? p.descripcion : '';
                const categoria = (p && p.categoria != null) ? p.categoria : '';
                const subcategoria = (p && p.subcategoria != null) ? p.subcategoria : ((p && p.sub != null) ? p.sub : '');

                return {
                    id: p.id,
                    nombre: nombre,
                    descripcion: descripcion,
                    categoria: categoria,
                    subcategoria: subcategoria,
                    imagenes: imgs.map(i => i.imagen ? resolveImageUrl(i.imagen) : '').filter(Boolean),
                    preview: firstImg || PLACEHOLDER,  // primera imagen o placeholder
                };
            });
            
            // CRÍTICO: Asignar a window.proyectos (no __proyectos)
            window.proyectos = proyectos;
            window.proyectosLoaded = true;
            console.log('✅ [SUCCESS] Proyectos cargados y asignados a window.proyectos:', proyectos.length);
            console.log('✅ Primer proyecto:', proyectos[0]);

            if (!proyectos.length) {
                proyectosFiltradosContainer.innerHTML = '<p class="no-proyectos">Aún no hay proyectos cargados.</p>';
                // No continuar: no hay categorías que construir.
                return;
            }


        } catch (error) {
            console.error("❌ [ERROR] No se pudieron cargar los proyectos:", error);
            window.proyectosLoaded = false;
            proyectosFiltradosContainer.innerHTML = '<p class="no-proyectos">Error al cargar la información de proyectos. Por favor, intente más tarde.</p>';
            return;
        }
        // Resolver URLs de imagen (ya normalizado arriba)
        const resolveImageUrl = (u) => u || '';

        // --- Construir categorías y subcategorías dinámicamente desde los datos ---
        const titleCase = (s) => String(s || '')
            .toLowerCase()
            .split(' ')
            .map(w => w ? w[0].toUpperCase() + w.slice(1) : '')
            .join(' ');

        const categoriasMap = new Map(); // key: slug normalizado, value: { label, subs: Map }
        proyectos.forEach(p => {
            const catSlug = normalizeString(p.categoria);
            const subSlug = normalizeString(p.subcategoria);
            const catLabel = titleCase(p.categoria);
            const subLabel = titleCase(p.subcategoria);
            if (!catSlug) return;
            if (!categoriasMap.has(catSlug)) {
                categoriasMap.set(catSlug, { label: catLabel, subs: new Map() });
            }
            const entry = categoriasMap.get(catSlug);
            if (subSlug) {
                entry.subs.set(subSlug, subLabel);
            }
        });

        // Helper centralizado para limpiar UI al cambiar filtros/categorías
        async function resetUI({ exceptCat = null } = {}) {
            // 1) Animación de salida y limpieza de proyectos
            if (proyectosFiltradosContainer.children.length > 0) {
                try {
                    await anime({
                        targets: '.proyecto-item',
                        translateY: [0, -30],
                        opacity: [1, 0],
                        duration: 400,
                        easing: 'easeInExpo'
                    }).finished;
                } catch (_) { /* noop */ }
            }
            proyectosFiltradosContainer.innerHTML = '';
            // 2) Cancelar intervalos/timers previos (si existieran)
            intervalos.forEach(id => clearInterval(id));
            intervalos = [];
            // 3) Cerrar todas las categorías excepto la indicada
            const cats = panelCategorias.querySelectorAll('.categoria');
            cats.forEach(c => {
                if (exceptCat && c === exceptCat) return;
                const btn = c.querySelector('.categoria-btn');
                const subContainer = c.querySelector('.subcategoria-container');
                if (btn) btn.setAttribute('aria-expanded', 'false');
                if (subContainer) subContainer.style.display = 'none';
            });
        }

        // Limpiar cualquier markup estático y renderizar dinámico
        panelCategorias.innerHTML = '';
        categoriasMap.forEach(({ label, subs }, catSlug) => {
            const catDiv = document.createElement('div');
            catDiv.className = 'categoria';
            const catBtn = document.createElement('button');
            catBtn.className = 'categoria-btn';
            catBtn.setAttribute('aria-expanded', 'false');
            catBtn.textContent = label || '';
            const subContainer = document.createElement('div');
            subContainer.className = 'subcategoria-container';
            subContainer.style.display = 'none';
            subs.forEach((subLabel, subSlug) => {
                const sBtn = document.createElement('button');
                sBtn.className = 'subcategoria-btn';
                sBtn.textContent = subLabel || '';
                // Listener de subcategoría: mantener solo una categoría activa, limpiar UI y renderizar
                sBtn.addEventListener('click', async () => {
                    const sub = subSlug;
                    await resetUI({ exceptCat: catDiv });
                    const filtrados = proyectos.filter(p => normalizeString(p.subcategoria) === sub);
                    if (filtrados.length === 0) {
                        proyectosFiltradosContainer.innerHTML = '<p class="no-proyectos">No hay proyectos en esta subcategoría.</p>';
                        return;
                    }
                    renderProyectos(filtrados);
                });
                subContainer.appendChild(sBtn);
            });
            // Listener de categoría: solo una activa a la vez, renderiza la categoría
            catBtn.addEventListener('click', async () => {
                const estaAbierto = subContainer.style.display === 'block';
                if (estaAbierto) {
                    await resetUI({});
                } else {
                    await resetUI({ exceptCat: catDiv });
                    subContainer.style.display = 'block';
                    catBtn.setAttribute('aria-expanded', 'true');
                    const filtradosCat = proyectos.filter(p => normalizeString(p.categoria) === catSlug);
                    if (filtradosCat.length === 0) {
                        proyectosFiltradosContainer.innerHTML = '<p class="no-proyectos">No hay proyectos en esta categoría.</p>';
                    } else {
                        renderProyectos(filtradosCat);
                    }
                }
            });
            catDiv.appendChild(catBtn);
            catDiv.appendChild(subContainer);
            panelCategorias.appendChild(catDiv);
        });

        // --- Filtrado inicial según parámetro ---
        const params = new URLSearchParams(window.location.search);
        const categoriaParam = params.get('categoria');
        const subParam = params.get('sub');

        // Mostrar una categoría concreta si viene por parámetro
        if (categoriaParam) {
            const catSlug = normalizeString(categoriaParam);
            const cats = panelCategorias.querySelectorAll('.categoria');
            cats.forEach(async c => {
                const btn = c.querySelector('.categoria-btn');
                const subContainer = c.querySelector('.subcategoria-container');
                if (btn && normalizeString(btn.textContent) === catSlug) {
                    await resetUI({ exceptCat: c });
                    c.style.display = '';
                    if (subContainer) subContainer.style.display = 'block';
                    btn.setAttribute('aria-expanded', 'true');
                    const filtradosCat = proyectos.filter(p => normalizeString(p.categoria) === catSlug);
                    if (filtradosCat.length === 0) {
                        proyectosFiltradosContainer.innerHTML = '<p class="no-proyectos">No hay proyectos en esta categoría.</p>';
                    } else {
                        renderProyectos(filtradosCat);
                    }
                } else {
                    c.style.display = 'none';
                }
            });
        }

        // Si no hay parámetros de filtro, mostrar todos los proyectos inicialmente
        if (!categoriaParam && !subParam) {
            renderProyectos(proyectos);
        }

        // Si hay subcategoría en el querystring, mostrar esa sub y renderizar directamente
        if (subParam) {
            const subSlug = normalizeString(subParam);
            const cats = panelCategorias.querySelectorAll('.categoria');
            let matched = false;
            cats.forEach(async c => {
                const btn = c.querySelector('.categoria-btn');
                const subContainer = c.querySelector('.subcategoria-container');
                const subBtns = c.querySelectorAll('.subcategoria-btn');
                let foundHere = false;
                subBtns.forEach(s => {
                    const lbl = normalizeString(s.textContent);
                    if (lbl === subSlug) {
                        foundHere = true;
                        s.style.display = 'inline-block';
                    } else {
                        s.style.display = 'none';
                    }
                });
                if (foundHere) {
                    matched = true;
                    await resetUI({ exceptCat: c });
                    c.style.display = '';
                    btn.setAttribute('aria-expanded', 'true');
                    if (subContainer) subContainer.style.display = 'block';
                } else {
                    c.style.display = 'none';
                }
            });
            proyectosFiltradosContainer.innerHTML = '';
            const filtrados = proyectos.filter(p => normalizeString(p.subcategoria) === subSlug);
            if (!filtrados.length) {
                proyectosFiltradosContainer.innerHTML = '<p class="no-proyectos">No hay proyectos en esta subcategoría.</p>';
            } else {
                renderProyectos(filtrados);
            }
        }

        // Ya se añadieron listeners a cada botón de subcategoría al construir el DOM dinámico.

        // --- Tooltip imagen ---
        const tooltip = document.createElement('div');
        tooltip.classList.add('tooltip-imagen');
        const tooltipImg = document.createElement('img');
        tooltip.appendChild(tooltipImg);
        document.body.appendChild(tooltip);
        document.addEventListener('mouseover', e => {
            const imgTarget = e.target.closest('.proyecto-item img');
            if (imgTarget) {
                tooltipImg.src = imgTarget.src;
                tooltip.style.display = 'block';
            }
        });
        document.addEventListener('mousemove', e => {
            tooltip.style.left = e.pageX + 20 + 'px';
            tooltip.style.top = e.pageY + 20 + 'px';
        });
        document.addEventListener('mouseout', e => {
            if (e.target.closest('.proyecto-item img')) {
                tooltip.style.display = 'none';
            }
        });

        // Helper para renderizado de proyectos con animación y observers
        function renderProyectos(lista) {
            // Placeholder inline para evitar 404s
            const PLACEHOLDER = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="100%" height="100%" fill="%23e5e7eb"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="Arial, Helvetica, sans-serif" font-size="24">Sin imagen</text></svg>';
            
            const visibles = [];
            const fuera = [];
            
            lista.forEach(p => {
                const div = document.createElement('div');
                div.classList.add('proyecto-item');
                const imgEl = document.createElement('img');
                imgEl.alt = p.nombre;
                imgEl.loading = 'lazy';
                imgEl.src = p.preview || PLACEHOLDER;
                imgEl.addEventListener('error', function () {
                    if (this.src !== PLACEHOLDER) this.src = PLACEHOLDER;
                });
                const descripcion = document.createElement('div');
                descripcion.className = 'descripcion';
                descripcion.innerHTML = '<h4>' + (p.nombre || '') + '</h4><p>' + (p.descripcion || '') + '</p>';
                div.appendChild(imgEl);
                div.appendChild(descripcion);
                div.addEventListener('click', () => abrirModal(p));
                proyectosFiltradosContainer.appendChild(div);
                
                // Determinar si está visible inicialmente
                const rect = div.getBoundingClientRect();
                const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
                const inViewport = rect.top < viewportHeight * 0.95 && rect.bottom > 0;
                
                if (inViewport) {
                    visibles.push(div);
                } else {
                    fuera.push(div);
                }
            });
            
            // Animar elementos visibles con stagger (una sola vez)
            if (visibles.length) {
                visibles.forEach(el => {
                    el.dataset.animated = 'true'; // marcar como animado
                    el.getBoundingClientRect();
                });
                requestAnimationFrame(() => {
                    anime({
                        targets: visibles,
                        translateY: [100, 0],
                        opacity: [0, 1],
                        delay: anime.stagger(200),
                        duration: 800,
                        easing: 'easeOutExpo'
                    });
                });
            }
            
            // Registrar elementos fuera del viewport para animar al hacer scroll
            fuera.forEach(el => {
                observer.observe(el);
            });
        }

        // Modal para visualizar un proyecto con sus imágenes (con clases para estilos/animaciones CSS)
        function abrirModal(p) {
            try {
                // Eliminar cualquier modal anterior
                const prev = document.getElementById('modal-proyecto');
                if (prev) prev.remove();

                // Overlay
                const overlay = document.createElement('div');
                overlay.id = 'modal-proyecto';
                overlay.setAttribute('role', 'dialog');
                overlay.setAttribute('aria-modal', 'true');
                overlay.style.display = 'flex'; // activar el flex ya que el estilo base usa display:none

                // Contenido
                const box = document.createElement('div');
                box.className = 'modal-contenido';

                // Botón cerrar
                const closeBtn = document.createElement('button');
                closeBtn.className = 'close-modal';
                closeBtn.setAttribute('aria-label', 'Cerrar');
                closeBtn.innerHTML = '&times;';

                // Título
                const title = document.createElement('h3');
                title.textContent = p.nombre || '';

                // Cuerpo del modal (galería + info)
                const body = document.createElement('div');
                body.className = 'modal-body';

                // Galería
                const galeria = document.createElement('div');
                galeria.className = 'modal-galeria';

                const prevBtn = document.createElement('button');
                prevBtn.className = 'nav-btn nav-prev';
                prevBtn.setAttribute('aria-label', 'Anterior');
                prevBtn.textContent = '❮';

                const img = document.createElement('img');
                img.id = 'modal-img';
                img.alt = p.nombre || '';

                const nextBtn = document.createElement('button');
                nextBtn.className = 'nav-btn nav-next';
                nextBtn.setAttribute('aria-label', 'Siguiente');
                nextBtn.textContent = '❯';

                // Lógica de imágenes: usar array completo desde p.imagenes
                const PLACEHOLDER = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="100%" height="100%" fill="%23e5e7eb"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="Arial, Helvetica, sans-serif" font-size="24">Sin imagen</text></svg>';
                const imgs = Array.isArray(p.imagenes) && p.imagenes.length ? p.imagenes : [];
                let idx = 0;
                
                const setImg = (i) => {
                    if (!imgs.length) {
                        img.src = PLACEHOLDER;
                        return;
                    }
                    img.src = imgs[i] || PLACEHOLDER;
                };
                setImg(idx);

                // Navegación (solo si hay múltiples imágenes)
                const goPrev = (ev) => {
                    if (ev) ev.stopPropagation();
                    if (imgs.length <= 1) return;
                    idx = (idx - 1 + imgs.length) % imgs.length;
                    setImg(idx);
                };
                const goNext = (ev) => {
                    if (ev) ev.stopPropagation();
                    if (imgs.length <= 1) return;
                    idx = (idx + 1) % imgs.length;
                    setImg(idx);
                };
                prevBtn.addEventListener('click', goPrev);
                nextBtn.addEventListener('click', goNext);
                
                // Ocultar botones de navegación si solo hay una imagen
                if (imgs.length <= 1) {
                    prevBtn.style.display = 'none';
                    nextBtn.style.display = 'none';
                }

                // Cerrar
                const close = (ev) => {
                    if (ev) ev.stopPropagation();
                    overlay.remove();
                    document.removeEventListener('keydown', onKey);
                };
                closeBtn.addEventListener('click', close);
                overlay.addEventListener('click', close);

                // Evitar que clics dentro del contenido cierren el modal
                box.addEventListener('click', (e) => e.stopPropagation());

                // Teclado
                const onKey = (e) => {
                    if (e.key === 'Escape') return close();
                    if (e.key === 'ArrowLeft') return goPrev();
                    if (e.key === 'ArrowRight') return goNext();
                };
                document.addEventListener('keydown', onKey);

                // Panel de información
                const info = document.createElement('aside');
                info.className = 'modal-info';
                const subEl = document.createElement('div');
                subEl.className = 'modal-sub';
                subEl.textContent = p.subcategoria ? ('Categoría: ' + p.subcategoria) : '';
                const descEl = document.createElement('p');
                descEl.className = 'modal-desc';
                descEl.textContent = p.descripcion || '';
                info.appendChild(subEl);
                info.appendChild(descEl);

                // Ensamblado
                galeria.appendChild(prevBtn);
                galeria.appendChild(img);
                galeria.appendChild(nextBtn);
                body.appendChild(galeria);
                body.appendChild(info);

                box.appendChild(closeBtn);
                box.appendChild(title);
                box.appendChild(body);
                overlay.appendChild(box);
                document.body.appendChild(overlay);
            } catch (err) {
                console.error('Error abriendo modal:', err);
            }
        }
    }
    // Llamar a la función principal para iniciar la lógica de la página
    init();
});
