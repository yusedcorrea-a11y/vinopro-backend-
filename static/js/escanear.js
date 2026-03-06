/**
 * Escanear etiqueta: formulario imagen/texto/código de barras y resultado.
 * Requiere: app.js (getSessionId para X-Session-ID).
 */
(function() {
  const form = document.getElementById('formEscaneo');
  const cargando = document.getElementById('cargando');
  const errorDiv = document.getElementById('error');
  const resultadoDiv = document.getElementById('resultado');

  if (!form) return;

  function guardarConsultaId(id) {
    try {
      let list = JSON.parse(localStorage.getItem('ultimasConsultas') || '[]');
      list = [id, ...list.filter(x => x !== id)].slice(0, 10);
      localStorage.setItem('ultimasConsultas', JSON.stringify(list));
    } catch (_) {}
  }

  function icono(c) { return '<span class="icono">' + c + '</span>'; }
  function slugify(s) {
    if (!s) return '';
    return String(s).toLowerCase().trim()
      .replace(/\s+/g, '-')
      .replace(/[áàäâ]/g, 'a').replace(/[éèëê]/g, 'e').replace(/[íìïî]/g, 'i')
      .replace(/[óòöô]/g, 'o').replace(/[úùüû]/g, 'u').replace(/ñ/g, 'n')
      .replace(/[^a-z0-9-]/g, '');
  }
  function escapeHtml(s) {
    if (s == null) return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function renderNoReconocido(esPro, mensaje) {
    var div = document.createElement('div');
    div.className = 'resultado-vino resultado-no-reconocido';
    var html = '<h3>No pudimos leer la etiqueta</h3>';
    html += '<p class="aviso-no-reconocido">' + escapeHtml(mensaje) + '</p>';
    html += '<p>Prueba con otra foto más nítida o <strong>escribe el nombre del vino</strong> en el cuadro de texto de arriba y pulsa Escanear.</p>';
    html += '<p class="premium-sutil">Con la opción gratuita ya tienes escaneo, sumiller y bodega. Si te pasas a Premium podrás registrar cualquier vino y ofrecerlo a otros. <a href="/planes">Ver planes</a></p>';
    div.innerHTML = html;
    return div;
  }

  function renderVino(vino, enBd, consultaId, key, mensaje) {
    const div = document.createElement('div');
    div.className = 'resultado-vino ' + (enBd ? 'en-bd' : 'externo');
    let html = '<h3>' + escapeHtml(vino.nombre || 'Sin nombre') + '</h3>';
    if (!enBd && mensaje) {
      html += '<div class="aviso-externo">' + escapeHtml(mensaje) + '</div>';
    }
    html += '<div class="fila-campo">' + icono('🏠') + '<strong>Bodega:</strong> ' + escapeHtml(vino.bodega || '—') + '</div>';
    html += '<div class="fila-campo">' + icono('📍') + '<strong>Región:</strong> ' + escapeHtml(vino.region || '—') + '</div>';
    html += '<div class="fila-campo">' + icono('🌍') + '<strong>País:</strong> ' + escapeHtml(vino.pais || '—') + '</div>';
    html += '<div class="fila-campo">' + icono('🍷') + '<strong>Tipo:</strong> ' + escapeHtml((vino.tipo || '—').toString()) + '</div>';
    html += '<div class="fila-campo">' + icono('⭐') + '<strong>Puntuación:</strong> ' + (vino.puntuacion != null ? vino.puntuacion : '—') + '</div>';
    html += '<div class="fila-campo">' + icono('💰') + '<strong>Precio estimado:</strong> ' + escapeHtml(vino.precio_estimado || '—') + '</div>';
    html += '<div class="campo"><strong>Descripción:</strong> ' + escapeHtml(vino.descripcion || '—') + '</div>';
    html += '<div class="campo"><strong>Notas de cata:</strong> ' + escapeHtml(vino.notas_cata || '—') + '</div>';
    html += '<div class="campo"><strong>Maridaje:</strong> ' + escapeHtml(vino.maridaje || '—') + '</div>';
    if (consultaId) {
      html += '<div class="consulta-id-box"><strong>Consulta ID</strong> (úsalo en Preguntar):<br><code>' + escapeHtml(consultaId) + '</code></div>';
      guardarConsultaId(consultaId);
    }
    html += '<p style="margin-top:1rem"><button type="button" class="btn btn-dorado" id="btnPdfCata">Exportar informe de cata (PDF)</button></p>';
    var vinoIdComprar = (key && key.trim()) ? encodeURIComponent(key.trim()) : slugify(vino.nombre || '');
    if (vinoIdComprar) {
      html += '<div class="acciones-escaneo"><a href="/vino/' + vinoIdComprar + '/comprar" target="_blank" rel="noopener noreferrer" class="btn-comprar btn btn-dorado">🛒 Comprar este vino</a></div>';
    }
    if (!enBd && vino.nombre) {
      html += '<p style="margin-top:0.5rem"><a href="#" class="btn btn-dorado" id="btnRegistrarEste">Registrar este vino</a></p>';
    }
    if (!enBd) {
      html += '<p class="premium-sutil">Con la opción gratuita ya tienes escaneo, sumiller y bodega. Si te pasas a Premium podrás registrar cualquier vino y ofrecerlo a otros. <a href="/planes">Ver planes</a></p>';
    }
    div.innerHTML = html;
    var btnPdf = div.querySelector('#btnPdfCata');
    if (btnPdf) {
      btnPdf.addEventListener('click', function() {
        fetch('/informes/cata', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ vino: vino, notas_adicionales: '' }) })
          .then(function(r) { return r.blob(); })
          .then(function(blob) {
            var a = document.createElement('a');
            a.href = window.URL.createObjectURL(blob);
            a.download = 'informe_cata.pdf';
            a.click();
          }).catch(function() { alert('Error al generar PDF.'); });
      });
    }
    if (!enBd && vino.nombre) {
      var btnReg = div.querySelector('#btnRegistrarEste');
      if (btnReg) btnReg.addEventListener('click', function(e) {
        e.preventDefault();
        const datos = {
          nombre: vino.nombre,
          bodega: vino.bodega || 'No especificada',
          region: vino.region || 'Por determinar',
          pais: vino.pais || 'Desconocido',
          tipo: vino.tipo || 'tinto',
          puntuacion: vino.puntuacion ?? null,
          precio_estimado: vino.precio_estimado || '',
          descripcion: vino.descripcion || '',
          notas_cata: vino.notas_cata || '',
          maridaje: vino.maridaje || ''
        };
        sessionStorage.setItem('vinoParaRegistrar', JSON.stringify(datos));
        window.location.href = '/registrar';
      });
    }
    return div;
  }

  var MAX_SIZE_MB = 6;
  var MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;
  var FETCH_TIMEOUT_MS = 60000;
  var SUBMIT_DEBOUNCE_MS = 1200;
  var isSubmitting = false;
  var lastSubmitAt = 0;
  var submitBtn = form.querySelector('button[type="submit"]');

  function setSubmittingState(active) {
    isSubmitting = !!active;
    if (submitBtn) submitBtn.disabled = !!active;
    if (btnCapturar) btnCapturar.disabled = !!active;
    if (btnAbrirCamara) btnAbrirCamara.disabled = !!active;
  }

  function canSubmitNow() {
    var now = Date.now();
    if (isSubmitting) return false;
    if (now - lastSubmitAt < SUBMIT_DEBOUNCE_MS) return false;
    lastSubmitAt = now;
    return true;
  }

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!canSubmitNow()) return;
    errorDiv.classList.add('hidden');
    resultadoDiv.classList.add('hidden');
    const imagen = document.getElementById('imagen').files[0];
    const texto = document.getElementById('texto').value.trim();
    const codigo_barras = document.getElementById('codigo_barras').value.trim();
    if (!imagen && !texto && !codigo_barras) {
      errorDiv.textContent = 'Introduce al menos: imagen, texto o código de barras.';
      errorDiv.classList.remove('hidden');
      return;
    }
    if (imagen && imagen.size > MAX_SIZE_BYTES) {
      errorDiv.textContent = 'La imagen es demasiado grande (máx. ' + MAX_SIZE_MB + ' MB). Redúcela o usa una foto más pequeña. También puedes escribir el nombre del vino abajo.';
      errorDiv.classList.remove('hidden');
      return;
    }
    if (imagen && imagen.type && imagen.type.indexOf('heic') !== -1) {
      errorDiv.textContent = 'Formato HEIC no soportado. Guarda la foto como JPG o PNG en tu móvil, o escribe el nombre del vino abajo.';
      errorDiv.classList.remove('hidden');
      return;
    }
    setSubmittingState(true);
    cargando.classList.remove('hidden');
    const formData = new FormData();
    if (imagen) formData.append('imagen', imagen);
    if (texto) formData.append('texto', texto);
    if (codigo_barras) formData.append('codigo_barras', codigo_barras);
    try {
      const opts = { method: 'POST', body: formData };
      if (typeof window.getSessionId === 'function') {
        var sid = window.getSessionId();
        if (sid) opts.headers = { 'X-Session-ID': sid };
      }
      var controller = new AbortController();
      var timeoutId = setTimeout(function() { controller.abort(); }, FETCH_TIMEOUT_MS);
      opts.signal = controller.signal;
      const r = await fetch('/escanear', opts);
      clearTimeout(timeoutId);
      var data;
      try {
        data = await r.json();
      } catch (_) {
        data = { message: 'Respuesta inválida del servidor.' };
      }
      cargando.classList.add('hidden');
      setSubmittingState(false);
      if (!r.ok) {
        var msg = data.message || data.detail || 'Error al escanear';
        if (typeof data.detail === 'string') msg = data.detail;
        if (Array.isArray(data.detail) && data.detail[0]) {
          var d = data.detail[0];
          msg = (d.msg || (d.loc && d.loc.join(' ')) || msg);
        }
        if (r.status === 400 && (msg.indexOf('imagen') !== -1 || msg.indexOf('texto') !== -1)) {
          msg = 'No pudimos leer la imagen. Prueba con otra foto (JPG o PNG, menos de ' + MAX_SIZE_MB + ' MB) o escribe el nombre del vino en el cuadro de texto.';
        }
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
        return;
      }
      if (data.reconocido === false) {
        resultadoDiv.innerHTML = '';
        resultadoDiv.appendChild(renderNoReconocido(!!data.es_pro, data.mensaje || 'No pudimos leer la etiqueta.'));
        resultadoDiv.classList.remove('hidden');
        return;
      }
      var vino = data.vino || {};
      var enBd = !!data.encontrado_en_bd;
      resultadoDiv.innerHTML = '';
      resultadoDiv.appendChild(renderVino(vino, enBd, data.consulta_id, data.vino_key != null ? data.vino_key : data.key, data.mensaje));
      resultadoDiv.classList.remove('hidden');
    } catch (err) {
      cargando.classList.add('hidden');
      setSubmittingState(false);
      if (err.name === 'AbortError') {
        errorDiv.textContent = 'La operación tardó demasiado. Prueba con una imagen más pequeña o escribe el nombre del vino en el cuadro de texto.';
      } else {
        errorDiv.textContent = 'Error de conexión: ' + (err.message || 'Comprueba tu conexión e inténtalo de nuevo.');
      }
      errorDiv.classList.remove('hidden');
    }
  });

  var cameraStream = null;
  var cameraWrap = document.getElementById('camera-wrap');
  var cameraPreview = document.getElementById('cameraPreview');
  var btnAbrirCamara = document.getElementById('btnAbrirCamara');
  var btnCapturar = document.getElementById('btnCapturar');
  var btnCerrarCamara = document.getElementById('btnCerrarCamara');

  function cerrarCamara() {
    if (cameraStream) {
      cameraStream.getTracks().forEach(function(t) { t.stop(); });
      cameraStream = null;
    }
    if (cameraWrap) cameraWrap.classList.add('hidden');
  }

  function enviarFormData(formData) {
    if (!canSubmitNow()) return;
    errorDiv.classList.add('hidden');
    resultadoDiv.classList.add('hidden');
    setSubmittingState(true);
    cargando.classList.remove('hidden');
    var opts = { method: 'POST', body: formData };
    if (typeof window.getSessionId === 'function') {
      var sid = window.getSessionId();
      if (sid) opts.headers = { 'X-Session-ID': sid };
    }
    var controller = new AbortController();
    var timeoutId = setTimeout(function() { controller.abort(); }, FETCH_TIMEOUT_MS);
    opts.signal = controller.signal;
    fetch('/escanear', opts)
      .then(function(r) {
        clearTimeout(timeoutId);
        return r.json().then(function(data) { return { ok: r.ok, data: data }; });
      })
      .then(function(res) {
        var data = res.data;
        cargando.classList.add('hidden');
        setSubmittingState(false);
        if (!res.ok) {
          errorDiv.textContent = (data && (data.detail || data.message)) || 'Error al escanear';
          errorDiv.classList.remove('hidden');
          return;
        }
        if (data.reconocido === false) {
          resultadoDiv.innerHTML = '';
          resultadoDiv.appendChild(renderNoReconocido(!!data.es_pro, data.mensaje || 'No pudimos leer la etiqueta.'));
          resultadoDiv.classList.remove('hidden');
          return;
        }
        var vino = data.vino || {};
        resultadoDiv.innerHTML = '';
        resultadoDiv.appendChild(renderVino(vino, !!data.encontrado_en_bd, data.consulta_id, data.vino_key != null ? data.vino_key : data.key, data.mensaje));
        resultadoDiv.classList.remove('hidden');
      })
      .catch(function(err) {
        clearTimeout(timeoutId);
        cargando.classList.add('hidden');
        setSubmittingState(false);
        errorDiv.textContent = err.name === 'AbortError' ? 'Operación tardó demasiado.' : ('Error: ' + (err.message || ''));
        errorDiv.classList.remove('hidden');
      });
  }

  function iniciarCamara() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      if (errorDiv) { errorDiv.textContent = 'Tu navegador no soporta la cámara. Usa el botón "Subir imagen" o escribe el nombre.'; errorDiv.classList.remove('hidden'); }
      return;
    }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
      .then(function(stream) {
        cameraStream = stream;
        if (cameraPreview) cameraPreview.srcObject = stream;
        if (cameraWrap) cameraWrap.classList.remove('hidden');
      })
      .catch(function() {
        if (errorDiv) { errorDiv.textContent = 'No se pudo acceder a la cámara. Comprueba los permisos o usa "Subir imagen".'; errorDiv.classList.remove('hidden'); }
      });
  }

  if (btnAbrirCamara) btnAbrirCamara.addEventListener('click', iniciarCamara);
  if (btnCerrarCamara) btnCerrarCamara.addEventListener('click', cerrarCamara);

  if (btnCapturar && cameraPreview) {
    btnCapturar.addEventListener('click', function() {
      if (isSubmitting) return;
      if (!cameraStream || !cameraPreview.videoWidth) return;
      var canvas = document.createElement('canvas');
      canvas.width = cameraPreview.videoWidth;
      canvas.height = cameraPreview.videoHeight;
      var ctx = canvas.getContext('2d');
      ctx.drawImage(cameraPreview, 0, 0);
      canvas.toBlob(function(blob) {
        if (!blob) return;
        cerrarCamara();
        var formData = new FormData();
        formData.append('imagen', blob, 'captura.jpg');
        var texto = document.getElementById('texto');
        var codigo = document.getElementById('codigo_barras');
        if (texto && texto.value.trim()) formData.append('texto', texto.value.trim());
        if (codigo && codigo.value.trim()) formData.append('codigo_barras', codigo.value.trim());
        enviarFormData(formData);
      }, 'image/jpeg', 0.9);
    });
  }

  // La cámara solo se abre cuando el usuario pulsa "Abrir cámara y escanear" (no al entrar en la página).
})();
