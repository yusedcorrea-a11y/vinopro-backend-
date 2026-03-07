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
    soporte_tecnico: '🛠️ <strong>Soporte técnico</strong><br><br><strong>Escáner:</strong> usa foto nítida de etiqueta, evita reflejos y prioriza JPG/PNG. Si falla OCR, prueba texto o código de barras.<br><strong>Mapa:</strong> en "Donde me tomo mi vino" puedes usar ubicación, radio por km y tarjetas sponsor con acciones (ruta, email, web).<br><strong>Tip sumiller:</strong> cuando detectes términos como "Crianza" o "Reserva", mantenlos en contexto enológico.',
    escanear: '🍷 <strong>Escáner de etiquetas</strong><br><br>Sube imagen (máx. 6 MB), o escribe texto/código de barras.<br>Si el móvil guarda en HEIC, conviértelo o reduce la imagen.<br>Tras identificar el vino, puedes llevarlo a bodega, comprar o trabajar ficha técnica.',
    mapa: '📍 <strong>Donde me tomo mi vino</strong><br><br>Activa ubicación para ver sitios cercanos y filtra por distancia (km).<br>Tienes dos guías: Selección VINO PRO y Guía Repsol.<br>Las tarjetas sponsor permiten abrir ruta, correo y web del local al instante.',
    adaptador: '🍴 <strong>Integración B2B (Adaptador)</strong><br><br>Ideal para restaurantes y wine bars.<br>1) Configura webhook URL.<br>2) Guarda token API.<br>3) Valida con "Probar webhook".<br>4) Si quieres seguridad extra, activa firma HMAC (<code>X-Vino-Signature</code>) con clave secreta.<br>Resultado: stock sincronizado en tiempo real entre sala y bodega digital.',
    negocio: '📈 <strong>Estrategia de negocio VINO</strong><br><br><strong>Sponsor PRO (ej. Casa Paca):</strong> más visibilidad en mapa y VINEROS, y mejor captación local.<br><strong>QR Networking Premium:</strong> genera QR comerciales, capta leads y mide escaneos por contacto/país.<br>Si tu objetivo es ventas y networking, este módulo acelera el embudo comercial horeca.<br><br>👉 <a href="/qr" class="chatbot-guia-link">Ir a QR Networking</a><br>👉 <a href="mailto:hola@vinoproia.com?subject=Interes%20comercial%20VINO%20PRO" class="chatbot-guia-link">Contactar administrador</a>',
    planes: '⭐ <strong>Planes</strong><br><br><strong>Gratis:</strong> escáner, sumiller, bodega limitada.<br><strong>Premium:</strong> bodega avanzada, QR Networking, herramientas comerciales y funciones profesionales para escalar ventas.<br><br>👉 <a href="/planes" class="chatbot-guia-link">Ver planes y activar Premium</a>',
    default: '👔 Cuéntame tu objetivo y te doy la ruta más directa. Ejemplos: "configurar webhook", "me falla el escáner", "quiero vender más", "negocios", "ventas", "qr networking".'
  };

  var KEYWORDS = {
    negocio: ['negocios', 'ventas', 'vender', 'captar', 'clientes', 'leads', 'sponsor', 'patrocinador', 'casa paca', 'qr', 'networking', 'comercial'],
    adaptador: ['adaptador', 'restaurante', 'webhook', 'token', 'api', 'integracion', 'tpv'],
    soporte_tecnico: ['soporte', 'tecnico', 'error', 'falla', 'arreglar', 'problema'],
    escanear: ['escanear', 'foto', 'imagen', 'etiqueta', 'ocr', 'codigo', 'barras'],
    mapa: ['mapa', 'donde me tomo', 'ubicacion', 'geolocalizacion', 'repsol', 'ruta', 'distancia'],
    planes: ['premium', 'pro', 'plan', 'planes', 'precio', 'pago', 'suscripcion', 'gratis']
  };

  function getAnswer(id) {
    return TEXTS[id] || TEXTS.default;
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
    el.classList.remove('chatbot-guia-answer--visible');
    el.innerHTML = getAnswer(id);
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

    document.querySelectorAll('.chatbot-guia-open-nav').forEach(function(trigger) {
      trigger.addEventListener('click', function(e) {
        e.preventDefault();
        openPanel();
      });
    });

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
