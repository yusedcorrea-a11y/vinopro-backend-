/**
 * Chatbot guía: presente en todos los menús y acciones. Conocimiento completo de cada área. Vende Premium. 👔
 */
(function() {
  var PANEL_ID = 'chatbot-guia-panel';
  var MASCOT_ID = 'chatbot-guia-mascot';
  var ANSWERS_ID = 'chatbot-guia-answer';
  var INPUT_ID = 'chatbot-guia-input';
  var STORAGE_KEY = 'chatbot-guia-mascot-pos';
  var DOUBLE_TAP_MS = 400;

  var TEXTS = {
    intro: '👔 <strong>Asistente estratégico VINO PRO IA</strong><br><br>Estoy para ayudarte en tres frentes: <strong>soporte técnico</strong> (escáner y mapa), <strong>integración B2B</strong> (Adaptador/webhooks) y <strong>crecimiento de negocio</strong> (Sponsor + QR Networking Premium).',
    soporte_tecnico: '🛠️ <strong>Soporte técnico</strong><br><br><strong>Escáner:</strong> usa foto nítida de etiqueta, evita reflejos y prioriza JPG/PNG. Si falla OCR, prueba texto o código de barras.<br><strong>Mapa:</strong> en "Donde me tomo mi vino" puedes usar ubicación, radio por km y tarjetas sponsor con acciones (ruta, email, web).<br><strong>Tip experto en vinos:</strong> cuando detectes términos como "Crianza" o "Reserva", mantenlos en contexto enológico.',
    escanear: '🍷 <strong>Escáner de etiquetas</strong><br><br>Sube imagen (máx. 6 MB), o escribe texto/código de barras.<br>Si el móvil guarda en HEIC, conviértelo o reduce la imagen.<br>Tras identificar el vino, puedes llevarlo a bodega, comprar o trabajar ficha técnica.',
    mapa: '📍 <strong>Donde me tomo mi vino</strong><br><br><strong>Mi ubicación</strong> abre Google Maps con vinotecas y bares de vino cerca.<br><strong>Selección VINO PRO</strong>: busca por ciudad para ver mapa y lista en la app.<br>Guía Repsol: enlace a la guía oficial. Tarjetas: ruta, llamar, web.',
    adaptador: '🍴 <strong>Integración B2B (Adaptador)</strong><br><br>Ideal para restaurantes y wine bars. Conecta tu TPV, CoverManager o TheFork con tu bodega digital VINO PRO.<br><br><strong>Pasos rápidos:</strong><br>1️⃣ Copia tu token API (sección "Tu Token").<br>2️⃣ Pega la URL de tu sistema en "Webhook URL".<br>3️⃣ Pulsa "Probar Webhook" para verificar.<br>4️⃣ Activa firma HMAC si quieres seguridad extra.<br><br><strong>Endpoint de stock:</strong><br><code>GET /api/bodega/stock</code><br>Cabecera: <code>X-API-Token: TU_TOKEN</code><br><br><strong>Registrar venta:</strong><br><code>POST /api/adaptador/venta</code><br>Body: <code>{"vino_nombre":"...", "cantidad":1}</code><br><br><strong>Evento webhook (bodega.updated):</strong><br>VINO enviará un POST a tu URL con <code>{"event":"bodega.updated","stock":[...]}</code> cada vez que cambies la bodega.<br><br><strong>Firma HMAC (opcional):</strong><br>Si guardas una clave secreta, VINO firmará cada petición con <code>X-Vino-Signature: sha256=...</code>. Verifica con: <code>hmac_sha256(secret, timestamp + "." + raw_body)</code>.<br><br>¿Necesitas el código de verificación en Node.js o Python? Despliega la sección técnica en la pantalla del Adaptador (botón 🔧).',
    negocio: '📈 <strong>Estrategia de negocio VINO</strong><br><br><strong>Sponsor PRO (ej. Casa Paca):</strong> más visibilidad en mapa y VINEROS, y mejor captación local.<br><strong>QR Networking Premium:</strong> genera QR comerciales, capta leads y mide escaneos por contacto/país.<br>Si tu objetivo es ventas y networking, este módulo acelera el embudo comercial horeca.<br><br>Accede desde el menú principal (☰) → QR Networking.',
    planes: '⭐ <strong>Planes</strong><br><br><strong>Gratis:</strong> escáner, experto en vinos, bodega limitada.<br><strong>Premium:</strong> bodega avanzada, QR Networking, herramientas comerciales y funciones profesionales para escalar ventas.<br><br>Accede desde el menú principal (☰) → Planes.',
    default: '👔 Cuéntame tu objetivo y te doy la ruta más directa. Ejemplos: "configurar webhook", "me falla el escáner", "quiero vender más", "negocios", "ventas", "qr networking".'
  };

  var KEYWORDS = {
    negocio: ['negocios', 'ventas', 'vender', 'captar', 'clientes', 'leads', 'sponsor', 'patrocinador', 'casa paca', 'qr', 'networking', 'comercial'],
    adaptador: ['adaptador', 'restaurante', 'webhook', 'token', 'api', 'integracion', 'tpv', 'covermanager', 'thefork', 'hmac', 'firma', 'stock', 'sincronizar', 'conectar', 'endpoint', 'curl'],
    soporte_tecnico: ['soporte', 'tecnico', 'error', 'falla', 'arreglar', 'problema'],
    escanear: ['escanear', 'foto', 'imagen', 'etiqueta', 'ocr', 'codigo', 'barras'],
    mapa: ['mapa', 'donde me tomo', 'ubicacion', 'geolocalizacion', 'repsol', 'ruta', 'distancia'],
    planes: ['premium', 'pro', 'plan', 'planes', 'precio', 'pago', 'suscripcion', 'gratis']
  };

  function getAnswer(id) {
    return TEXTS[id] || TEXTS.default;
  }

  function getIntentMeta(topic) {
    if (topic === 'adaptador') {
      return { cls: 'intent-b2b', icon: '🔌', label: 'CONECTIVIDAD B2B', ctaPulse: false };
    }
    if (topic === 'negocio' || topic === 'planes') {
      return { cls: 'intent-pro', icon: '💰', label: 'ESTRATEGIA PRO', ctaPulse: true };
    }
    if (topic === 'soporte_tecnico' || topic === 'escanear' || topic === 'mapa') {
      return { cls: 'intent-soporte', icon: '🛠️', label: 'SOPORTE', ctaPulse: false };
    }
    return null;
  }

  function openPanel() {
    var panel = document.getElementById(PANEL_ID);
    var backdrop = document.getElementById('chatbot-guia-backdrop');
    if (panel) panel.classList.remove('chatbot-guia-panel--closed');
    if (backdrop) { backdrop.classList.remove('chatbot-guia-backdrop--closed'); backdrop.setAttribute('aria-hidden', 'false'); }
  }

  function closePanel() {
    var panel = document.getElementById(PANEL_ID);
    var backdrop = document.getElementById('chatbot-guia-backdrop');
    if (panel) panel.classList.add('chatbot-guia-panel--closed');
    if (backdrop) { backdrop.classList.add('chatbot-guia-backdrop--closed'); backdrop.setAttribute('aria-hidden', 'true'); }
  }

  function showAnswer(id) {
    var el = document.getElementById(ANSWERS_ID);
    if (!el) return;
    var intent = getIntentMeta(id);
    var badgeHtml = '';
    if (intent) {
      badgeHtml = '<span class="chatbot-guia-intent-badge ' + intent.cls + '">' +
        '<span class="chatbot-guia-intent-ico" aria-hidden="true">' + intent.icon + '</span>' +
        '<span class="chatbot-guia-intent-text">' + intent.label + '</span>' +
      '</span>';
    }
    el.classList.remove('chatbot-guia-answer--visible');
    el.innerHTML = badgeHtml + getAnswer(id);
    el.classList.remove('intent-soporte', 'intent-b2b', 'intent-pro');
    if (intent && intent.cls) el.classList.add(intent.cls);
    el.querySelectorAll('a.chatbot-guia-link').forEach(function(a) {
      if (intent && intent.ctaPulse) a.classList.add('chatbot-guia-cta-pro');
      else a.classList.remove('chatbot-guia-cta-pro');
    });
    el.classList.add('chatbot-guia-answer--visible');
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function matchTopic(text) {
    if (!text || !text.trim()) return null;
    var t = text.toLowerCase().trim();
    for (var topic in KEYWORDS) {
      for (var i = 0; i < KEYWORDS[topic].length; i++) {
        if (t.indexOf(KEYWORDS[topic][i]) !== -1) return topic;
      }
    }
    return null;
  }

  function initMascot(mascot) {
    var lastTap = 0;
    var dragging = false;
    var startX = 0, startY = 0, startLeft = 0, startTop = 0;

    function getPos() {
      var l = parseInt(mascot.style.left, 10), t = parseInt(mascot.style.top, 10);
      if (isNaN(l) || isNaN(t)) {
        var rect = mascot.getBoundingClientRect();
        return { left: rect.left, top: rect.top };
      }
      return { left: l, top: t };
    }
    function applyPos(left, top) {
      var maxW = window.innerWidth - mascot.offsetWidth;
      var maxH = window.innerHeight - mascot.offsetHeight;
      left = Math.max(0, Math.min(left, maxW));
      top = Math.max(0, Math.min(top, maxH));
      mascot.style.right = '';
      mascot.style.bottom = '';
      mascot.style.left = left + 'px';
      mascot.style.top = top + 'px';
      try { localStorage.setItem(STORAGE_KEY, left + ',' + top); } catch (e) {}
    }
    function loadSavedPos() {
      try {
        var s = localStorage.getItem(STORAGE_KEY);
        if (s) {
          var p = s.split(',');
          if (p.length >= 2) {
            var l = parseInt(p[0], 10), t = parseInt(p[1], 10);
            if (!isNaN(l) && !isNaN(t)) {
              applyPos(l, t);
              return;
            }
          }
        }
      } catch (e) {}
      mascot.style.left = '';
      mascot.style.top = '';
    }

    function openOnDoubleTap() {
      var now = Date.now();
      if (now - lastTap <= DOUBLE_TAP_MS) {
        lastTap = 0;
        openPanel();
      } else {
        lastTap = now;
      }
    }

    mascot.addEventListener('click', function(e) {
      if (dragging) return;
      e.preventDefault();
      openOnDoubleTap();
    });
    mascot.addEventListener('dblclick', function(e) {
      e.preventDefault();
      openPanel();
    });
    mascot.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openOnDoubleTap();
      }
    });

    function startDrag(clientX, clientY) {
      dragging = true;
      lastTap = 0;
      var p = getPos();
      startLeft = p.left;
      startTop = p.top;
      startX = clientX;
      startY = clientY;
    }
    function moveDrag(clientX, clientY) {
      if (!dragging) return;
      applyPos(startLeft + (clientX - startX), startTop + (clientY - startY));
    }
    function endDrag() {
      dragging = false;
    }

    mascot.addEventListener('mousedown', function(e) {
      if (e.button !== 0) return;
      startDrag(e.clientX, e.clientY);
    });
    window.addEventListener('mousemove', function(e) {
      moveDrag(e.clientX, e.clientY);
    });
    window.addEventListener('mouseup', endDrag);

    mascot.addEventListener('touchstart', function(e) {
      if (e.touches.length === 1) startDrag(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: true });
    window.addEventListener('touchmove', function(e) {
      if (e.touches.length === 1) moveDrag(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: true });
    window.addEventListener('touchend', endDrag);

    mascot.style.cursor = 'grab';
    mascot.addEventListener('mousedown', function() {
      mascot.style.cursor = 'grabbing';
    });
    window.addEventListener('mouseup', function() {
      mascot.style.cursor = 'grab';
    });

    loadSavedPos();
  }

  function init() {
    var mascot = document.getElementById(MASCOT_ID);
    var panel = document.getElementById(PANEL_ID);
    var input = document.getElementById(INPUT_ID);
    if (!panel) return;

    if (mascot) initMascot(mascot);

    if (input) {
      input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          var topic = matchTopic(input.value);
          if (topic) showAnswer(topic); else showAnswer('default');
        }
      });
    }

    var closeBtn = panel.querySelector('.chatbot-guia-close');
    if (closeBtn) closeBtn.addEventListener('click', closePanel);

    var backdrop = document.getElementById('chatbot-guia-backdrop');
    if (backdrop) backdrop.addEventListener('click', closePanel);

    window.chatbotGuiaOpen = openPanel;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
