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
  var lastKnownCity = null;
  var lugaresCache = [];
  var destacadosCache = [];
  var REQUIRED_IDS = [
    'mapa-btn-ubicacion',
    'mapa-btn-buscar-ciudad',
    'mapa-input-ciudad',
    'mapa-radio',
    'mapa-estado',
    'mapa-lista',
    'mapa-mapa'
  ];

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
      distancia: el.getAttribute('data-text-distancia') || 'km',
      cargando_ubicacion: el.getAttribute('data-text-cargando-ubicacion') || 'Obteniendo ubicación...',
      cargando_busqueda: el.getAttribute('data-text-cargando-busqueda') || 'Buscando...',
      no_https: el.getAttribute('data-text-no-https') || 'Tu navegador bloquea la ubicación por seguridad. Abre la app en HTTPS para usar GPS.',
      geo_no_disponible: el.getAttribute('data-text-geo-no-disponible') || 'No pudimos obtener tu ubicación actual. Verifica señal GPS o busca por ciudad.',
      geo_timeout: el.getAttribute('data-text-geo-timeout') || 'La ubicación tardó demasiado. Intenta de nuevo o busca por ciudad.',
      error_init: el.getAttribute('data-text-error-init') || 'No se pudo inicializar el mapa. Recarga la página.',
      sin_destacados: el.getAttribute('data-text-sin-destacados') || 'No hay lugares recomendados por ahora.'
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

  function isGeoSecureContext() {
    if (window.isSecureContext) return true;
    var host = (window.location && window.location.hostname) || '';
    return host === 'localhost' || host === '127.0.0.1' || host === '::1';
  }

  function mapGeoError(error) {
    var fallback = textos.permiso_denegado || 'No podemos acceder a tu ubicación. Busca por ciudad arriba.';
    if (!error || typeof error.code !== 'number') return fallback;
    if (error.code === 1) return textos.permiso_denegado || fallback; // PERMISSION_DENIED
    if (error.code === 2) return textos.geo_no_disponible || fallback;
    if (error.code === 3) return textos.geo_timeout || fallback;
    return fallback;
  }

  function setButtonLoading(btn, active, text) {
    if (!btn) return;
    if (active) {
      if (!btn.dataset.originalHtml) btn.dataset.originalHtml = btn.innerHTML;
      btn.disabled = true;
      btn.classList.add('btn-loading');
      btn.innerHTML = '<span class="btn-spinner" aria-hidden="true"></span><span>' + (text || textos.cargando_busqueda || 'Buscando...') + '</span>';
      btn.setAttribute('aria-busy', 'true');
      return;
    }
    if (btn.dataset.originalHtml) {
      btn.innerHTML = btn.dataset.originalHtml;
    }
    btn.classList.remove('btn-loading');
    btn.disabled = false;
    btn.removeAttribute('aria-busy');
  }

  function validateRequiredElements() {
    var missing = REQUIRED_IDS.filter(function(id) { return !document.getElementById(id); });
    if (!missing.length) return true;
    console.error('[Mapa] Faltan IDs requeridos en HTML:', missing.join(', '));
    showEstado(textos.error_init || 'No se pudo inicializar el mapa. Recarga la página.', true);
    return false;
  }

  function initMapa(centerLat, centerLon, zoom) {
    var container = document.getElementById('mapa-mapa');
    if (!container || map) return map;
    if (typeof L === 'undefined' || !L.map) {
      showEstado(textos.error_init || 'No se pudo inicializar el mapa. Recarga la página.', true);
      return null;
    }
    if (L.Icon && L.Icon.Default && L.Icon.Default.mergeOptions) {
      L.Icon.Default.mergeOptions({
        iconUrl: '/static/images/leaflet/marker-icon.png',
        iconRetinaUrl: '/static/images/leaflet/marker-icon-2x.png',
        shadowUrl: '/static/images/leaflet/marker-shadow.png'
      });
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
      container.innerHTML = '<p class="page-subtitle">' + (textos.sin_destacados || 'No hay lugares recomendados por ahora.') + '</p>';
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
    return fetchLugares(url)
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
        throw new Error('error_red');
      });
  }

  function buscarPorCiudad(ciudad, radioKm) {
    if (ciudad && ciudad.trim()) lastKnownCity = ciudad.trim();
    getTextos();
    showEstado(textos.buscando, false);
    var url = '/api/lugares?ciudad=' + encodeURIComponent(ciudad) + '&radio=' + (radioKm || 5);
    return fetchLugares(url)
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
        throw new Error('sin_resultados');
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
    var base = 'https://www.guiarepsol.com/es/buscador/';
    var term = parseInputTerm();
    if (!term) return base;
    return base + '?q=' + encodeURIComponent(term);
  }

  /**
   * Geocodificación inversa (Nominatim): coords → ciudad/localidad para pasar a Repsol ?q=
   * Nominatim exige User-Agent identificando la app; sin él puede devolver 403 o vacío.
   */
  function reverseGeocodeCity(lat, lon) {
    var url = 'https://nominatim.openstreetmap.org/reverse?lat=' + encodeURIComponent(lat) + '&lon=' + encodeURIComponent(lon) + '&format=json&accept-language=es';
    return fetch(url, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'VINO PRO IA (vinopro-app; mapa/guia-repsol)'
      }
    })
      .then(function(r) { return r.ok ? r.json() : null; })
      .then(function(data) {
        if (!data || !data.address) return null;
        var a = data.address;
        return (a.city || a.town || a.village || a.municipality || a.county || a.state || '').trim() || null;
      })
      .catch(function() { return null; });
  }

  function parseInputCoords() {
    var inputCiudad = document.getElementById('mapa-input-ciudad');
    var raw = inputCiudad ? (inputCiudad.value || '').trim() : '';
    if (!raw) return null;
    var coordsMatch = raw.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/);
    if (!coordsMatch) return null;
    var lat = parseFloat(coordsMatch[1]);
    var lon = parseFloat(coordsMatch[2]);
    if (!isFinite(lat) || !isFinite(lon)) return null;
    return { lat: lat, lon: lon };
  }

  function openRepsolWithUserLocation() {
    var base = 'https://www.guiarepsol.com/es/buscador/';
    var term = parseInputTerm();
    if (term) {
      lastKnownCity = term;
      window.open(base + '?q=' + encodeURIComponent(term), '_blank', 'noopener');
      return;
    }
    if (lastKnownCity) {
      window.open(base + '?q=' + encodeURIComponent(lastKnownCity), '_blank', 'noopener');
      return;
    }
    var coords = (userCoords && userCoords.lat != null && userCoords.lon != null)
      ? userCoords
      : parseInputCoords();
    if (coords) {
      reverseGeocodeCity(coords.lat, coords.lon).then(function(city) {
        if (city) {
          lastKnownCity = city;
          window.open(base + '?q=' + encodeURIComponent(city), '_blank', 'noopener');
        } else {
          window.open(base, '_blank', 'noopener');
        }
      });
      return;
    }
    window.open(base, '_blank', 'noopener');
  }

  function initGuideTabs() {
    var tabVino = document.getElementById('mapa-tab-vino');
    var tabRepsol = document.getElementById('mapa-tab-repsol');
    var panelVino = document.getElementById('mapa-panel-vino');
    var panelRepsol = document.getElementById('mapa-panel-repsol');
    var btnRepsol = document.getElementById('mapa-btn-repsol-search');
    var descVino = document.getElementById('mapa-guide-desc-vino');
    var descRepsol = document.getElementById('mapa-guide-desc-repsol');
    var seccionDestacados = document.getElementById('mapa-seccion-destacados');
    if (!tabVino || !tabRepsol || !panelVino || !panelRepsol) return;

    function setDescVisibility(showVinoDesc) {
      if (descVino) { descVino.classList.toggle('hidden', !showVinoDesc); descVino.setAttribute('aria-hidden', showVinoDesc ? 'false' : 'true'); }
      if (descRepsol) { descRepsol.classList.toggle('hidden', showVinoDesc); descRepsol.setAttribute('aria-hidden', showVinoDesc ? 'true' : 'false'); }
    }

    function showVino() {
      tabVino.classList.add('active');
      tabRepsol.classList.remove('active');
      tabVino.setAttribute('aria-selected', 'true');
      tabRepsol.setAttribute('aria-selected', 'false');
      panelVino.classList.remove('hidden');
      panelRepsol.classList.add('hidden');
      panelRepsol.setAttribute('aria-hidden', 'true');
      setDescVisibility(true);
      if (map && typeof map.invalidateSize === 'function') {
        setTimeout(function() { map.invalidateSize(); }, 100);
      }
      // Al hacer clic en Selección VINO PRO IA, llevar al usuario a la sección de patrocinadores/recomendados
      if (seccionDestacados) {
        setTimeout(function() {
          seccionDestacados.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 150);
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
      setDescVisibility(false);
    }

    tabVino.addEventListener('click', showVino);
    tabRepsol.addEventListener('click', showRepsol);
    if (btnRepsol) {
      btnRepsol.addEventListener('click', function() {
        openRepsolWithUserLocation();
      });
    }
  }

  function init() {
    getTextos();
    var btnUbicacion = document.getElementById('mapa-btn-ubicacion');
    var btnCiudad = document.getElementById('mapa-btn-buscar-ciudad');
    var inputCiudad = document.getElementById('mapa-input-ciudad');
    if (!btnUbicacion || !btnCiudad || !inputCiudad) {
      if (document.getElementById('mapa-estado')) {
        showEstado(textos.error_init || 'No se pudo inicializar el mapa. Recarga la página.', true);
      }
      return;
    }
    if (!validateRequiredElements()) {
      showEstado(textos.error_init || 'No se pudo inicializar el mapa. Recarga la página.', true);
    }

    if (btnUbicacion) {
      btnUbicacion.addEventListener('click', function() {
        if (!navigator.geolocation) {
          showEstado(textos.permiso_denegado, true);
          return;
        }
        if (!isGeoSecureContext()) {
          showEstado(textos.no_https, true);
          return;
        }
        setButtonLoading(btnUbicacion, true, textos.cargando_ubicacion);
        showEstado(textos.cargando_ubicacion || textos.buscando, false);
        navigator.geolocation.getCurrentPosition(
          function(pos) {
            var lat = pos.coords.latitude;
            var lon = pos.coords.longitude;
            userCoords = { lat: lat, lon: lon };
            setInputFromCoords(lat, lon);
            reverseGeocodeCity(lat, lon).then(function(city) {
              if (city) lastKnownCity = city;
            });
            // Solo Google Maps: dónde tomar vino cerca (el mini mapa no se actualiza aquí)
            var mapsUrl = 'https://www.google.com/maps/search/vinoteca+bar+de+vino+wine+bar/@' + lat + ',' + lon + ',14z';
            try {
              window.open(mapsUrl, '_blank', 'noopener,noreferrer');
            } catch (e) {}
            hideEstado();
            showEstado('Se abrió Google Maps con sitios para tomar vino cerca. Para ver la lista en la app, usa «Buscar por ciudad» en la pestaña Selección VINO PRO.', false);
            setButtonLoading(btnUbicacion, false);
          },
          function(err) {
            showEstado(mapGeoError(err), true);
            setButtonLoading(btnUbicacion, false);
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
      });
    }

    if (btnCiudad && inputCiudad) {
      function buscarCiudad() {
        var ciudad = (inputCiudad.value || '').trim();
        if (ciudad.length < 2) return;
        setButtonLoading(btnCiudad, true, textos.cargando_busqueda);
        var coordsMatch = ciudad.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/);
        if (coordsMatch) {
          buscarPorCoords(parseFloat(coordsMatch[1]), parseFloat(coordsMatch[2]), getRadioKm())
            .finally(function() { setButtonLoading(btnCiudad, false); });
          return;
        }
        buscarPorCiudad(ciudad, getRadioKm())
          .finally(function() { setButtonLoading(btnCiudad, false); });
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
      estadoEl.setAttribute('data-text-geo-no-disponible', estadoEl.getAttribute('data-text-geo-no-disponible') || 'No pudimos obtener tu ubicación actual. Verifica señal GPS o busca por ciudad.');
      estadoEl.setAttribute('data-text-geo-timeout', estadoEl.getAttribute('data-text-geo-timeout') || 'La ubicación tardó demasiado. Intenta de nuevo o busca por ciudad.');
      estadoEl.setAttribute('data-text-error-init', estadoEl.getAttribute('data-text-error-init') || 'No se pudo inicializar el mapa. Recarga la página.');
      estadoEl.setAttribute('data-text-sin-destacados', estadoEl.getAttribute('data-text-sin-destacados') || 'No hay lugares recomendados por ahora.');
    }

    initGuideTabs();
    try {
      initMapa(40.4168, -3.7038, 6);
      cargarLugaresDestacados();
    } catch (err) {
      if (typeof console !== 'undefined' && console.error) console.error('[Mapa] initMapa/L:', err);
      showEstado(textos.error_init || 'No se pudo cargar el mapa. Recarga la página.', true);
    }

    // Pregunta breve de ubicación al entrar: una vez por sesión. Si acepta, todas las funciones (mapa, Repsol) quedan listas.
    (function initAskUbicacion() {
      var STORAGE_KEY = 'mapa_ubicacion_asked';
      var banner = document.getElementById('mapa-ask-ubicacion');
      var btnSi = document.getElementById('mapa-ask-si');
      var btnNo = document.getElementById('mapa-ask-no');
      if (!banner || !btnSi || !btnNo) return;
      function hideBanner() {
        banner.classList.add('hidden');
        try { sessionStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
      }
      function showBanner() {
        banner.classList.remove('hidden');
      }
      if (navigator.geolocation && isGeoSecureContext()) {
        try {
          if (!sessionStorage.getItem(STORAGE_KEY) && !(userCoords && userCoords.lat != null)) showBanner();
        } catch (e) { showBanner(); }
      }
      btnSi.addEventListener('click', function() {
        if (!navigator.geolocation || !isGeoSecureContext()) { hideBanner(); return; }
        btnSi.disabled = true;
        navigator.geolocation.getCurrentPosition(
          function(pos) {
            userCoords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
            setInputFromCoords(userCoords.lat, userCoords.lon);
            reverseGeocodeCity(userCoords.lat, userCoords.lon).then(function(city) {
              if (city) lastKnownCity = city;
            });
            hideBanner();
            btnSi.disabled = false;
          },
          function() {
            hideBanner();
            btnSi.disabled = false;
          },
          { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 }
        );
      });
      btnNo.addEventListener('click', hideBanner);
    })();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
