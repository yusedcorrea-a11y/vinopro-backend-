/**
 * VINO PRO IA - Sesión y tema.
 * Expone window.getSessionId() y tema claro/oscuro.
 */
(function() {
  'use strict';

  var SESSION_KEY = 'vino_pro_session_id';
  var THEME_KEY = 'vino_pro_theme';

  // 1. Exponer getSessionId en window de inmediato (primera línea ejecutable útil)
  window.getSessionId = function getSessionId() {
    try {
      return window.localStorage.getItem(SESSION_KEY) || '';
    } catch (e) {
      return '';
    }
  };

  // 2. Crear session ID si no existe (síncrono, para que getSessionId() lo devuelva ya)
  try {
    if (!window.localStorage.getItem(SESSION_KEY)) {
      var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0;
        var v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
      window.localStorage.setItem(SESSION_KEY, uuid);
    }
  } catch (e) {}

  // 3. Tema
  function getTheme() {
    try {
      return window.localStorage.getItem(THEME_KEY) || 'light';
    } catch (e) {
      return 'light';
    }
  }

  function setTheme(theme) {
    try {
      window.localStorage.setItem(THEME_KEY, theme);
    } catch (e) {}
    var root = document.documentElement;
    if (root && root.setAttribute) {
      root.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
    }
    var btn = document.getElementById('toggle-theme-btn');
    if (btn && btn.textContent !== undefined) {
      btn.textContent = theme === 'dark' ? 'Modo claro' : 'Modo oscuro';
    }
  }

  window.getTheme = getTheme;
  window.setTheme = setTheme;

  // Aplicar tema guardado al cargar
  try {
    var root = document.documentElement;
    if (root && root.setAttribute) {
      root.setAttribute('data-theme', getTheme() === 'dark' ? 'dark' : 'light');
    }
  } catch (e) {}

  // Cuando el DOM esté listo: botón de tema
  function onReady() {
    var btn = document.getElementById('toggle-theme-btn');
    if (btn) {
      btn.textContent = getTheme() === 'dark' ? 'Modo claro' : 'Modo oscuro';
      btn.addEventListener('click', function() {
        var next = getTheme() === 'dark' ? 'light' : 'dark';
        setTheme(next);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
