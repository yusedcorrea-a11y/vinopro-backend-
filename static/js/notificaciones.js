/**
 * Notificaciones en header: badge + dropdown, enlace a chat o perfil.
 */
(function() {
  'use strict';

  function headers() {
    var sid = typeof window.getSessionId === 'function' ? window.getSessionId() : '';
    var h = { 'Accept': 'application/json', 'Content-Type': 'application/json' };
    if (sid) h['X-Session-ID'] = sid;
    return h;
  }

  function updateBadge(count) {
    var badge = document.getElementById('notif-badge');
    if (!badge) return;
    if (count > 0) {
      badge.textContent = count > 99 ? '99+' : String(count);
      badge.style.display = '';
    } else {
      badge.style.display = 'none';
    }
  }

  function fetchCount() {
    fetch('/api/notificaciones/count', { headers: headers() })
      .then(function(r) { return r.ok ? r.json() : null; })
      .then(function(data) {
        if (data && typeof data.unread === 'number') updateBadge(data.unread);
      })
      .catch(function() {});
  }

  function renderItem(n) {
    var tipo = n.tipo || '';
    var from = (n.from_username || '').trim();
    var leida = !!n.leida;
    var dd = document.getElementById('notif-dropdown');
    var msgEnviado = (dd && dd.getAttribute('data-msg-enviado')) || ' te ha enviado un mensaje';
    var msgSigue = (dd && dd.getAttribute('data-msg-sigue')) || ' te sigue';
    var cls = 'notif-item' + (leida ? '' : ' no-leida');
    var label = '';
    var href = '#';
    if (tipo === 'nuevo_mensaje' && from) {
      label = from + ' ' + msgEnviado;
      href = '/comunidad/chat/' + encodeURIComponent(from);
    } else if (tipo === 'nuevo_seguidor' && from) {
      label = from + ' ' + msgSigue;
      href = '/comunidad/perfil/' + encodeURIComponent(from);
    } else {
      label = 'Notificación';
    }
    var a = document.createElement('a');
    a.className = cls;
    a.href = href;
    a.setAttribute('data-id', n.id || '');
    a.innerHTML = '<span class="notif-item-tipo">' + escapeHtml(label) + '</span>';
    return a;
  }

  function escapeHtml(t) {
    return String(t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function openDropdown() {
    var dd = document.getElementById('notif-dropdown');
    var list = document.getElementById('notif-list');
    var empty = document.getElementById('notif-empty');
    if (!dd || !list) return;
    dd.classList.remove('notif-dropdown--cerrado');
    list.innerHTML = '';
    fetch('/api/notificaciones', { headers: headers() })
      .then(function(r) { return r.ok ? r.json() : null; })
      .then(function(data) {
        var notifs = (data && data.notificaciones) || [];
        if (notifs.length === 0) {
          if (empty) { empty.style.display = 'block'; }
        } else {
          if (empty) { empty.style.display = 'none'; }
          notifs.forEach(function(n) {
            var el = renderItem(n);
            el.addEventListener('click', function() {
              var id = n.id;
              if (id) markRead([id]);
              fetchCount();
            });
            list.appendChild(el);
          });
        }
      })
      .catch(function() {
        if (empty) { empty.style.display = 'block'; empty.textContent = 'Error al cargar.'; }
      });
  }

  function closeDropdown() {
    var dd = document.getElementById('notif-dropdown');
    if (dd) dd.classList.add('notif-dropdown--cerrado');
  }

  function markRead(ids) {
    var body = ids !== null && ids.length ? { ids: ids } : {};
    fetch('/api/notificaciones/leer', {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify(body)
    })
      .then(function() { fetchCount(); })
      .catch(function() {});
  }

  function init() {
    var btn = document.getElementById('btn-notificaciones');
    var wrap = document.getElementById('header-notif-wrap');
    var dd = document.getElementById('notif-dropdown');
    var btnMarcar = document.getElementById('notif-marcar-todas');

    fetchCount();

    if (btn && dd) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (dd.classList.contains('notif-dropdown--cerrado')) {
          openDropdown();
        } else {
          closeDropdown();
        }
      });
    }

    if (btnMarcar) {
      btnMarcar.addEventListener('click', function() {
        markRead(null);
        closeDropdown();
      });
    }

    document.addEventListener('click', function() {
      closeDropdown();
    });
    if (wrap) {
      wrap.addEventListener('click', function(e) { e.stopPropagation(); });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
