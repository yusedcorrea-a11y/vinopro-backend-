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
  var testWebhookHistory = document.getElementById('test-webhook-history');
  var testWebhookPayload = document.getElementById('test-webhook-payload');
  var testWebhookHeaders = document.getElementById('test-webhook-headers');
  var testWebhookMode = document.getElementById('test-webhook-mode');
  var copyTestPayloadBtn = document.getElementById('copy-test-payload');
  var copyTestPayloadMsg = document.getElementById('copy-test-payload-msg');
  var signatureTabs = document.querySelectorAll('[data-signature-tab]');
  var signaturePanels = document.querySelectorAll('[data-signature-panel]');
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

  function escapeHtml(text) {
    return String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function renderTestHistory(items) {
    if (!testWebhookHistory) return;
    if (!items || !items.length) {
      testWebhookHistory.innerHTML = '<div class="history-item"><div class="history-meta">Todavía no hay pruebas registradas.</div></div>';
      return;
    }
    testWebhookHistory.innerHTML = items.map(function(item) {
      var statusCode = item.status_code ? 'HTTP ' + item.status_code : 'Sin respuesta HTTP';
      var when = formatDate(item.attempted_at) || 'Fecha desconocida';
      var mode = item.mode === 'signed' ? 'Firmado' : 'Plano';
      var preview = item.response_preview ? '<div class="history-preview">' + escapeHtml(item.response_preview) + '</div>' : '';
      return '<div class="history-item ' + (item.success ? 'ok' : 'err') + '">' +
        '<div class="history-meta">' + when + ' · ' + statusCode + ' · ' + mode + '</div>' +
        '<div>' + escapeHtml(item.message || '') + '</div>' +
        preview +
      '</div>';
    }).join('');
  }

  function getWebhookSecret() {
    var secretEl = document.getElementById('webhook-secret');
    return secretEl ? secretEl.value.trim() : '';
  }

  function getTestMode() {
    return (testWebhookMode && testWebhookMode.value === 'signed') ? 'signed' : 'plain';
  }

  async function hmacSha256Hex(secret, text) {
    if (!window.crypto || !window.crypto.subtle || !window.TextEncoder) {
      return 'firma-no-disponible-en-este-navegador';
    }
    var encoder = new TextEncoder();
    var key = await window.crypto.subtle.importKey(
      'raw',
      encoder.encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );
    var signature = await window.crypto.subtle.sign('HMAC', key, encoder.encode(text));
    return Array.from(new Uint8Array(signature)).map(function(b) {
      return b.toString(16).padStart(2, '0');
    }).join('');
  }

  function buildTestPayload() {
    var nombreRest = document.getElementById('nombre-rest');
    return {
      event: 'bodega.test',
      timestamp: new Date().toISOString(),
      restaurant_name: (nombreRest && nombreRest.value.trim()) || 'Mi Restaurante',
      message: 'Evento de prueba desde VINO. No afecta al stock real.',
      sample_stock: [
        {
          id: 'sample-botella',
          vino_nombre: 'Vino de prueba',
          cantidad: 2,
          anada: 2021,
          ubicacion: 'Bodega principal',
          tipo: 'tinto'
        }
      ]
    };
  }

  function renderTestPayload() {
    if (!testWebhookPayload) return;
    testWebhookPayload.textContent = JSON.stringify(buildTestPayload(), null, 2);
  }

  async function renderTestHeaders() {
    if (!testWebhookHeaders) return;
    var payload = JSON.stringify(buildTestPayload());
    var timestamp = new Date().toISOString();
    var lines = [
      'Content-Type: application/json',
      'X-Vino-Event: bodega.test',
      'X-Vino-Timestamp: ' + timestamp
    ];
    if (getTestMode() === 'signed') {
      var secret = getWebhookSecret();
      if (secret) {
        var signature = await hmacSha256Hex(secret, timestamp + '.' + payload);
        lines.push('X-Vino-Signature: sha256=' + signature);
      } else {
        lines.push('X-Vino-Signature: configura una clave secreta para generarla');
      }
    }
    testWebhookHeaders.textContent = lines.join('\n');
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
    var webhookSecret = document.getElementById('webhook-secret');
    if (webhookSecret) webhookSecret.value = d.webhook_secret || '';
    updateSyncStatus(d);
    renderTestHistory(d.webhook_test_history || []);
    renderTestPayload();
    renderTestHeaders();
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
      var webhookSecret = document.getElementById('webhook-secret');
      var payload = {
        nombre: nombreRest ? nombreRest.value.trim() || null : null,
        programas: programas,
        webhook_url: webhookUrl ? webhookUrl.value.trim() || null : null,
        webhook_secret: webhookSecret ? webhookSecret.value.trim() || null : null
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
          renderTestHeaders();
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
      var mode = getTestMode();
      fetch('/api/adaptador/test-webhook?token=' + encodeURIComponent(apiToken) + '&mode=' + encodeURIComponent(mode), {
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
            renderTestHistory(res.data.history || []);
            showMsg(testWebhookMsg, msg, false);
            return;
          }
          msg = (res.data && res.data.message) || (res.data && res.data.detail) || 'Error al probar el webhook.';
          if (res.data && res.data.status_code) msg += ' (HTTP ' + res.data.status_code + ')';
          if (res.data && res.data.response_preview) msg += ' Respuesta: ' + res.data.response_preview;
          if (res.data && res.data.history) renderTestHistory(res.data.history);
          showMsg(testWebhookMsg, msg, true);
        })
        .catch(function(err) {
          testWebhookBtn.disabled = false;
          showMsg(testWebhookMsg, 'Error al probar el webhook: ' + (err.message || ''), true);
        });
    });
  }

  var nombreRestInput = document.getElementById('nombre-rest');
  if (nombreRestInput) {
    nombreRestInput.addEventListener('input', function() {
      renderTestPayload();
      renderTestHeaders();
    });
  }

  var webhookSecretInput = document.getElementById('webhook-secret');
  if (webhookSecretInput) {
    webhookSecretInput.addEventListener('input', renderTestHeaders);
  }

  if (testWebhookMode) {
    testWebhookMode.addEventListener('change', renderTestHeaders);
  }

  if (copyTestPayloadBtn) {
    copyTestPayloadBtn.addEventListener('click', function() {
      var payload = JSON.stringify(buildTestPayload(), null, 2);
      navigator.clipboard.writeText(payload).then(function() {
        if (!copyTestPayloadMsg) return;
        copyTestPayloadMsg.textContent = 'Payload de prueba copiado al portapapeles.';
        copyTestPayloadMsg.className = 'texto-pequeno';
        copyTestPayloadMsg.classList.remove('hidden');
        setTimeout(function() { copyTestPayloadMsg.classList.add('hidden'); }, 2000);
      });
    });
  }

  if (signatureTabs.length && signaturePanels.length) {
    signatureTabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        var target = tab.getAttribute('data-signature-tab');
        signatureTabs.forEach(function(other) {
          var active = other === tab;
          other.classList.toggle('active', active);
          other.setAttribute('aria-selected', active ? 'true' : 'false');
        });
        signaturePanels.forEach(function(panel) {
          panel.classList.toggle('active', panel.getAttribute('data-signature-panel') === target);
        });
      });
    });
  }

  updateTokenField();
  renderTestPayload();
  renderTestHeaders();
  loadToken();
})();
