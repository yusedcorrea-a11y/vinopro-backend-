/**
 * Menú secreto: se abre con ☰ o doble clic en el ayudante. Se cierra al elegir opción o clic fuera.
 */
(function() {
  var MENU_ID = 'menu-secreto';
  var BACKDROP_ID = 'menu-secreto-backdrop';
  var BTN_ID = 'btn-menu-secreto';
  var MASCOT_ID = 'chatbot-guia-mascot';

  function getMenu() { return document.getElementById(MENU_ID); }
  function getBackdrop() { return document.getElementById(BACKDROP_ID); }
  function getBtn() { return document.getElementById(BTN_ID); }
  function getMascot() { return document.getElementById(MASCOT_ID); }

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

  document.addEventListener('vino-pro-abrir-menu-secreto', openMenu);

  function init() {
    var btn = getBtn();
    var backdrop = getBackdrop();
    var mascot = getMascot();
    var menu = getMenu();

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
        links[i].addEventListener('click', function() {
          closeMenu();
        });
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
