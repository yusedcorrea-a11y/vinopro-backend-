/**
 * Adaptador restaurantes: token API, copiar, formulario de configuración (nombre, programas, webhook).
 */
(function() {
  var apiToken = '';
  var tokenEl = document.getElementById('api-token');
  var copyBtn = document.getElementById('copy-token');
  var tokenMsg = document.getElementById('token-msg');
  var formConfig = document.getElementById('form-config');
  var configMsg = document.getElementById('config-msg');

  if (!tokenEl) return;

  function showMsg(el, text, isError) {
    if (!el) return;
    el.textContent = text;
    el.className = 'mensaje ' + (isError ? 'error' : 'exito');
    el.classList.remove('hidden');
    setTimeout(function() { el.classList.add('hidden'); }, 4000);
  }

  function loadToken() {
    fetch('/api/adaptador/token')
      .then(function(r) { return r.json(); })
      .then(function(d) {
        apiToken = d.token || '';
        tokenEl.textContent = apiToken || 'No se pudo generar';
        if (d.session_id) {
          try { localStorage.setItem('vino_pro_session_id', d.session_id); } catch (_) {}
        }
        if (d.nombre) {
          var nombreRest = document.getElementById('nombre-rest');
          if (nombreRest) nombreRest.value = d.nombre || '';
        }
        if (d.programas && d.programas.length) {
          document.querySelectorAll('input[name="programa"]').forEach(function(cb) {
            cb.checked = d.programas.indexOf(cb.value) !== -1;
          });
        }
        if (d.webhook_url) {
          var webhookUrl = document.getElementById('webhook-url');
          if (webhookUrl) webhookUrl.value = d.webhook_url || '';
        }
      })
      .catch(function() {
        tokenEl.textContent = 'Error al cargar';
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
        .then(function(r) { return r.json(); })
        .then(function() {
          showMsg(configMsg, 'Configuración guardada.', false);
        })
        .catch(function() {
          showMsg(configMsg, 'Error al guardar.', true);
        });
    });
  }

  loadToken();
})();
