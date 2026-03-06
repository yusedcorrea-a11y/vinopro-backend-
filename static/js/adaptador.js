/**
 * Adaptador restaurantes: token API, configuración y documentación dinámica.
 */
(function() {
  var SESSION_KEY = 'vino_pro_session_id';
  var apiToken = '';
  var tokenVisible = false;
  var tokenEl = document.getElementById('api-token');
  var toggleBtn = document.getElementById('toggle-token');
  var regenBtn = document.getElementById('regen-token');
  var copyBtn = document.getElementById('copy-token');
  var tokenMsg = document.getElementById('token-msg');
  var formConfig = document.getElementById('form-config');
  var configMsg = document.getElementById('config-msg');
  var testWebhookBtn = document.getElementById('test-webhook');
  var testWebhookMsg = document.getElementById('test-webhook-msg');
  var syncStatus = document.getElementById('sync-status');
  var curlStock = document.getElementById('curl-stock');
  var curlVenta = document.getElementById('curl-venta');

  if (!tokenEl) return;

  function getSid() {
    try {
      return (localStorage.getItem(SESSION_KEY) || '').trim();
    } catch (_) {
      return '';
    }
  }

  function showMsg(el, text, isError) {
    if (!el) return;
    el.textContent = text;
    el.className = 'mensaje ' + (isError ? 'error' : 'exito');
    el.classList.remove('hidden');
    setTimeout(function() { el.classList.add('hidden'); }, 4000);
  }

  function formatDate(iso) {
    if (!iso) return '';
    try {
      return new Date(iso).toLocaleString('es-ES');
    } catch (_) {
      return iso;
    }
  }

  function updateTokenField() {
    tokenEl.type = tokenVisible ? 'text' : 'password';
    tokenEl.value = apiToken || 'No se pudo generar';
    if (toggleBtn) toggleBtn.textContent = tokenVisible ? 'Ocultar' : 'Revelar';
    updateDocs();
  }

  function updateDocs() {
    var tokenDoc = (tokenVisible && apiToken) ? apiToken : 'TU_TOKEN_AQUI';
    if (curlStock) {
      curlStock.textContent = 'curl -X GET "https://tu-dominio.com/api/bodega/stock" \\\n  -H "X-API-Token: ' + tokenDoc + '"';
    }
    if (curlVenta) {
      curlVenta.textContent = 'curl -X POST "https://tu-dominio.com/api/adaptador/venta" \\\n  -H "Content-Type: application/json" \\\n  -H "X-API-Token: ' + tokenDoc + '" \\\n  -d "{\\"vino_nombre\\":\\"Marqués de Riscal Reserva\\",\\"cantidad\\":1}"';
    }
  }

  function updateSyncStatus(data) {
    if (!syncStatus) return;
    var status = data && data.last_sync_status;
    var when = data && data.last_sync_at;
    var err = data && data.last_sync_error;
    syncStatus.className = 'sync-status';
    if (status === 'success' && when) {
      syncStatus.classList.add('ok');
      syncStatus.textContent = 'Última sincronización exitosa: ' + formatDate(when);
      return;
    }
    if (status === 'error') {
      syncStatus.classList.add('err');
      syncStatus.textContent = 'Última sincronización fallida: ' + (err || 'Error desconocido');
      return;
    }
    syncStatus.textContent = 'Última sincronización: todavía no disponible.';
  }

  function applyTokenData(d) {
    apiToken = d.token || '';
    updateTokenField();
    if (d.session_id) {
      try { localStorage.setItem(SESSION_KEY, d.session_id); } catch (_) {}
    }
    var nombreRest = document.getElementById('nombre-rest');
    if (nombreRest) nombreRest.value = d.nombre || '';
    document.querySelectorAll('input[name="programa"]').forEach(function(cb) {
      cb.checked = !!(d.programas && d.programas.indexOf(cb.value) !== -1);
    });
    var webhookUrl = document.getElementById('webhook-url');
    if (webhookUrl) webhookUrl.value = d.webhook_url || '';
    updateSyncStatus(d);
  }

  function loadToken() {
    var headers = { 'Accept': 'application/json' };
    var sid = getSid();
    if (sid) headers['X-Session-ID'] = sid;
    fetch('/api/adaptador/token', { headers: headers })
      .then(function(r) { return r.json(); })
      .then(function(d) { applyTokenData(d); })
      .catch(function() {
        apiToken = '';
        updateTokenField();
        tokenEl.value = 'Error al cargar';
      });
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function() {
      tokenVisible = !tokenVisible;
      updateTokenField();
    });
  }

  if (regenBtn) {
    regenBtn.addEventListener('click', function() {
      if (!confirm('¿Regenerar el token? El token anterior dejará de funcionar inmediatamente.')) return;
      var headers = { 'Accept': 'application/json' };
      var sid = getSid();
      if (sid) headers['X-Session-ID'] = sid;
      fetch('/api/adaptador/token/regenerate', {
        method: 'POST',
        headers: headers
      })
        .then(function(r) { return r.json().then(function(d) { return { ok: r.ok, data: d }; }); })
        .then(function(res) {
          if (!res.ok || !res.data || !res.data.success) {
            showMsg(tokenMsg, 'No se pudo regenerar el token.', true);
            return;
          }
          tokenVisible = false;
          applyTokenData(res.data.token_data || {});
          showMsg(tokenMsg, 'Token regenerado. Actualiza tu integración externa.', false);
        })
        .catch(function() {
          showMsg(tokenMsg, 'Error al regenerar el token.', true);
        });
    });
  }

  if (copyBtn) {
    copyBtn.addEventListener('click', function() {
      if (!apiToken) return;
      navigator.clipboard.writeText(apiToken).then(function() {
        tokenMsg.textContent = 'Token copiado al portapapeles.';
        tokenMsg.classList.remove('hidden');
        tokenMsg.className = 'texto-pequeno';
        setTimeout(function() { tokenMsg.classList.add('hidden'); }, 2000);
      });
    });
  }

  if (formConfig) {
    formConfig.addEventListener('submit', function(e) {
      e.preventDefault();
      if (!apiToken) {
        showMsg(configMsg, 'Primero carga el token.', true);
        return;
      }
      var programas = [];
      document.querySelectorAll('input[name="programa"]:checked').forEach(function(cb) {
        programas.push(cb.value);
      });
      var nombreRest = document.getElementById('nombre-rest');
      var webhookUrl = document.getElementById('webhook-url');
      var payload = {
        nombre: nombreRest ? nombreRest.value.trim() || null : null,
        programas: programas,
        webhook_url: webhookUrl ? webhookUrl.value.trim() || null : null
      };
      fetch('/api/adaptador/config?token=' + encodeURIComponent(apiToken), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function(r) { return r.json().then(function(d) { return { ok: r.ok, data: d }; }); })
        .then(function(res) {
          if (!res.ok) {
            showMsg(configMsg, 'Error al guardar.', true);
            return;
          }
          if (res.data && res.data.config) updateSyncStatus(res.data.config);
          showMsg(configMsg, 'Configuración guardada.', false);
        })
        .catch(function() {
          showMsg(configMsg, 'Error al guardar.', true);
        });
    });
  }

  if (testWebhookBtn) {
    testWebhookBtn.addEventListener('click', function() {
      if (!apiToken) {
        showMsg(testWebhookMsg, 'Primero carga el token.', true);
        return;
      }
      testWebhookBtn.disabled = true;
      fetch('/api/adaptador/test-webhook?token=' + encodeURIComponent(apiToken), {
        method: 'POST',
        headers: { 'Accept': 'application/json' }
      })
        .then(function(r) {
          return r.json().then(function(d) { return { ok: r.ok, data: d }; });
        })
        .then(function(res) {
          testWebhookBtn.disabled = false;
          var msg = '';
          if (res.ok && res.data && res.data.success) {
            msg = (res.data.message || 'Webhook de prueba correcto.') + ' ';
            msg += '(HTTP ' + (res.data.status_code || 200) + ')';
            if (res.data.response_preview) msg += ' Respuesta: ' + res.data.response_preview;
            showMsg(testWebhookMsg, msg, false);
            return;
          }
          msg = (res.data && res.data.message) || (res.data && res.data.detail) || 'Error al probar el webhook.';
          if (res.data && res.data.status_code) msg += ' (HTTP ' + res.data.status_code + ')';
          if (res.data && res.data.response_preview) msg += ' Respuesta: ' + res.data.response_preview;
          showMsg(testWebhookMsg, msg, true);
        })
        .catch(function(err) {
          testWebhookBtn.disabled = false;
          showMsg(testWebhookMsg, 'Error al probar el webhook: ' + (err.message || ''), true);
        });
    });
  }

  updateTokenField();
  loadToken();
})();
