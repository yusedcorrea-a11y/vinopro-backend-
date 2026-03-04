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
    intro: '¡Hola! Soy el asistente de Vino Pro IA. 👔 Resuelvo dudas de <strong>toda</strong> la app. Para vinos y maridajes, usa <strong>Preguntar</strong>. Escribe algo abajo o elige un tema.',
    escanear: '🍷 <strong>Escanear</strong><br><br>• <strong>Foto:</strong> Sube una imagen de la etiqueta (JPG, PNG, WebP o GIF; máx. 6 MB). Si viene del móvil en HEIC o muy pesada, puede fallar: redúcela o escribe el nombre.<br>• <strong>Texto:</strong> Escribe el nombre del vino o palabras clave y te buscamos en nuestra base y en Open Food Facts.<br>• <strong>Código de barras:</strong> Si lo tienes, introdúcelo y te devolvemos la ficha.<br>Tras el resultado puedes registrar el vino en tu bodega o ir a Comprar. Si algo no se lee bien, el bloque de respuesta tiene fondo oscuro para que se vea todo.',
    registrar: '📝 <strong>Registrar</strong><br><br>• <strong>Buscador:</strong> Arriba del formulario busca el vino (como Google). Si sale en "En nuestra base", ya está; si sale en "Encontrados en internet", usa "Usar estos datos" y se rellena solo.<br>• <strong>Gratis:</strong> Solo puedes registrar vinos que el buscador encuentre.<br>• <strong>Premium:</strong> Si no aparece nada, puedes registrarlo tú, añadir una foto y ofrecerlo a otros (aparecerá en Comprar como "Un usuario ofrece este vino"). Para eso hace falta <strong>PRO</strong>.',
    preguntar: '💬 <strong>Preguntar (sumiller)</strong><br><br>• Aquí preguntas por maridajes, recomendaciones, tipo de vino, etc.<br>• <strong>Modo IA Local 🖥️:</strong> Solo Premium. Usa el agente en tu PC (tienes que tener abierto <code>python agente_local\\server.py</code>).<br>• <strong>Modo Nube ☁️:</strong> Para todos. Respuestas del servidor, sin instalar nada.<br>• <strong>Consulta ID:</strong> Si acabas de escanear un vino, pega el UUID que te damos y el sumiller responde sobre ese vino en concreto.<br>• <strong>Perfil:</strong> Principiante, Aficionado o Profesional, para adaptar el lenguaje.',
    ia_local: '🖥️ <strong>IA Local</strong> (solo Premium)<br><br>La IA Local es <strong>exclusiva para usuarios PRO</strong>. Si no eres Premium, en Preguntar solo verás modo Nube ☁️.<br><br>Para usarla siendo PRO:<br>1. Abre una terminal en la carpeta del proyecto.<br>2. Ejecuta: <code>python agente_local\\server.py</code> (Windows) o <code>python agente_local/server.py</code> (Mac/Linux).<br>3. Debe salir algo como "Agente Sumiller local en http://0.0.0.0:8080".<br>4. En Preguntar, elige modo <strong>IA Local 🖥️</strong>.<br>Si no tienes el agente abierto, elige <strong>Nube ☁️</strong> y todo funcionará desde el servidor.',
    bodega: '🏠 <strong>Mi Bodega</strong><br><br>• Aquí ves y gestionas las botellas que añades (desde Escanear o Registrar).<br>• <strong>Límite diario:</strong> Según tu nivel (nuevo, normal, verificado) puedes añadir X registros al día.<br>• <strong>Plan Gratis:</strong> Máximo 50 vinos en la bodega. Si llegas al límite, te pedimos pasar a PRO.<br>• <strong>PRO:</strong> Bodega ilimitada y además puedes ofrecer vinos que no estén en la base (con foto y enlace de contacto en Comprar).<br>• Exportar PDF, valoración y alertas también están aquí.',
    comprar: '🛒 <strong>Comprar</strong><br><br>• En cada ficha de vino (tras escanear o buscar) tienes "Comprar este vino".<br>• <strong>Pestañas:</strong> Nacional (tu país), Internacional, Subastas.<br>• <strong>¿Dónde tomarlo?</strong> Guía por país (Repsol, Gambero Rosso, etc.) según dónde estés.<br>• Si un usuario <strong>Premium</strong> ha ofrecido ese vino, verás "Un usuario ofrece este vino" y podrás contactarle por correo (sin compromisos de pago ni envío por nuestra parte).',
    planes: '📋 <strong>Planes y Premium</strong> 👔<br><br><strong>Gratis:</strong> Escaneo, sumiller, bodega hasta 50 vinos, informes PDF. Solo puedes registrar vinos que el buscador encuentre.<br><br><strong>PRO (4,99 €/mes):</strong> Bodega ilimitada, registrar vinos que no estén en la base, subir foto y ofrecerlos a otros (tu enlace de contacto en Comprar). Ideal si tienes botellas raras o eres coleccionista. Los pagos son con Stripe; si no está activo, el administrador puede activarlo.<br><br><strong>Restaurante:</strong> Adaptador para conectar tu sistema con la app (webhook, token).<br><br>👉 <a href="/planes" class="chatbot-guia-link">Ver planes y pasar a PRO</a> — ¡te va a molar! 🍷',
    adaptador: '🍴 <strong>Adaptador restaurante</strong><br><br>Para bares y restaurantes que quieran enlazar su carta o sistema con Vino Pro IA.<br>• Configuras una <strong>URL de webhook</strong> y te damos un <strong>token</strong>.<br>• Cuando actualices el stock en Mi Bodega, enviamos un POST a esa URL con los datos.<br>• Así mantienes la carta de vinos sincronizada. Si no eres técnico, pásale esto al que gestione la web del local. 😉',
    default: '👔 No he pillado del todo tu duda. Prueba a escribir "premium", "escanear", "registrar", "preguntar", "IA local", "bodega", "comprar" o "adaptador", o pulsa uno de los temas de arriba.'
  };

  var KEYWORDS = {
    planes: ['premium', 'pro', 'plan', 'planes', 'precio', 'pago', 'pagar', 'suscripcion', 'gratis', 'limite', 'ilimitad'],
    escanear: ['escanear', 'foto', 'imagen', 'etiqueta', 'codigo', 'barras', 'buscar'],
    registrar: ['registrar', 'registro', 'formulario', 'buscar vino', 'añadir vino'],
    preguntar: ['preguntar', 'sumiller', 'maridaje', 'recomendacion'],
    ia_local: ['ia local', 'local', 'agente', '8080', 'terminal', 'servidor local'],
    bodega: ['bodega', 'mi bodega', 'botellas', 'cantidad'],
    comprar: ['comprar', 'comprar vino', 'tienda', 'donde tomarlo', 'guia'],
    adaptador: ['adaptador', 'restaurante', 'webhook', 'token', 'api']
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

    panel.querySelectorAll('.chatbot-guia-topic').forEach(function(t) {
      t.addEventListener('click', function() {
        var id = this.getAttribute('data-topic');
        showAnswer(id);
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
