/**
 * Preguntar al experto en vinos: formulario, voz, historial y respuesta.
 * Requiere: app.js (getSessionId), DOM con formPregunta, consulta_id, texto, etc.
 */
(function() {
  const form = document.getElementById('formPregunta');
  const vinoContextoSelect = document.getElementById('vino_contexto');
  const errorDiv = document.getElementById('error');
  const respuestaDiv = document.getElementById('respuesta');
  const modoSelect = document.getElementById('modo_sumiller');
  const textoInput = document.getElementById('texto');
  const btnMic = document.getElementById('btn-mic');
  const chipsContainer = document.getElementById('chips_preguntas_recientes');

  if (!form) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let isListening = false;

  function guardarInteraccionVoz(pregunta, respuesta) {
    try {
      var list = JSON.parse(localStorage.getItem('vino_pro_voice_history') || '[]');
      list.unshift({ pregunta: pregunta, respuesta: respuesta, fecha: new Date().toISOString() });
      list = list.slice(0, 5);
      localStorage.setItem('vino_pro_voice_history', JSON.stringify(list));
    } catch (_) {}
  }

  function setMicListening(listening) {
    isListening = listening;
    if (!btnMic) return;
    btnMic.classList.toggle('listening', listening);
    btnMic.title = listening ? 'Escuchando...' : 'Preguntar por voz';
    btnMic.setAttribute('aria-label', listening ? 'Escuchando' : 'Activar micrófono para hablar');
    btnMic.textContent = listening ? 'Escuchando...' : '🎤';
  }

  function iniciarReconocimientoVoz() {
    if (!SpeechRecognition) {
      errorDiv.textContent = 'Tu navegador no soporta reconocimiento de voz. Prueba con Chrome o Edge.';
      errorDiv.classList.remove('hidden');
      return;
    }
    if (!recognition) {
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'es-ES';
      recognition.onresult = function(e) {
        var transcript = (e.results[0] && e.results[0][0]) ? e.results[0][0].transcript : '';
        if (transcript.trim()) {
          textoInput.value = transcript.trim();
          window._ultimaPreguntaFueVoz = true;
          form.requestSubmit();
        }
        setMicListening(false);
      };
      recognition.onend = function() { setMicListening(false); };
      recognition.onerror = function(e) {
        setMicListening(false);
        if (e.error === 'not-allowed') {
          errorDiv.textContent = 'Permiso de micrófono denegado. Activa el micrófono en la configuración del navegador para usar la voz.';
        } else if (e.error === 'no-speech') {
          errorDiv.textContent = 'No se detectó voz. Vuelve a intentarlo.';
        } else {
          errorDiv.textContent = 'Error de voz: ' + (e.error || 'desconocido');
        }
        errorDiv.classList.remove('hidden');
      };
    }
    errorDiv.classList.add('hidden');
    setMicListening(true);
    try {
      recognition.start();
    } catch (err) {
      setMicListening(false);
      errorDiv.textContent = 'No se pudo iniciar el micrófono. Comprueba que has dado permiso.';
      errorDiv.classList.remove('hidden');
    }
  }

  if (btnMic) btnMic.addEventListener('click', iniciarReconocimientoVoz);

  function hablarTexto(texto) {
    if (!window.speechSynthesis) {
      errorDiv.textContent = 'Tu navegador no soporta la lectura en voz alta.';
      errorDiv.classList.remove('hidden');
      return;
    }
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(texto);
    u.lang = 'es-ES';
    u.rate = 0.95;
    var voces = speechSynthesis.getVoices();
    var es = voces.find(function(v) { return v.lang.startsWith('es'); });
    if (es) u.voice = es;
    window.speechSynthesis.speak(u);
  }

  if (window.speechSynthesis) {
    speechSynthesis.getVoices();
    window.addEventListener('voiceschanged', function() { speechSynthesis.getVoices(); });
  }

  /* Modo: ocultar fila entera para usuarios gratis; PRO: auto Local sin internet */
  (function initModoPremium() {
    var sid = getSessionId();
    if (!sid) return;
    var wrapRow = document.getElementById('wrap_modo_row');
    fetch('/api/check-limit', { headers: { 'X-Session-ID': sid, 'Accept': 'application/json' } })
      .then(function(r) { return r.ok ? r.json() : {}; })
      .then(function(d) {
        var esPro = !!d.es_pro;
        var wrap = document.getElementById('wrap_modo_premium');
        if (wrap) wrap.style.display = esPro ? 'none' : '';
        if (wrapRow) wrapRow.style.display = esPro ? 'flex' : 'none';
        if (!esPro) {
          if (modoSelect) modoSelect.value = 'nube';
          return;
        }
        var optLocal = modoSelect && modoSelect.querySelector('option[value="local"]');
        if (optLocal) optLocal.disabled = false;
        if (!navigator.onLine && modoSelect) modoSelect.value = 'local';
        window.addEventListener('offline', function() { if (modoSelect) modoSelect.value = 'local'; });
        window.addEventListener('online', function() { if (modoSelect) modoSelect.value = 'nube'; });
      })
      .catch(function() { if (wrapRow) wrapRow.style.display = 'none'; });
  })();

  function ensureSessionId() {
    try {
      var key = 'vino_pro_session_id';
      var sid = localStorage.getItem(key);
      if (sid && sid.trim()) return sid.trim();
      var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
      localStorage.setItem(key, uuid);
      return uuid;
    } catch (_) { return ''; }
  }
  function getSessionId() {
    ensureSessionId();
    try {
      if (typeof window.getSessionId === 'function') {
        var fromApp = (window.getSessionId() || '').trim();
        if (fromApp) return fromApp;
      }
      return (localStorage.getItem('vino_pro_session_id') || '').trim();
    } catch (_) { return ''; }
  }

  /** Idioma de la app (cookie / html lang) para que el chatbot responda en el idioma del usuario. */
  function getAppLang() {
    try {
      var htmlLang = (document.documentElement.getAttribute('lang') || '').trim().toLowerCase().slice(0, 2);
      if (htmlLang) return htmlLang;
      var m = (document.cookie || '').match(/vino_pro_lang=([^;]+)/);
      if (m && m[1]) return m[1].trim().toLowerCase().slice(0, 2);
    } catch (_) {}
    return 'es';
  }

  function cargarVinoContexto() {
    var sid = getSessionId();
    if (!vinoContextoSelect || !sid) return;
    vinoContextoSelect.innerHTML = '<option value="">Sin vino en contexto</option>';
    fetch('/historial-escaneos', { headers: { 'X-Session-ID': sid } })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        (d.historial || []).slice(0, 15).forEach(function(h) {
          var id = h.consulta_id || '';
          var nombre = h.vino_nombre || 'Sin nombre';
          var opt = document.createElement('option');
          opt.value = id;
          opt.textContent = 'Vino escaneado: ' + nombre;
          vinoContextoSelect.appendChild(opt);
        });
      })
      .catch(function() {});
  }
  cargarVinoContexto();

  var chipsHideTimer = null;
  function mostrarChipsPreguntasRecientes() {
    if (!chipsContainer) return;
    try {
      var list = JSON.parse(localStorage.getItem('vino_pro_voice_history') || '[]');
      var preguntas = list.slice(0, 5).map(function(x) { return x.pregunta; }).filter(Boolean);
      chipsContainer.innerHTML = '';
      if (preguntas.length === 0) { chipsContainer.hidden = true; return; }
      preguntas.forEach(function(p) {
        var chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'chip-pregunta';
        chip.textContent = p.length > 50 ? p.slice(0, 47) + '…' : p;
        chip.title = p;
        chip.addEventListener('click', function() {
          if (textoInput) textoInput.value = p;
          chipsContainer.hidden = true;
        });
        chipsContainer.appendChild(chip);
      });
      chipsContainer.hidden = false;
    } catch (_) { chipsContainer.hidden = true; }
  }
  function ocultarChipsConRetraso() {
    if (chipsHideTimer) clearTimeout(chipsHideTimer);
    chipsHideTimer = setTimeout(function() { if (chipsContainer) chipsContainer.hidden = true; chipsHideTimer = null; }, 200);
  }
  if (textoInput && chipsContainer) {
    textoInput.addEventListener('focus', mostrarChipsPreguntasRecientes);
    textoInput.addEventListener('blur', ocultarChipsConRetraso);
  }

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    errorDiv.classList.add('hidden');
    respuestaDiv.classList.add('hidden');
    const consulta_id = (vinoContextoSelect && vinoContextoSelect.value) ? vinoContextoSelect.value.trim() : '';
    const texto = document.getElementById('texto').value.trim();
    var modoLocal = modoSelect && modoSelect.value === 'local';
    if (!texto) {
      errorDiv.textContent = 'Escribe tu pregunta.';
      errorDiv.classList.remove('hidden');
      return;
    }
    var perfil = document.getElementById('perfil').value || 'aficionado';
    var t0 = performance.now();
    try {
      var r, data;
      if (modoLocal && consulta_id) {
        var sid = getSessionId();
        var localHeaders = { 'Content-Type': 'application/json' };
        if (sid) localHeaders['X-Session-ID'] = sid;
        r = await fetch('/api/preguntar-local', {
          method: 'POST',
          headers: localHeaders,
          body: JSON.stringify({ consulta_id: consulta_id, pregunta: texto, perfil: perfil })
        });
        data = await r.json().catch(function() { return { detail: 'Respuesta inválida del servidor.' }; });
      } else {
        var url = '/preguntar-sumiller?texto=' + encodeURIComponent(texto) + '&perfil=' + encodeURIComponent(perfil);
        if (consulta_id) url += '&consulta_id=' + encodeURIComponent(consulta_id);
        var lang = getAppLang();
        if (lang) url += '&lang=' + encodeURIComponent(lang);
        var sid = getSessionId();
        var headers = { 'Accept': 'application/json' };
        if (sid) headers['X-Session-ID'] = sid;
        r = await fetch(url, { headers: headers });
        data = await r.json().catch(function() { return { detail: 'Respuesta inválida del servidor.' }; });
      }
      var t1 = performance.now();
      var tiempoMs = Math.round((t1 - t0) * 100) / 100;
      if (!r.ok) {
        errorDiv.textContent = (Array.isArray(data.detail) ? (data.detail[0] && data.detail[0].msg) || data.detail : data.detail) || data.message || 'Error al preguntar';
        errorDiv.classList.remove('hidden');
        return;
      }
      guardarInteraccionVoz(texto, data.respuesta || '');
      if (window._ultimaPreguntaFueVoz) window._ultimaPreguntaFueVoz = false;
      respuestaDiv.innerHTML = '';
      var meta = document.createElement('div');
      meta.className = 'texto-pequeno respuesta-meta';
      meta.style.marginBottom = '0.5rem';
      var modoReal = data.modo || (modoLocal ? 'local' : 'nube');
      meta.textContent = 'Respuesta en ' + tiempoMs + ' s · ' + (modoReal === 'local' ? 'IA Local 🖥️' : 'Nube ☁️');
      respuestaDiv.appendChild(meta);

      var respuestaContainer = document.createElement('div');
      respuestaContainer.className = 'respuesta-container';
      if (data.imagen_url) {
        var img = document.createElement('img');
        img.src = data.imagen_url;
        img.alt = data.vino_nombre || 'Vino';
        img.className = 'vino-imagen';
        img.onerror = function() { this.style.display = 'none'; };
        respuestaContainer.appendChild(img);
      }
      var respuestaTexto = document.createElement('div');
      respuestaTexto.className = 'respuesta-texto';
      if (data.vino_nombre) {
        var tit = document.createElement('div');
        tit.className = 'texto-pequeno';
        tit.style.marginBottom = '0.5rem';
        tit.textContent = 'Vino: ' + data.vino_nombre;
        respuestaTexto.appendChild(tit);
      }
      if (data.vinos_recomendados && data.vinos_recomendados.length) {
        var listWrap = document.createElement('div');
        listWrap.className = 'texto-pequeno';
        listWrap.style.marginBottom = '0.5rem';
        listWrap.innerHTML = 'Opciones: ' + data.vinos_recomendados.map(function(v) {
          return (v.nombre || '—') + (v.bodega ? ' (' + v.bodega + ')' : '');
        }).join(' · ');
        respuestaTexto.appendChild(listWrap);
      }
      var respuestaTextoContenido = (data.respuesta || '').replace(/\n/g, ' ');
      var block = document.createElement('div');
      block.className = 'respuesta-block';
      block.innerHTML = '<div class="pregunta">Pregunta: ' + (data.pregunta || texto) + '</div>' +
        '<div class="respuesta">' + (data.respuesta || '').replace(/\n/g, '<br>') + '</div>';
      var toolbar = document.createElement('div');
      toolbar.className = 'respuesta-toolbar';
      var btnSpeak = document.createElement('button');
      btnSpeak.type = 'button';
      btnSpeak.className = 'btn-speak';
      btnSpeak.innerHTML = '🔊';
      btnSpeak.title = 'Escuchar respuesta';
      btnSpeak.setAttribute('aria-label', 'Escuchar respuesta en voz alta');
      btnSpeak.addEventListener('click', function() { hablarTexto(respuestaTextoContenido); });
      toolbar.appendChild(btnSpeak);
      var vinoKeyComprar = data.vino_key || (data.vino_nombre ? String(data.vino_nombre).toLowerCase().trim().replace(/\s+/g, '-')
        .replace(/[áàäâ]/g, 'a').replace(/[éèëê]/g, 'e').replace(/[íìïî]/g, 'i')
        .replace(/[óòöô]/g, 'o').replace(/[úùüû]/g, 'u').replace(/ñ/g, 'n').replace(/[^a-z0-9-]/g, '') : '');
      if ((data.mostrar_boton_comprar || data.vino_nombre) && vinoKeyComprar) {
        var aComprar = document.createElement('a');
        aComprar.href = '/vino/' + encodeURIComponent(vinoKeyComprar) + '/comprar';
        aComprar.target = '_blank';
        aComprar.rel = 'noopener noreferrer';
        aComprar.className = 'btn-comprar btn btn-dorado';
        aComprar.textContent = '🛒 Comprar este vino';
        aComprar.title = 'Ver dónde comprar este vino';
        toolbar.appendChild(aComprar);
      }
      block.appendChild(toolbar);
      respuestaTexto.appendChild(block);
      respuestaContainer.appendChild(respuestaTexto);
      respuestaDiv.appendChild(respuestaContainer);

      if (data.sugerencias_personalizadas && data.sugerencias_personalizadas.length > 0) {
        var sugSection = document.createElement('div');
        sugSection.className = 'sugerencias-personalizadas';
        var sugTitle = document.createElement('h3');
        sugTitle.className = 'sugerencias-titulo';
        sugTitle.setAttribute('data-i18n', 'recomendaciones.personalizadas');
        sugTitle.textContent = 'Recomendaciones para ti';
        sugSection.appendChild(sugTitle);
        data.sugerencias_personalizadas.forEach(function(s) {
          var item = document.createElement('div');
          item.className = 'sugerencia-item';
          var nombre = (s.nombre || '—') + (s.bodega ? ' · ' + s.bodega : '');
          var spanNombre = document.createElement('span');
          spanNombre.className = 'sugerencia-nombre';
          spanNombre.textContent = nombre;
          item.appendChild(spanNombre);
          var wrapBtn = document.createElement('div');
          wrapBtn.className = 'sugerencia-feedback';
          var btnLike = document.createElement('button');
          btnLike.type = 'button';
          btnLike.className = 'btn-feedback btn-like';
          btnLike.setAttribute('data-i18n', 'feedback.me_gusta');
          btnLike.textContent = '👍 Me gusta';
          btnLike.dataset.key = s.key || '';
          var btnDislike = document.createElement('button');
          btnDislike.type = 'button';
          btnDislike.className = 'btn-feedback btn-dislike';
          btnDislike.setAttribute('data-i18n', 'feedback.no_me_gusta');
          btnDislike.textContent = '👎 No me gusta';
          btnDislike.dataset.key = s.key || '';
          wrapBtn.appendChild(btnLike);
          wrapBtn.appendChild(btnDislike);
          item.appendChild(wrapBtn);
          sugSection.appendChild(item);
          var wineKey = s.key || '';
          btnLike.addEventListener('click', function() {
            sendFeedbackVino(wineKey, true);
            btnLike.classList.add('active');
            btnDislike.classList.remove('active');
          });
          btnDislike.addEventListener('click', function() {
            sendFeedbackVino(wineKey, false);
            btnDislike.classList.add('active');
            btnLike.classList.remove('active');
          });
        });
        respuestaDiv.appendChild(sugSection);
      }
      function sendFeedbackVino(wineKey, like) {
        var sid = getSessionId();
        if (!wineKey) return;
        fetch('/api/feedback-vino', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sid, wine_key: wineKey, like: like })
        }).then(function(r) { return r.json(); }).then(function() {}).catch(function() {});
      }

      respuestaDiv.classList.remove('hidden');
      if (data.navegacion) {
        if (data.navegacion === 'menu') {
          var ev = new CustomEvent('vino-pro-abrir-menu-secreto');
          document.dispatchEvent(ev);
        } else if (typeof data.navegacion === 'string' && data.navegacion.indexOf('/') === 0) {
          setTimeout(function() { window.location.href = data.navegacion; }, 800);
        }
      }
    } catch (err) {
      errorDiv.textContent = 'Error de conexión: ' + err.message;
      errorDiv.classList.remove('hidden');
    }
  });
})();
