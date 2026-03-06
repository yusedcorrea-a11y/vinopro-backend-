/**
 * Página Mapa: geolocalización del usuario y búsqueda de lugares para tomar vino.
 * Usa la API /api/lugares con fallback a /api/lugares-cerca.
 */
(function() {
  'use strict';

  var map = null;
  var markers = [];
  var destacadosMarkers = [];
  var userMarker = null;
  var textos = {};
  var userCoords = null;
  var lugaresCache = [];
  var destacadosCache = [];

  function getTextos() {
    var el = document.getElementById('mapa-estado');
    if (!el) return;
    textos = {
      buscando: el.getAttribute('data-text-buscando') || 'Buscando lugares...',
      no_resultados: el.getAttribute('data-text-no-resultados') || 'No se encontraron lugares cercanos.',
      permiso_denegado: el.getAttribute('data-text-permiso-denegado') || 'No podemos acceder a tu ubicación. Busca por ciudad arriba.',
      error_red: el.getAttribute('data-text-error-red') || 'Error de conexión. Intenta de nuevo.',
      ver_ruta: el.getAttribute('data-text-ver-ruta') || 'Ver ruta',
      llamar: el.getAttribute('data-text-llamar') || 'Llamar',
      web: el.getAttribute('data-text-web') || 'Web',
      distancia: el.getAttribute('data-text-distancia') || 'km'
    };
  }

  function showEstado(msg, isError) {
    var el = document.getElementById('mapa-estado');
    if (!el) return;
    el.textContent = msg;
    el.style.display = 'block';
    el.classList.toggle('error', !!isError);
  }

  function hideEstado() {
    var el = document.getElementById('mapa-estado');
    if (el) { el.style.display = 'none'; el.classList.remove('error'); }
  }

  function initMapa(centerLat, centerLon, zoom) {
    var container = document.getElementById('mapa-mapa');
    if (!container || map) return map;
    if (typeof L === 'undefined' || !L.map) {
      showEstado('No se pudo cargar el mapa. Recarga la página.', true);
      return null;
    }
    map = L.map('mapa-mapa').setView([centerLat, centerLon], zoom || 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19
    }).addTo(map);
    return map;
  }

  function clearMarkers() {
    markers.forEach(function(m) { if (m && m.remove) m.remove(); });
    markers = [];
  }

  function clearDestacadosMarkers() {
    destacadosMarkers.forEach(function(m) { if (m && m.remove) m.remove(); });
    destacadosMarkers = [];
  }

  function addUserMarker(lat, lon) {
    if (userMarker && userMarker.remove) userMarker.remove();
    if (!map) return;
    userMarker = L.marker([lat, lon], {
      icon: L.divIcon({ className: 'mapa-marker-user', html: '&#9783;', iconSize: [24, 24] })
    }).addTo(map);
  }

  function addLugarMarkers(lugares, centerLat, centerLon) {
    clearMarkers();
    if (!map || !lugares || !lugares.length) return;
    var bounds = L.latLngBounds([[centerLat, centerLon], [centerLat, centerLon]]);
    lugares.forEach(function(lugar) {
      if (lugar.lat == null || lugar.lon == null) return;
      var m = L.marker([lugar.lat, lugar.lon])
        .addTo(map)
        .bindPopup(
          '<strong>' + (lugar.nombre || '') + '</strong><br>' +
          (lugar.direccion ? lugar.direccion + '<br>' : '') +
          (lugar.distancia_km != null ? lugar.distancia_km + ' km' : '')
        );
      markers.push(m);
      bounds.extend([lugar.lat, lugar.lon]);
    });
    map.fitBounds(bounds, { padding: [20, 20], maxZoom: 15 });
  }

  function addDestacadosMarkers(lugares) {
    clearDestacadosMarkers();
    if (!map || !lugares || !lugares.length) return;
    lugares.forEach(function(lugar) {
      if (lugar.lat == null || lugar.lon == null) return;
      var m = L.marker([lugar.lat, lugar.lon])
        .addTo(map)
        .bindPopup(
          '<strong>' + (lugar.nombre || '') + '</strong> (Recomendado)<br>' +
          (lugar.direccion ? lugar.direccion + '<br>' : '') +
          (lugar.email ? '<a href="mailto:' + encodeURIComponent(lugar.email) + '">' + lugar.email + '</a>' : '')
        );
      destacadosMarkers.push(m);
    });
  }

  function renderLugarCard(lugar, opts) {
    if (window.LugaresUI && typeof window.LugaresUI.renderLugarCard === 'function') {
      return window.LugaresUI.renderLugarCard(lugar, opts, textos);
    }
    return '<h4>' + (lugar.nombre || '—') + '</h4>';
  }

  function bindCardActions(card, lugar) {
    card.addEventListener('click', function(e) {
      var actionBtn = e.target.closest('[data-action]');
      if (actionBtn) {
        e.preventDefault();
        e.stopPropagation();
        if (window.LugaresUI && typeof window.LugaresUI.openAction === 'function') {
          window.LugaresUI.openAction(lugar, actionBtn.getAttribute('data-action'));
        }
        return;
      }
      if (!map) return;
      if (lugar.lat == null || lugar.lon == null) return;
      map.setView([lugar.lat, lugar.lon], 17);
      var allMarkers = markers.concat(destacadosMarkers);
      var m = allMarkers.find(function(x) { return x.getLatLng().lat === lugar.lat && x.getLatLng().lng === lugar.lon; });
      if (m && m.openPopup) m.openPopup();
    });
  }

  function setInputFromCoords(lat, lon) {
    var input = document.getElementById('mapa-input-ciudad');
    if (!input) return;
    var latText = Number(lat).toFixed(5);
    var lonText = Number(lon).toFixed(5);
    input.value = latText + ', ' + lonText;
    input.setAttribute('data-lat', latText);
    input.setAttribute('data-lon', lonText);
  }

  function distanciaKm(lat1, lon1, lat2, lon2) {
    var R = 6371;
    var dLat = (lat2 - lat1) * Math.PI / 180;
    var dLon = (lon2 - lon1) * Math.PI / 180;
    var a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  function withDistance(lugares, base) {
    if (!base || base.lat == null || base.lon == null) return (lugares || []).slice();
    return (lugares || []).map(function(lugar) {
      var dist = null;
      if (lugar.lat != null && lugar.lon != null) {
        dist = distanciaKm(base.lat, base.lon, Number(lugar.lat), Number(lugar.lon));
      }
      var next = Object.assign({}, lugar);
      if (dist != null && isFinite(dist)) next.distancia_km = Number(dist.toFixed(2));
      return next;
    });
  }

  function renderLista(lugares) {
    var container = document.getElementById('mapa-lista');
    if (!container) return;
    getTextos();
    container.innerHTML = '';
    if (!lugares || !lugares.length) {
      container.innerHTML = '<p class="page-subtitle">' + textos.no_resultados + '</p>';
      return;
    }
    lugares.forEach(function(lugar) {
      var card = document.createElement('div');
      card.className = 'mapa-lugar-card';
      card.setAttribute('data-lat', lugar.lat);
      card.setAttribute('data-lon', lugar.lon);
      card.innerHTML = renderLugarCard(lugar);
      bindCardActions(card, lugar);
      container.appendChild(card);
    });
  }

  function renderDestacados(lugares) {
    var container = document.getElementById('mapa-destacados');
    if (!container) return;
    getTextos();
    container.innerHTML = '';
    if (!lugares || !lugares.length) {
      container.innerHTML = '<p class="page-subtitle">No hay lugares recomendados por ahora.</p>';
      return;
    }
    lugares.forEach(function(lugar) {
      var card = document.createElement('div');
      card.className = 'mapa-lugar-card mapa-lugar-card-destacado';
      card.setAttribute('data-lat', lugar.lat);
      card.setAttribute('data-lon', lugar.lon);
      card.innerHTML = renderLugarCard(lugar, { destacado: true });
      bindCardActions(card, lugar);
      container.appendChild(card);
    });
  }

  function cargarLugaresDestacados() {
    fetch('/api/lugares-destacados', { headers: { 'Accept': 'application/json' } })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        destacadosCache = data.lugares || [];
        applyDistanceFilter();
      })
      .catch(function() {
        destacadosCache = [];
        applyDistanceFilter();
      });
  }

  function buscarPorCoords(lat, lon, radioKm) {
    getTextos();
    showEstado(textos.buscando, false);
    var url = '/api/lugares?lat=' + encodeURIComponent(lat) + '&lon=' + encodeURIComponent(lon) + '&radio=' + (radioKm || 5);
    fetchLugares(url)
      .then(function(data) {
        hideEstado();
        userCoords = { lat: Number(lat), lon: Number(lon) };
        lugaresCache = data.lugares || [];
        if (!map) initMapa(lat, lon);
        else map.setView([lat, lon], map.getZoom() || 14);
        addUserMarker(lat, lon);
        applyDistanceFilter();
      })
      .catch(function() {
        showEstado(textos.error_red, true);
      });
  }

  function buscarPorCiudad(ciudad, radioKm) {
    getTextos();
    showEstado(textos.buscando, false);
    var url = '/api/lugares?ciudad=' + encodeURIComponent(ciudad) + '&radio=' + (radioKm || 5);
    fetchLugares(url)
      .then(function(data) {
        hideEstado();
        var lat = Number(data.lat), lon = Number(data.lon);
        userCoords = { lat: lat, lon: lon };
        lugaresCache = data.lugares || [];
        setInputFromCoords(lat, lon);
        if (!map) initMapa(lat, lon);
        else map.setView([lat, lon], 14);
        addUserMarker(lat, lon);
        applyDistanceFilter();
      })
      .catch(function() {
        showEstado(textos.no_resultados + ' (' + ciudad + ')', true);
      });
  }

  function getRadioKm() {
    var sel = document.getElementById('mapa-radio');
    return sel ? parseFloat(sel.value) || 5 : 5;
  }

  function getFilteredByRadius(lugares) {
    var radio = getRadioKm();
    if (!userCoords || userCoords.lat == null || userCoords.lon == null) return (lugares || []).slice();
    return (lugares || []).filter(function(lugar) {
      if (lugar.lat == null || lugar.lon == null) return false;
      var dist = distanciaKm(userCoords.lat, userCoords.lon, Number(lugar.lat), Number(lugar.lon));
      return isFinite(dist) && dist <= radio;
    });
  }

  function applyDistanceFilter() {
    var filtrados = withDistance(getFilteredByRadius(lugaresCache), userCoords);
    renderLista(filtrados);
    if (userCoords && map) {
      addLugarMarkers(filtrados, userCoords.lat, userCoords.lon);
    } else {
      clearMarkers();
    }
    var destacadosFiltrados = withDistance(getFilteredByRadius(destacadosCache), userCoords);
    renderDestacados(destacadosFiltrados);
    addDestacadosMarkers(destacadosFiltrados);
  }

  function fetchLugares(urlPrimary) {
    return fetch(urlPrimary, { headers: { 'Accept': 'application/json' } }).then(function(r) {
      if (r.status === 404 && urlPrimary.indexOf('/api/lugares?') === 0) {
        var fallback = urlPrimary.replace('/api/lugares?', '/api/lugares-cerca?');
        return fetch(fallback, { headers: { 'Accept': 'application/json' } }).then(function(r2) {
          if (!r2.ok) throw new Error('No encontrado');
          return r2.json();
        });
      }
      if (!r.ok) throw new Error('No encontrado');
      return r.json();
    });
  }

  function parseInputTerm() {
    var inputCiudad = document.getElementById('mapa-input-ciudad');
    var raw = inputCiudad ? (inputCiudad.value || '').trim() : '';
    if (!raw) return '';
    var coordsMatch = raw.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/);
    if (coordsMatch) return '';
    return raw;
  }

  function buildRepsolUrl() {
    var base = 'https://www.guiarepsol.com/es/comer/';
    var term = parseInputTerm();
    if (!term) return base;
    return base + '?q=' + encodeURIComponent(term);
  }

  function initGuideTabs() {
    var tabVino = document.getElementById('mapa-tab-vino');
    var tabRepsol = document.getElementById('mapa-tab-repsol');
    var panelVino = document.getElementById('mapa-panel-vino');
    var panelRepsol = document.getElementById('mapa-panel-repsol');
    var btnRepsol = document.getElementById('mapa-btn-repsol-search');
    if (!tabVino || !tabRepsol || !panelVino || !panelRepsol) return;

    function showVino() {
      tabVino.classList.add('active');
      tabRepsol.classList.remove('active');
      tabVino.setAttribute('aria-selected', 'true');
      tabRepsol.setAttribute('aria-selected', 'false');
      panelVino.classList.remove('hidden');
      panelRepsol.classList.add('hidden');
      panelRepsol.setAttribute('aria-hidden', 'true');
      if (map && typeof map.invalidateSize === 'function') {
        setTimeout(function() { map.invalidateSize(); }, 100);
      }
    }

    function showRepsol() {
      tabRepsol.classList.add('active');
      tabVino.classList.remove('active');
      tabRepsol.setAttribute('aria-selected', 'true');
      tabVino.setAttribute('aria-selected', 'false');
      panelRepsol.classList.remove('hidden');
      panelRepsol.setAttribute('aria-hidden', 'false');
      panelVino.classList.add('hidden');
    }

    tabVino.addEventListener('click', showVino);
    tabRepsol.addEventListener('click', showRepsol);
    if (btnRepsol) {
      btnRepsol.addEventListener('click', function() {
        window.open(buildRepsolUrl(), '_blank', 'noopener');
      });
    }
  }

  function init() {
    getTextos();
    var btnUbicacion = document.getElementById('mapa-btn-ubicacion');
    var btnCiudad = document.getElementById('mapa-btn-buscar-ciudad');
    var inputCiudad = document.getElementById('mapa-input-ciudad');

    if (btnUbicacion) {
      btnUbicacion.addEventListener('click', function() {
        if (!navigator.geolocation) {
          showEstado(textos.permiso_denegado, true);
          return;
        }
        showEstado(textos.buscando, false);
        navigator.geolocation.getCurrentPosition(
          function(pos) {
            var lat = pos.coords.latitude;
            var lon = pos.coords.longitude;
            setInputFromCoords(lat, lon);
            buscarPorCoords(lat, lon, getRadioKm());
          },
          function() {
            showEstado(textos.permiso_denegado, true);
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
      });
    }

    if (btnCiudad && inputCiudad) {
      function buscarCiudad() {
        var ciudad = (inputCiudad.value || '').trim();
        if (ciudad.length < 2) return;
        var coordsMatch = ciudad.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/);
        if (coordsMatch) {
          buscarPorCoords(parseFloat(coordsMatch[1]), parseFloat(coordsMatch[2]), getRadioKm());
          return;
        }
        buscarPorCiudad(ciudad, getRadioKm());
      }
      btnCiudad.addEventListener('click', buscarCiudad);
      inputCiudad.addEventListener('keydown', function(e) { if (e.key === 'Enter') { e.preventDefault(); buscarCiudad(); } });
    }

    var radioSel = document.getElementById('mapa-radio');
    if (radioSel) {
      radioSel.addEventListener('change', applyDistanceFilter);
    }

    var estadoEl = document.getElementById('mapa-estado');
    if (estadoEl) {
      estadoEl.setAttribute('data-text-buscando', estadoEl.getAttribute('data-text-buscando') || 'Buscando lugares...');
      estadoEl.setAttribute('data-text-no-resultados', estadoEl.getAttribute('data-text-no-resultados') || 'No se encontraron lugares cercanos.');
      estadoEl.setAttribute('data-text-permiso-denegado', estadoEl.getAttribute('data-text-permiso-denegado') || 'No podemos acceder a tu ubicación. Busca por ciudad arriba.');
      estadoEl.setAttribute('data-text-error-red', estadoEl.getAttribute('data-text-error-red') || 'Error de conexión.');
      estadoEl.setAttribute('data-text-ver-ruta', estadoEl.getAttribute('data-text-ver-ruta') || 'Ver ruta');
      estadoEl.setAttribute('data-text-llamar', estadoEl.getAttribute('data-text-llamar') || 'Llamar');
      estadoEl.setAttribute('data-text-web', estadoEl.getAttribute('data-text-web') || 'Web');
      estadoEl.setAttribute('data-text-distancia', estadoEl.getAttribute('data-text-distancia') || 'km');
    }

    initMapa(40.4168, -3.7038, 6);
    cargarLugaresDestacados();
    initGuideTabs();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
