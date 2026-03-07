/**
 * Menú secreto: se abre con ☰ o doble clic en el ayudante. Se cierra al elegir opción o clic fuera.
 */
(function() {
  var MENU_ID = 'menu-secreto';
  var BACKDROP_ID = 'menu-secreto-backdrop';
  var BTN_ID = 'btn-menu-secreto';
  var MASCOT_ID = 'chatbot-guia-mascot';
  var PREMIUM_MODAL_ID = 'premium-upsell-modal';
  var PREMIUM_CLOSE_ID = 'premium-upsell-close';
  var DELETE_ACCOUNT_BTN_ID = 'delete-account-btn';
  var SESSION_KEY = 'vino_pro_session_id';

  function getMenu() { return document.getElementById(MENU_ID); }
  function getBackdrop() { return document.getElementById(BACKDROP_ID); }
  function getBtn() { return document.getElementById(BTN_ID); }
  function getMascot() { return document.getElementById(MASCOT_ID); }
  function getPremiumModal() { return document.getElementById(PREMIUM_MODAL_ID); }
  function getPremiumCloseBtn() { return document.getElementById(PREMIUM_CLOSE_ID); }
  function getDeleteAccountBtn() { return document.getElementById(DELETE_ACCOUNT_BTN_ID); }

  function openMenu() {
    var menu = getMenu();
    var backdrop = getBackdrop();
    if (menu) {
      menu.classList.remove('menu-secreto--cerrado');
      menu.setAttribute('aria-hidden', 'false');
    }
    if (backdrop) {
      backdrop.classList.remove('menu-secreto--cerrado');
      backdrop.setAttribute('aria-hidden', 'false');
    }
  }

  function closeMenu() {
    var menu = getMenu();
    var backdrop = getBackdrop();
    if (menu) {
      menu.classList.add('menu-secreto--cerrado');
      menu.setAttribute('aria-hidden', 'true');
    }
    if (backdrop) {
      backdrop.classList.add('menu-secreto--cerrado');
      backdrop.setAttribute('aria-hidden', 'true');
    }
  }

  function toggleMenu() {
    var menu = getMenu();
    var isOpen = menu && !menu.classList.contains('menu-secreto--cerrado');
    if (isOpen) closeMenu();
    else openMenu();
  }

  function showPremiumUpsell() {
    var modal = getPremiumModal();
    if (!modal) return;
    modal.removeAttribute('hidden');
  }

  function hidePremiumUpsell() {
    var modal = getPremiumModal();
    if (!modal) return;
    modal.setAttribute('hidden', '');
  }

  function deleteAccount() {
    var sid = '';
    try { sid = (window.getSessionId ? window.getSessionId() : '') || ''; } catch (_) {}
    if (!sid) {
      window.alert('No se ha encontrado una sesión activa para eliminar.');
      return;
    }
    var confirmed = window.confirm('Se eliminarán tu perfil, bodega, escaneos, valoraciones, contactos QR y datos asociados. Esta acción no se puede deshacer. ¿Deseas continuar?');
    if (!confirmed) return;
    fetch('/api/auth/eliminar-cuenta', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Session-ID': sid
      },
      body: '{}'
    })
      .then(function(r) {
        return r.json().then(function(data) {
          return { ok: r.ok, data: data };
        }).catch(function() {
          return { ok: r.ok, data: null };
        });
      })
      .then(function(result) {
        if (!result.ok) {
          var detail = result.data && (result.data.detail || result.data.error);
          throw new Error(detail || 'No se pudo eliminar la cuenta.');
        }
        try {
          localStorage.removeItem(SESSION_KEY);
          localStorage.removeItem('vineros_target_lang');
        } catch (_) {}
        window.alert('Tu cuenta se ha eliminado de forma definitiva.');
        window.location.href = '/inicio';
      })
      .catch(function(err) {
        window.alert(err && err.message ? err.message : 'No se pudo eliminar la cuenta.');
      });
  }

  function checkPremiumForQr() {
    var sid = '';
    try { sid = (window.getSessionId ? window.getSessionId() : '') || ''; } catch (_) {}
    if (!sid) {
      showPremiumUpsell();
      return Promise.resolve(false);
    }
    return fetch('/api/check-limit', {
      headers: {
        'Accept': 'application/json',
        'X-Session-ID': sid
      }
    })
      .then(function(r) { return r.ok ? r.json() : null; })
      .then(function(data) {
        var isPro = !!(data && data.es_pro);
        if (!isPro) showPremiumUpsell();
        return isPro;
      })
      .catch(function() {
        showPremiumUpsell();
        return false;
      });
  }

  document.addEventListener('vino-pro-abrir-menu-secreto', openMenu);

  function init() {
    var btn = getBtn();
    var backdrop = getBackdrop();
    var mascot = getMascot();
    var menu = getMenu();
    var premiumClose = getPremiumCloseBtn();
    var premiumModal = getPremiumModal();

    if (btn) btn.addEventListener('click', function() { toggleMenu(); });

    if (backdrop) backdrop.addEventListener('click', function() { closeMenu(); });

    if (mascot) {
      mascot.addEventListener('dblclick', function(e) {
        e.preventDefault();
        openMenu();
      });
    }

    if (menu) {
      var links = menu.querySelectorAll('.menu-secreto-link');
      for (var i = 0; i < links.length; i++) {
        links[i].addEventListener('click', function(e) {
          var link = e.currentTarget;
          var href = (link.getAttribute('href') || '').trim();
          if (href === '/qr') {
            e.preventDefault();
            closeMenu();
            checkPremiumForQr().then(function(isPro) {
              if (isPro) window.location.href = '/qr';
            });
            return;
          }
          closeMenu();
        });
      }
    }

    if (premiumClose) premiumClose.addEventListener('click', hidePremiumUpsell);
    if (premiumModal) {
      premiumModal.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('premium-upsell-backdrop')) hidePremiumUpsell();
      });
    }

    var deleteBtn = getDeleteAccountBtn();
    if (deleteBtn) {
      deleteBtn.addEventListener('click', function() {
        closeMenu();
        deleteAccount();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
