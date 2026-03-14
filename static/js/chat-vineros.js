/**
 * Chat VINEROS: cada usuario escribe en su idioma; el otro lee en el suyo (traducción automática).
 */
(function() {
  'use strict';

  var sid = window.getSessionId ? window.getSessionId() : '';
  var htmlLang = (document.documentElement.getAttribute('lang') || 'es').slice(0, 2).toLowerCase();
  var LANG_KEY = 'vineros_chat_lang';
  var langSelect = document.getElementById('chat-lang-select');
  var listView = document.getElementById('chat-list-view');
  var threadView = document.getElementById('chat-thread-view');
  var chatList = document.getElementById('chat-list');
  var chatSinConv = document.getElementById('chat-sin-conversaciones');
  var chatLoading = document.getElementById('chat-loading');
  var chatError = document.getElementById('chat-error');
  var chatMessages = document.getElementById('chat-messages');
  var chatForm = document.getElementById('chat-form');
  var chatInput = document.getElementById('chat-input');
  var chatThreadWith = document.getElementById('chat-thread-with');
  var initialUsername = (window.CHAT_INITIAL_USERNAME || '').trim().toLowerCase();
  var TEXTS = window.CHAT_TEXTS || {};

  function getLang() {
    if (!langSelect) return htmlLang || 'es';
    var v = (langSelect.value || 'auto').toLowerCase();
    if (v === 'auto') return htmlLang || 'es';
    return v;
  }

  function headers() {
    var h = { 'Accept': 'application/json', 'Content-Type': 'application/json' };
    if (sid) h['X-Session-ID'] = sid;
    return h;
  }

  function showList() {
    if (chatLoading) chatLoading.style.display = 'none';
    if (chatError) chatError.style.display = 'none';
    if (listView) { listView.classList.add('visible'); listView.style.display = 'block'; }
    if (threadView) { threadView.classList.remove('visible'); threadView.style.display = 'none'; }
  }

  function showThread() {
    if (chatLoading) chatLoading.style.display = 'none';
    if (chatError) chatError.style.display = 'none';
    if (listView) { listView.classList.remove('visible'); listView.style.display = 'none'; }
    if (threadView) { threadView.classList.add('visible'); threadView.style.display = 'block'; }
  }

  var CHAT_SIGNUP_URL = '/signup?next=' + encodeURIComponent('/comunidad/chat');

  function t(key) {
    return TEXTS[key] || key;
  }

  function showErr(msg, showAuthCta) {
    if (chatLoading) chatLoading.style.display = 'none';
    if (!chatError) return;
    chatError.style.display = 'block';
    if (showAuthCta) {
      chatError.innerHTML = escapeHtml(msg || t('error_perfil')) +
        '<div class="chat-error-ctas">' +
        '<a href="' + CHAT_SIGNUP_URL + '" class="btn btn-dorado">' + escapeHtml(t('registrarme')) + '</a> ' +
        '<a href="' + CHAT_SIGNUP_URL + '" class="btn btn-outline">' + escapeHtml(t('iniciar_sesion')) + '</a>' +
        '</div>';
    } else {
      chatError.textContent = msg || 'Error';
    }
  }

  function formatTimeAgo(ts) {
    if (!ts) return '';
    var now = Date.now() / 1000;
    var diff = now - ts;
    var mins = Math.floor(diff / 60);
    var hours = Math.floor(diff / 3600);
    var days = Math.floor(diff / 86400);
    if (mins < 1) return '';
    if (mins < 60) return (t('hace_min') || 'Hace {n} min').replace('{n}', mins);
    var d = new Date(ts * 1000);
    var today = new Date();
    var isToday = d.getDate() === today.getDate() && d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear();
    var yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    var isYesterday = d.getDate() === yesterday.getDate() && d.getMonth() === yesterday.getMonth() && d.getFullYear() === yesterday.getFullYear();
    if (isToday) return (t('hoy') || 'Hoy') + ', ' + d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    if (isYesterday) return t('ayer') || 'Ayer';
    if (days < 7) return d.toLocaleDateString(undefined, { weekday: 'short' });
    return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
  }

  function initLangSelect() {
    if (!langSelect) return;
    try {
      var saved = (localStorage.getItem(LANG_KEY) || '').toLowerCase();
      if (['auto', 'es', 'en', 'ru', 'hi'].indexOf(saved) >= 0) langSelect.value = saved;
    } catch (_) {}
    langSelect.addEventListener('change', function() {
      try { localStorage.setItem(LANG_KEY, (langSelect.value || 'auto').toLowerCase()); } catch (_) {}
      if (initialUsername) loadThread(initialUsername);
    });
  }

  function escapeHtml(t) {
    return String(t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function loadConversaciones() {
    if (chatLoading) chatLoading.style.display = 'block';
    fetch('/api/conversaciones', { headers: headers() })
      .then(function(r) {
        if (r.status === 401) { showErr('Necesitas crear perfil para usar el chat.', true); return null; }
        return r.json();
      })
      .then(function(data) {
        if (!data) return;
        var list = data.conversaciones || [];
        showList();
        if (!chatList) return;
        chatList.innerHTML = '';
        if (chatSinConv) chatSinConv.style.display = list.length ? 'none' : 'block';
        list.forEach(function(c) {
          var other = c.other_username || '';
          var preview = (c.last_message || '').substring(0, 60);
          var timeAgo = formatTimeAgo(c.last_at);
          var avatarLetter = (other.charAt(0) || 'V').toUpperCase();
          var a = document.createElement('a');
          a.className = 'chat-conv-item';
          a.href = '/comunidad/chat/' + encodeURIComponent(other);
          a.innerHTML = '<div class="chat-conv-avatar">' + escapeHtml(avatarLetter) + '</div>' +
            '<div class="chat-conv-body">' +
            '<div class="chat-conv-row"><span class="chat-conv-name">' + escapeHtml(other) + '</span>' +
            (timeAgo ? '<span class="chat-conv-time">' + escapeHtml(timeAgo) + '</span>' : '') + '</div>' +
            '<div class="chat-conv-preview">' + escapeHtml(preview) + '</div></div>';
          chatList.appendChild(a);
        });
      })
      .catch(function() { showErr(t('error_cargar_conv')); });
  }

  function textToSafeHtml(text) {
    return escapeHtml(text).replace(/\n/g, '<br>');
  }

  function renderMessage(msg, miUsername) {
    var isMine = (msg.from_username || '').toLowerCase() === (miUsername || '').toLowerCase();
    var text = msg.texto_traducido || msg.texto || '';
    var time = msg.created_at ? new Date(msg.created_at * 1000).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) : '';
    var div = document.createElement('div');
    div.className = 'chat-msg ' + (isMine ? 'mine' : 'theirs');
    div.innerHTML = '<span class="chat-msg-text">' + textToSafeHtml(text) + '</span><div class="chat-msg-meta">' + escapeHtml(time) + '</div>';
    return div;
  }

  function loadThread(username) {
    if (chatLoading) chatLoading.style.display = 'block';
    if (chatThreadWith) chatThreadWith.textContent = username;
    var lang = getLang();
    var url = '/api/chat/' + encodeURIComponent(username) + '?limit=100';
    if (lang) url += '&lang=' + encodeURIComponent(lang);
    fetch(url, { headers: headers() })
      .then(function(r) {
        if (r.status === 401) { showErr(t('error_perfil_chatear'), true); return null; }
        if (r.status === 404) { showErr(t('usuario_no_encontrado')); return null; }
        return r.json();
      })
      .then(function(data) {
        if (!data) return;
        showThread();
        if (!chatMessages) return;
        var miUsername = (data.mi_username || '').toLowerCase();
        var mensajes = data.mensajes || [];
        if (mensajes.length === 0) {
          chatMessages.innerHTML = '<p class="chat-empty-state" aria-live="polite">' + escapeHtml(t('envia_primero')) + '</p>';
        } else {
          chatMessages.innerHTML = '';
          mensajes.forEach(function(m) {
            chatMessages.appendChild(renderMessage(m, miUsername));
          });
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
      })
      .catch(function() { showErr(t('error_cargar_chat')); });
  }

  if (chatForm && chatInput) {
    chatForm.addEventListener('submit', function(e) {
      e.preventDefault();
      var text = (chatInput.value || '').trim();
      if (!text || !initialUsername) return;
      var btn = document.getElementById('chat-send-btn');
      if (btn) btn.disabled = true;
      fetch('/api/chat/' + encodeURIComponent(initialUsername), {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ texto: text })
      })
        .then(function(r) {
          if (r.status === 401 || r.status === 404) return null;
          return r.json();
        })
        .then(function(data) {
          if (btn) btn.disabled = false;
          if (!data || !data.ok) return;
          chatInput.value = '';
          var msg = data.mensaje || {};
          var div = renderMessage(msg, (msg.from_username || '').toLowerCase());
          if (chatMessages) {
            var emptyP = chatMessages.querySelector('.chat-empty-state');
            if (emptyP) emptyP.remove();
            chatMessages.appendChild(div);
            chatMessages.scrollTop = chatMessages.scrollHeight;
          }
        })
        .catch(function() { if (btn) btn.disabled = false; });
    });
  }

  initLangSelect();

  if (initialUsername) {
    loadThread(initialUsername);
  } else {
    loadConversaciones();
  }
})();
