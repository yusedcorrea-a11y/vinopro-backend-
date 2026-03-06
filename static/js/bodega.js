/**
 * Mi Bodega: dashboard visual, filtros, cantidad, semáforo de guarda, maridajes y PDF.
 * Requiere: window.ERROR_MSGS y window.INFO_REGISTROS_HOY (inyectados por la plantilla).
 */
(function() {
  var SESSION_KEY = 'vino_pro_session_id';
  var botellasCache = [];
  var sortAsc = true;
  var filtroTexto = '';
  var TYPE_COLORS = {
    tinto: '#8b1e3f',
    blanco: '#d4a63a',
    rosado: '#d87093',
    espumoso: '#7fb7be',
    dulce: '#7a5c99'
  };
  var MARIDAJES_RAPIDOS = {
    tinto: 'Carnes rojas, guisos, quesos curados y cocina intensa.',
    blanco: 'Pescados, mariscos, arroces ligeros y quesos suaves.',
    rosado: 'Tapas, pasta, verduras asadas y aves.',
    espumoso: 'Aperitivos, frituras finas, marisco y celebraciones.',
    dulce: 'Foie, quesos azules, postres y fruta madura.'
  };

  function escapeHtml(s) {
    return String(s || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function getSid() {
    try {
      return (localStorage.getItem(SESSION_KEY) || '').trim();
    } catch (e) {
      return '';
    }
  }

  function showFormError(msg) {
    var el = document.getElementById('form-botella-error');
    if (el) {
      el.textContent = msg || '';
      el.style.display = msg ? 'block' : 'none';
    }
  }

  function loadRegistrosHoy() {
    var sid = getSid();
    var el = document.getElementById('registros-hoy-msg');
    if (!el) return;
    if (!sid) { el.textContent = ''; return; }
    fetch('/api/bodega/registros-hoy', { headers: { 'X-Session-ID': sid, 'Accept': 'application/json' } })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        var n = d.registros_hoy || 0;
        var max = d.limite;
        var tpl = (typeof window.INFO_REGISTROS_HOY !== 'undefined') ? window.INFO_REGISTROS_HOY : 'Hoy has añadido {n} de {max} botellas.';
        if (max == null) el.textContent = tpl.replace('{n}', n).replace(' de {max}', '').replace('{max}', '') || ('Hoy has añadido ' + n + ' botellas (PRO).');
        else el.textContent = tpl.replace('{n}', n).replace('{max}', max);
      })
      .catch(function() { el.textContent = ''; });
  }

  function getSortBy() {
    return (document.getElementById('bodega-sort-by') && document.getElementById('bodega-sort-by').value) || 'nombre';
  }

  function getSortDir() { return sortAsc ? 1 : -1; }

  function setOrderDir(asc) {
    sortAsc = asc;
    var btn = document.getElementById('bodega-order-dir');
    if (btn) {
      btn.textContent = sortAsc ? '↑' : '↓';
      btn.title = sortAsc ? 'Ascendente (clic para descendente)' : 'Descendente (clic para ascendente)';
    }
  }

  function getSortedBotellas() {
    var by = getSortBy();
    var dir = getSortDir();
    var list = botellasCache.slice();
    list.sort(function(a, b) {
      var va, vb, cmp;
      switch (by) {
        case 'nombre':
          va = (a.vino_nombre || '').toLowerCase();
          vb = (b.vino_nombre || '').toLowerCase();
          cmp = va < vb ? -1 : (va > vb ? 1 : 0);
          return cmp * dir;
        case 'anada':
          va = a.anada != null ? a.anada : 0;
          vb = b.anada != null ? b.anada : 0;
          return (va - vb) * dir;
        case 'ubicacion':
          va = (a.ubicacion || '').trim().toLowerCase();
          vb = (b.ubicacion || '').trim().toLowerCase();
          cmp = va < vb ? -1 : (va > vb ? 1 : 0);
          return cmp * dir;
        case 'fecha_guardado':
          va = a.fecha_guardado || '';
          vb = b.fecha_guardado || '';
          cmp = va < vb ? -1 : (va > vb ? 1 : 0);
          return cmp * dir;
        case 'cantidad':
          va = a.cantidad != null ? a.cantidad : 0;
          vb = b.cantidad != null ? b.cantidad : 0;
          return (va - vb) * dir;
        default:
          return 0;
      }
    });
    return list;
  }

  function getFilteredBotellas() {
    var list = getSortedBotellas();
    if (!filtroTexto) return list;
    return list.filter(function(b) {
      var nombre = (b.vino_nombre || '').toLowerCase();
      var ubicacion = (b.ubicacion || '').toLowerCase();
      var tipo = (b.tipo || '').toLowerCase();
      return nombre.indexOf(filtroTexto) !== -1 || ubicacion.indexOf(filtroTexto) !== -1 || tipo.indexOf(filtroTexto) !== -1;
    });
  }

  function getPotencialClass(pg) {
    var restantes = pg && pg.anios_restantes_estimados;
    if (restantes == null) return 'amarillo';
    if (restantes < 2) return 'rojo';
    if (restantes <= 5) return 'amarillo';
    return 'verde';
  }

  function getPotencialLabel(pg) {
    var restantes = pg && pg.anios_restantes_estimados;
    if (restantes == null) return 'Semáforo no disponible';
    if (restantes < 2) return 'Beber pronto';
    if (restantes <= 5) return 'Evolucionando';
    return 'Gran potencial';
  }

  function renderDashboard(botellas) {
    var donut = document.getElementById('donut-bodega');
    var legend = document.getElementById('chart-legend');
    if (!donut || !legend) return;
    var counts = {};
    var total = 0;
    (botellas || []).forEach(function(b) {
      var tipo = ((b.tipo || 'tinto') + '').toLowerCase();
      var cantidad = parseInt(b.cantidad, 10) || 1;
      counts[tipo] = (counts[tipo] || 0) + cantidad;
      total += cantidad;
    });
    if (!total) {
      donut.className = 'donut-chart donut-empty';
      donut.style.background = 'conic-gradient(#d4d4d4 0deg, #d4d4d4 360deg)';
      donut.innerHTML = '<div class="chart-center-label"><strong>0</strong><span>botellas</span></div>';
      legend.innerHTML = '<div class="texto-pequeno">Añade botellas para ver el reparto visual de tu bodega.</div>';
      return;
    }
    var start = 0;
    var parts = [];
    var legendHtml = '';
    Object.keys(counts).sort().forEach(function(tipo) {
      var value = counts[tipo];
      var angle = (value / total) * 360;
      var color = TYPE_COLORS[tipo] || '#999';
      parts.push(color + ' ' + start + 'deg ' + (start + angle) + 'deg');
      start += angle;
      legendHtml += '<div class="chart-legend-item"><span class="chart-dot" style="background:' + color + '"></span><span><strong>' +
        escapeHtml(tipo.charAt(0).toUpperCase() + tipo.slice(1)) + '</strong>: ' + value + '</span></div>';
    });
    donut.className = 'donut-chart';
    donut.style.background = 'conic-gradient(' + parts.join(', ') + ')';
    donut.innerHTML = '<div class="chart-center-label"><strong>' + total + '</strong><span>botellas</span></div>';
    legend.innerHTML = legendHtml;
  }

  function updateResumen(botellas) {
    var el = document.getElementById('bodega-resumen');
    if (!el) return;
    var total = botellasCache.length;
    var visibles = (botellas || []).length;
    el.textContent = visibles === total ? (visibles + ' referencias visibles') : (visibles + ' de ' + total + ' referencias');
  }

  function refreshVista() {
    var visibles = getFilteredBotellas();
    renderBotellas(visibles);
    renderDashboard(botellasCache);
    updateResumen(visibles);
  }

  function renderBotellas(botellas) {
    var el = document.getElementById('lista-botellas');
    var bar = document.getElementById('bodega-sort-bar');
    var html = '';
    if (!botellas || botellas.length === 0) {
      if (bar) bar.style.display = botellasCache.length ? 'flex' : 'none';
      html = botellasCache.length ? '<p class="texto-pequeno">No hay resultados para ese filtro.</p>' : '<p class="texto-pequeno">Aún no tienes botellas. Añade una arriba.</p>';
    } else {
      if (bar) bar.style.display = 'flex';
      botellas.forEach(function(b) {
        var pg = (b.potencial_guarda && b.potencial_guarda.mensaje) ? b.potencial_guarda.mensaje : '';
        var pgClass = getPotencialClass(b.potencial_guarda);
        var pgLabel = getPotencialLabel(b.potencial_guarda);
        var nombre = b.vino_nombre || 'Sin nombre';
        var cant = b.cantidad || 1;
        var ubi = (b.ubicacion || '').trim();
        var tipo = ((b.tipo || 'tinto') + '').toLowerCase();
        var bid = b.id || '';
        html += '<div class="resultado-vino en-bd" style="margin-bottom:1rem;" data-botella-id="' + bid + '" data-cant="' + cant + '">';
        if (b.anada) html += '<strong>' + escapeHtml(nombre) + ' ' + b.anada + '</strong> - Cant: ';
        else html += '<strong>' + escapeHtml(nombre) + '</strong> · Cant: ';
        html += '<button type="button" class="btn-cant" data-action="minus" title="Restar 1">−</button> ';
        html += '<span class="cant-value">' + cant + '</span> ';
        html += '<button type="button" class="btn-cant" data-action="plus" title="Sumar 1">+</button>';
        var sep = b.anada ? ' - ' : ' · ';
        var ubiEsc = escapeHtml(ubi);
        html += '<span class="ubicacion-wrap" data-sep="' + sep.replace(/"/g, '&quot;') + '">' + sep + '<span class="ubicacion-text">' + ubiEsc + '</span> <button type="button" class="btn-ubicacion-edit" title="Editar ubicación">✏️</button></span>';
        html += '<p class="texto-pequeno" style="margin-top:0.5rem;"><strong>Tipo:</strong> ' + escapeHtml(tipo.charAt(0).toUpperCase() + tipo.slice(1)) + '</p>';
        html += '<div class="potencial-badge ' + pgClass + '" title="' + escapeHtml(pg) + '">● ' + escapeHtml(pgLabel) + '</div>';
        if (pg) html += '<p class="texto-pequeno">' + escapeHtml(pg) + '</p>';
        html += '<div class="acciones-bodega">';
        html += '<button type="button" class="btn btn-outline btn-mini btn-maridaje" data-tipo="' + escapeHtml(tipo) + '">Sugerencia de maridaje</button>';
        html += '<button type="button" class="btn btn-outline btn-mini btn-abrir-ahora" data-id="' + bid + '">Abrir ahora</button>';
        html += '<button type="button" class="btn btn-eliminar btn-mini" data-id="' + bid + '">Eliminar</button>';
        html += '</div>';
        html += '<div class="maridaje-tip hidden"></div>';
        html += '</div>';
      });
    }
    el.innerHTML = html;

    el.querySelectorAll('.btn-eliminar').forEach(function(btn) {
      btn.addEventListener('click', function() {
        if (!confirm('¿Eliminar esta botella?')) return;
        var sid2 = getSid();
        if (!sid2) return;
        fetch('/api/bodega/botellas/' + btn.getAttribute('data-id'), {
          method: 'DELETE',
          headers: { 'X-Session-ID': sid2, 'Accept': 'application/json' }
        }).then(function() { loadBodega(); loadValoracion(); });
      });
    });

    el.querySelectorAll('.btn-cant').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var row = btn.closest('.resultado-vino');
        var bid = row.getAttribute('data-botella-id');
        var cant = parseInt(row.getAttribute('data-cant'), 10) || 1;
        var action = btn.getAttribute('data-action');
        var sid2 = getSid();
        if (!sid2 || !bid) return;
        if (action === 'minus') {
          if (cant <= 1) {
            if (!confirm('¿Eliminar?')) return;
            fetch('/api/bodega/botellas/' + bid, {
              method: 'DELETE',
              headers: { 'X-Session-ID': sid2, 'Accept': 'application/json' }
            }).then(function() { loadBodega(); loadValoracion(); });
            return;
          }
          cant = cant - 1;
        } else {
          cant = cant + 1;
        }
        fetch('/api/bodega/botellas/' + bid, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', 'X-Session-ID': sid2, 'Accept': 'application/json' },
          body: JSON.stringify({ cantidad: cant })
        })
          .then(function(r) { return r.json(); })
          .then(function(d) {
            if (d.success) { loadBodega(); loadValoracion(); }
            else alert(d.detail || 'Error');
          })
          .catch(function() { alert('Error al actualizar.'); });
      });
    });

    el.querySelectorAll('.btn-abrir-ahora').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var row = btn.closest('.resultado-vino');
        var bid = btn.getAttribute('data-id');
        var cant = parseInt(row.getAttribute('data-cant'), 10) || 1;
        var sid2 = getSid();
        if (!sid2 || !bid) return;
        if (!confirm('¿Abrir una botella ahora? Se descontará 1 unidad del stock.')) return;
        if (cant <= 1) {
          fetch('/api/bodega/botellas/' + bid, {
            method: 'DELETE',
            headers: { 'X-Session-ID': sid2, 'Accept': 'application/json' }
          }).then(function() { loadBodega(); loadValoracion(); });
          return;
        }
        fetch('/api/bodega/botellas/' + bid, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', 'X-Session-ID': sid2, 'Accept': 'application/json' },
          body: JSON.stringify({ cantidad: cant - 1 })
        }).then(function() { loadBodega(); loadValoracion(); });
      });
    });

    el.querySelectorAll('.btn-maridaje').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var row = btn.closest('.resultado-vino');
        var tip = row.querySelector('.maridaje-tip');
        var tipo = (btn.getAttribute('data-tipo') || 'tinto').toLowerCase();
        if (!tip) return;
        if (!tip.classList.contains('hidden')) {
          tip.classList.add('hidden');
          tip.innerHTML = '';
          return;
        }
        tip.innerHTML = '<strong>Maridaje rápido:</strong> ' + escapeHtml(MARIDAJES_RAPIDOS[tipo] || 'Cocina mediterránea, quesos y platos de intensidad media.');
        tip.classList.remove('hidden');
      });
    });
  }

  function loadBodega() {
    var el = document.getElementById('lista-botellas');
    var sid = getSid();
    if (!sid) {
      el.innerHTML = '<p class="mensaje info">Sin sesión. Recarga la página para generar una.</p>';
      var bar = document.getElementById('bodega-sort-bar');
      if (bar) bar.style.display = 'none';
      return;
    }
    fetch('/api/bodega', {
      method: 'GET',
      headers: { 'X-Session-ID': sid, 'Accept': 'application/json' }
    })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        botellasCache = d.botellas || [];
        refreshVista();
      })
      .catch(function() {
        el.innerHTML = '<p class="mensaje error">Error al cargar. Revisa la consola.</p>';
        var bar = document.getElementById('bodega-sort-bar');
        if (bar) bar.style.display = 'none';
      });
  }

  function loadValoracion() {
    var el = document.getElementById('valoracion');
    var sid = getSid();
    if (!sid) {
      el.textContent = 'Sin sesión.';
      return;
    }
    fetch('/api/bodega/valoracion', {
      method: 'GET',
      headers: { 'X-Session-ID': sid, 'Accept': 'application/json' }
    })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        el.innerHTML = 'Total botellas: <strong>' + (d.total_botellas || 0) + '</strong> · Valoración: <strong>' + (d.valoracion_estimada || 0) + ' €</strong>';
      })
      .catch(function() { el.textContent = 'Error'; });
  }

  function init() {
    document.getElementById('form-botella').addEventListener('submit', function(e) {
      e.preventDefault();
      var sid = getSid();
      if (!sid) { alert('Sin sesión. Recarga la página.'); return; }
      var anadaVal = document.getElementById('anada').value.trim();
      var payload = {
        vino_nombre: document.getElementById('vino_nombre').value.trim(),
        cantidad: parseInt(document.getElementById('cantidad').value, 10) || 1,
        anada: anadaVal ? parseInt(anadaVal, 10) : null,
        ubicacion: document.getElementById('ubicacion').value.trim(),
        tipo: (document.getElementById('tipo_vino').value || 'tinto').trim().toLowerCase()
      };
      if (!payload.vino_nombre) { alert('Nombre obligatorio.'); return; }
      showFormError('');
      fetch('/api/bodega/botellas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Session-ID': sid, 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function(r) { return r.json().then(function(d) { return { ok: r.ok, status: r.status, data: d }; }); })
        .then(function(res) {
          if (res.ok && res.data.success) {
            loadBodega();
            loadValoracion();
            loadRegistrosHoy();
            document.getElementById('form-botella').reset();
            document.getElementById('anada').value = new Date().getFullYear();
            document.getElementById('tipo_vino').value = 'tinto';
            return;
          }
          if (res.status === 400) {
            var msg = (typeof res.data.detail === 'string') ? res.data.detail : (res.data.detail && res.data.detail.message_key && window.ERROR_MSGS && window.ERROR_MSGS[res.data.detail.message_key]) ? window.ERROR_MSGS[res.data.detail.message_key] : (res.data.detail && res.data.detail.message_key) || res.data.detail || 'Nombre de vino no válido';
            showFormError(msg);
            return;
          }
          if (res.status === 429) {
            var msg429 = (window.ERROR_MSGS && window.ERROR_MSGS.limite_diario) || 'Límite diario alcanzado.';
            showFormError(msg429);
            return;
          }
          if (res.status === 403 && res.data.detail && res.data.detail.redirect) {
            var msg403 = res.data.detail.message || 'Límite alcanzado.';
            if (confirm(msg403 + '\n\n¿Ir a Planes?')) window.location.href = res.data.detail.redirect;
            return;
          }
          alert(res.data.detail && (res.data.detail.message || res.data.detail.message_key || res.data.detail) || 'Error');
        })
        .catch(function() { showFormError('Error de conexión. Comprueba la red e inténtalo de nuevo.'); });
    });

    document.getElementById('btn-pdf-bodega').addEventListener('click', function(e) {
      e.preventDefault();
      var sid = getSid();
      if (!sid) { alert('Sin sesión.'); return; }
      var x = new XMLHttpRequest();
      x.open('GET', '/informes/bodega');
      x.setRequestHeader('X-Session-ID', sid);
      x.responseType = 'blob';
      x.onload = function() {
        if (x.status !== 200) { alert('Error PDF.'); return; }
        var a = document.createElement('a');
        a.href = window.URL.createObjectURL(x.response);
        a.download = 'informe_bodega.pdf';
        a.click();
      };
      x.send();
    });

    document.getElementById('bodega-sort-by').addEventListener('change', function() {
      if (this.value === 'anada') setOrderDir(false);
      else setOrderDir(true);
      refreshVista();
    });

    document.getElementById('bodega-order-dir').addEventListener('click', function() {
      sortAsc = !sortAsc;
      setOrderDir(sortAsc);
      refreshVista();
    });

    document.getElementById('bodega-search').addEventListener('input', function() {
      filtroTexto = (this.value || '').trim().toLowerCase();
      refreshVista();
    });

    document.getElementById('lista-botellas').addEventListener('click', function(e) {
      var btn = e.target.closest('.btn-ubicacion-edit');
      if (!btn) return;
      var wrap = btn.closest('.ubicacion-wrap');
      var row = wrap.closest('.resultado-vino');
      var bid = row.getAttribute('data-botella-id');
      var textSpan = wrap.querySelector('.ubicacion-text');
      var currentVal = textSpan ? textSpan.textContent : '';
      var sep = wrap.getAttribute('data-sep') || ' - ';
      var sid2 = getSid();
      if (!sid2 || !bid) return;
      var inp = document.createElement('input');
      inp.type = 'text';
      inp.className = 'input-ubicacion-inline';
      inp.value = currentVal;
      wrap.innerHTML = '';
      wrap.appendChild(inp);
      inp.focus();
      var editingDone = false;
      function save() {
        if (editingDone) return;
        editingDone = true;
        var newVal = inp.value.trim();
        fetch('/api/bodega/botellas/' + bid, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', 'X-Session-ID': sid2, 'Accept': 'application/json' },
          body: JSON.stringify({ ubicacion: newVal })
        })
          .then(function(r) { return r.json(); })
          .then(function(d) {
            if (d.success) { loadBodega(); loadValoracion(); }
            else { editingDone = false; alert(d.detail || 'Error'); }
          })
          .catch(function() { editingDone = false; alert('Error al actualizar.'); });
      }
      function cancel() {
        if (editingDone) return;
        editingDone = true;
        wrap.innerHTML = sep + '<span class="ubicacion-text">' + escapeHtml(currentVal) + '</span> <button type="button" class="btn-ubicacion-edit" title="Editar ubicación">✏️</button>';
      }
      inp.addEventListener('keydown', function(ev) {
        if (ev.key === 'Enter') { ev.preventDefault(); save(); }
        if (ev.key === 'Escape') { ev.preventDefault(); cancel(); }
      });
      inp.addEventListener('blur', function() { if (!editingDone) save(); });
    });

    document.getElementById('anada').value = new Date().getFullYear();
    document.getElementById('tipo_vino').value = 'tinto';
    loadValoracion();
    loadBodega();
    loadRegistrosHoy();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
