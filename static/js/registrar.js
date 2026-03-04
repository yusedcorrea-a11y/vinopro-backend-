/**
 * Registrar vino: formulario, registros-hoy, pre-relleno desde escaneo, países, buscador para registrar.
 * Requiere: window.ERROR_MSGS, window.INFO_REGISTROS_HOY y window.REGISTRAR_BUSCAR (inyectados por la plantilla).
 */
(function() {
  const form = document.getElementById('formRegistro');
  const mensajeDiv = document.getElementById('mensaje');
  const inputBuscar = document.getElementById('buscar-vino-input');
  const divResultados = document.getElementById('buscar-vino-resultados');
  const pNoResultados = document.getElementById('buscar-vino-no-resultados');
  const SESSION_KEY = 'vino_pro_session_id';
  const TEXTS = window.REGISTRAR_BUSCAR || {};
  var esPro = false;

  if (!form) return;

  function setFormBlocked(blocked) {
    if (!form) return;
    if (blocked) {
      form.classList.add('form-blocked-no-resultados');
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.setAttribute('aria-disabled', 'true'); }
    } else {
      form.classList.remove('form-blocked-no-resultados');
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = false; btn.removeAttribute('aria-disabled'); }
    }
  }

  function getSid() {
    try {
      return (localStorage.getItem(SESSION_KEY) || '').trim();
    } catch (e) {
      return '';
    }
  }

  function loadRegistrosHoy() {
    const sid = getSid();
    const el = document.getElementById('registros-hoy-msg');
    if (!el || !sid) {
      if (el) el.textContent = '';
      return;
    }
    fetch('/api/bodega/registros-hoy', { headers: { 'X-Session-ID': sid, 'Accept': 'application/json' } })
      .then(r => r.json())
      .then(d => {
        const n = d.registros_hoy || 0;
        const max = d.limite;
        const tpl = window.INFO_REGISTROS_HOY || 'Hoy has registrado {n} de {max} vinos.';
        if (max == null) el.textContent = tpl.replace('{n}', n).replace(' de {max}', '').replace('{max}', '') || ('Hoy has registrado ' + n + ' vinos.');
        else el.textContent = tpl.replace('{n}', n).replace('{max}', max);
      })
      .catch(() => { if (el) el.textContent = ''; });
  }
  loadRegistrosHoy();

  (function loadCheckLimit() {
    var sid = getSid();
    if (!sid) return;
    fetch('/api/check-limit', { headers: { 'X-Session-ID': sid, 'Accept': 'application/json' } })
      .then(function(r) { return r.json(); })
      .then(function(d) { esPro = !!d.es_pro; })
      .catch(function() {});
  })();

  function prefillForm(vino) {
    if (!vino) return;
    const set = function(id, val) {
      const el = document.getElementById(id);
      if (el) el.value = (val != null && val !== '') ? String(val) : '';
    };
    set('nombre', vino.nombre);
    set('bodega', vino.bodega);
    set('region', vino.region);
    set('pais', vino.pais);
    set('tipo', vino.tipo || 'tinto');
    set('puntuacion', vino.puntuacion);
    set('precio_estimado', vino.precio_estimado);
    set('descripcion', vino.descripcion);
    set('notas_cata', vino.notas_cata);
    set('maridaje', vino.maridaje);
    if (divResultados) { divResultados.classList.add('hidden'); divResultados.innerHTML = ''; }
    if (pNoResultados) pNoResultados.classList.add('hidden');
    if (inputBuscar) inputBuscar.value = '';
    setFormBlocked(false);
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function showResultados(data) {
    if (!divResultados || !pNoResultados) return;
    const enBd = (data.en_bd || []);
    const externos = (data.externos || []).map(function(x) { return x.vino || x; });
    const total = enBd.length + externos.length;
    pNoResultados.classList.add('hidden');
    setFormBlocked(false);
    if (total === 0) {
      divResultados.classList.add('hidden');
      divResultados.innerHTML = '';
      if (esPro) {
        pNoResultados.textContent = TEXTS.no_resultados || 'No hay resultados. Rellena el formulario manualmente.';
      } else {
        var cta = (TEXTS.no_resultados_premium_cta || 'Este vino no está en nuestra base. Pásate a Premium para registrarlo y poder ofrecerlo a otros.');
        var linkText = TEXTS.ir_planes || 'Ver planes';
        pNoResultados.innerHTML = cta + ' <a href="/planes" class="link-planes">' + escapeHtml(linkText) + '</a>';
        setFormBlocked(true);
      }
      pNoResultados.classList.remove('hidden');
      return;
    }
    let html = '';
    if (enBd.length) {
      html += '<div class="grupo">' + (TEXTS.en_nuestra_base || 'En nuestra base') + '</div>';
      enBd.forEach(function(r) {
        const v = r.vino || {};
        const nombre = (v.nombre || '').trim() || '—';
        const detalle = [v.bodega, v.region, v.pais].filter(Boolean).join(' · ');
        html += '<div class="item" role="listitem" data-origen="bd" data-key="' + (r.key || '') + '"><div><div class="nombre">' + escapeHtml(nombre) + '</div>' + (detalle ? '<div class="detalle">' + escapeHtml(detalle) + '</div>' : '') + '</div><span class="accion">' + (TEXTS.ya_en_base || 'Ya en la base') + '</span></div>';
      });
    }
    if (externos.length) {
      html += '<div class="grupo">' + (TEXTS.encontrados_internet || 'Encontrados en internet') + '</div>';
      externos.forEach(function(v, i) {
        const nombre = (v.nombre || '').trim() || '—';
        const detalle = [v.bodega, v.region, v.pais].filter(Boolean).join(' · ');
        html += '<div class="item" role="listitem" data-origen="externo" data-index="' + i + '"><div><div class="nombre">' + escapeHtml(nombre) + '</div>' + (detalle ? '<div class="detalle">' + escapeHtml(detalle) + '</div>' : '') + '</div><span class="accion">' + (TEXTS.usar_datos || 'Usar estos datos') + '</span></div>';
      });
    }
    divResultados.innerHTML = html;
    divResultados.classList.remove('hidden');
    divResultados.querySelectorAll('.item').forEach(function(el) {
      el.addEventListener('click', function() {
        const origen = el.getAttribute('data-origen');
        if (origen === 'bd') {
          mensajeDiv.className = 'mensaje exito';
          mensajeDiv.textContent = TEXTS.ya_en_base || 'Este vino ya está en nuestra base de datos.';
          mensajeDiv.classList.remove('hidden');
          divResultados.classList.add('hidden');
          divResultados.innerHTML = '';
          inputBuscar.value = '';
        } else {
          const idx = parseInt(el.getAttribute('data-index'), 10);
          if (!isNaN(idx) && externos[idx]) prefillForm(externos[idx]);
        }
      });
    });
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  var buscarTimeout;
  if (inputBuscar) {
    inputBuscar.addEventListener('input', function() {
      var q = (inputBuscar.value || '').trim();
      clearTimeout(buscarTimeout);
      if (q.length < 2) {
        if (divResultados) { divResultados.classList.add('hidden'); divResultados.innerHTML = ''; }
        if (pNoResultados) { pNoResultados.classList.add('hidden'); pNoResultados.textContent = ''; pNoResultados.innerHTML = ''; }
        setFormBlocked(false);
        return;
      }
      buscarTimeout = setTimeout(function() {
        fetch('/api/buscar-para-registrar?q=' + encodeURIComponent(q), { headers: { 'Accept': 'application/json' } })
          .then(function(r) { return r.json(); })
          .then(showResultados)
          .catch(function() {
            if (divResultados) divResultados.classList.add('hidden');
            if (pNoResultados) { pNoResultados.textContent = TEXTS.no_resultados || 'No hay resultados.'; pNoResultados.classList.remove('hidden'); }
          });
      }, 350);
    });
    inputBuscar.addEventListener('focus', function() {
      if (divResultados && divResultados.innerHTML.trim() && !divResultados.classList.contains('hidden')) divResultados.classList.remove('hidden');
    });
  }
  document.addEventListener('click', function(e) {
    if (divResultados && !divResultados.classList.contains('hidden') && inputBuscar && !inputBuscar.contains(e.target) && !divResultados.contains(e.target)) {
      divResultados.classList.add('hidden');
    }
  });

  try {
    const stored = sessionStorage.getItem('vinoParaRegistrar');
    if (stored) {
      const v = JSON.parse(stored);
      sessionStorage.removeItem('vinoParaRegistrar');
      if (v.nombre) document.getElementById('nombre').value = v.nombre;
      if (v.bodega) document.getElementById('bodega').value = v.bodega;
      if (v.region) document.getElementById('region').value = v.region;
      if (v.pais) document.getElementById('pais').value = v.pais;
      if (v.tipo) document.getElementById('tipo').value = v.tipo;
      if (v.puntuacion != null) document.getElementById('puntuacion').value = v.puntuacion;
      if (v.precio_estimado) document.getElementById('precio_estimado').value = v.precio_estimado;
      if (v.descripcion) document.getElementById('descripcion').value = v.descripcion;
      if (v.notas_cata) document.getElementById('notas_cata').value = v.notas_cata;
      if (v.maridaje) document.getElementById('maridaje').value = v.maridaje;
    }
  } catch (_) {}

  fetch('/paises')
    .then(r => r.json())
    .then(data => {
      const sel = document.getElementById('pais');
      if (!sel) return;
      const current = sel.value;
      (data.paises || []).sort().forEach(p => {
        const opt = document.createElement('option');
        opt.value = p;
        opt.textContent = p;
        sel.appendChild(opt);
      });
      if (current) sel.value = current;
    })
    .catch(() => {});

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    mensajeDiv.classList.add('hidden');
    const payload = {
      nombre: document.getElementById('nombre').value.trim(),
      bodega: document.getElementById('bodega').value.trim(),
      region: document.getElementById('region').value.trim(),
      pais: document.getElementById('pais').value.trim(),
      tipo: document.getElementById('tipo').value.trim() || 'tinto',
      puntuacion: document.getElementById('puntuacion').value ? parseInt(document.getElementById('puntuacion').value, 10) : null,
      precio_estimado: document.getElementById('precio_estimado').value.trim() || null,
      descripcion: document.getElementById('descripcion').value.trim(),
      notas_cata: document.getElementById('notas_cata').value.trim(),
      maridaje: document.getElementById('maridaje').value.trim()
    };
    if (!payload.nombre || !payload.bodega || !payload.region || !payload.pais) {
      mensajeDiv.className = 'mensaje error';
      mensajeDiv.textContent = 'Rellena nombre, bodega, región y país.';
      mensajeDiv.classList.remove('hidden');
      return;
    }
    try {
      const sid = getSid();
      const headers = { 'Content-Type': 'application/json' };
      if (sid) headers['X-Session-ID'] = sid;
      const r = await fetch('/registrar-vino', {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      });
      const data = await r.json();
      if (r.ok && data.success) {
        mensajeDiv.className = 'mensaje exito';
        var key = data.key || '';
        var txt = 'Vino registrado correctamente. Clave: ' + key;
        if (esPro && key) {
          txt += '. <a href="/oferta/crear?key=' + encodeURIComponent(key) + '" class="link-oferta">¿Ofrecer este vino a otros? Añade una foto</a>';
        }
        mensajeDiv.innerHTML = txt;
        mensajeDiv.classList.remove('hidden');
        form.reset();
        loadRegistrosHoy();
      } else if (r.status === 400 && data.detail && data.detail.message_key) {
        const msg = (window.ERROR_MSGS && window.ERROR_MSGS[data.detail.message_key]) || data.detail.message_key;
        mensajeDiv.className = 'mensaje error';
        mensajeDiv.textContent = msg;
        mensajeDiv.classList.remove('hidden');
      } else if (r.status === 429) {
        const msg = (window.ERROR_MSGS && window.ERROR_MSGS.limite_diario) || 'Límite diario alcanzado.';
        mensajeDiv.className = 'mensaje error';
        mensajeDiv.textContent = msg;
        mensajeDiv.classList.remove('hidden');
      } else {
        mensajeDiv.className = 'mensaje error';
        mensajeDiv.textContent = data.detail && (data.detail.message || data.detail.message_key) || data.message || 'Error al registrar';
        mensajeDiv.classList.remove('hidden');
      }
    } catch (err) {
      mensajeDiv.className = 'mensaje error';
      mensajeDiv.textContent = 'Error de conexión: ' + err.message;
      mensajeDiv.classList.remove('hidden');
    }
  });
})();
