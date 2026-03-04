/**
 * Panel generador de QRs personalizados (networking Turín).
 * Genera QR, descarga PNG, lista contactos.
 */
(function() {
  'use strict';

  var form = document.getElementById('form-qr');
  var result = document.getElementById('qr-result');
  var qrUrl = document.getElementById('qr-url');
  var qrImg = document.getElementById('qr-img');
  var qrDescargar = document.getElementById('qr-descargar');
  var loading = document.getElementById('qr-loading');
  var tabla = document.getElementById('qr-tabla');
  var tablaBody = document.getElementById('qr-tabla-body');
  var emptyMsg = document.getElementById('qr-empty');

  function showResult(codigo, url) {
    result.classList.add('visible');
    qrUrl.textContent = url;
    qrImg.src = '/api/qr/descargar/' + encodeURIComponent(codigo);
    qrDescargar.href = '/api/qr/descargar/' + encodeURIComponent(codigo);
    qrDescargar.download = 'vino-pro-qr-' + codigo + '.png';
  }

  function loadContactos() {
    if (!tablaWrap) return;
    loading.style.display = 'block';
    fetch('/api/qr/contactos', { headers: { 'Accept': 'application/json' } })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        loading.style.display = 'none';
        var contactos = data.contactos || [];
        if (contactos.length === 0) {
          if (emptyMsg) emptyMsg.style.display = 'block';
          return;
        }
        if (emptyMsg) emptyMsg.style.display = 'none';
        if (tabla) tabla.style.display = 'table';
        if (tablaBody) {
          tablaBody.innerHTML = '';
          contactos.forEach(function(c) {
            var esc = c.escaneado ? '<span class="badge si">Sí</span>' : '<span class="badge no">No</span>';
            var fecha = (c.fecha_escaneo || '').slice(0, 10);
            var pais = c.pais_escaneo || '–';
            var tr = document.createElement('tr');
            tr.innerHTML = '<td>' + (c.nombre || '') + '</td><td>' + (c.empresa || '') + '</td><td>' + (c.idioma || '') + '</td><td>' + esc + '</td><td>' + fecha + '</td><td>' + pais + '</td>';
            tablaBody.appendChild(tr);
          });
        }
      })
      .catch(function() {
        loading.style.display = 'none';
        if (emptyMsg) { emptyMsg.textContent = 'Error al cargar contactos.'; emptyMsg.style.display = 'block'; }
      });
  }

  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      var nombre = (document.getElementById('qr-nombre') || {}).value;
      var empresa = (document.getElementById('qr-empresa') || {}).value || '';
      var idioma = (document.getElementById('qr-idioma') || {}).value || 'it';
      if (!nombre || !nombre.trim()) return;
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.textContent = 'Generando…'; }
      fetch('/api/qr/generar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ nombre: nombre.trim(), empresa: empresa.trim(), idioma: idioma }),
      })
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (btn) { btn.disabled = false; btn.textContent = form.getAttribute('data-btn-text') || 'Generar QR'; }
          if (data.ok && data.codigo && data.url) {
            showResult(data.codigo, data.url);
            loadContactos();
          } else {
            alert(data.detail || 'Error al generar');
          }
        })
        .catch(function() {
          if (btn) { btn.disabled = false; btn.textContent = form.getAttribute('data-btn-text') || 'Generar QR'; }
          alert('Error de conexión');
        });
    });
    var btn = form.querySelector('button[type="submit"]');
    if (btn) form.setAttribute('data-btn-text', btn.textContent);
  }

  loadContactos();
})();
