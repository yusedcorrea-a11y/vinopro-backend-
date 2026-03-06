/**
 * Página Mapa: geolocalización del usuario y búsqueda de lugares cercanos (restaurantes, vinotecas, bares).
 * Usa la API /api/lugares-cerca con lat/lon o ciudad.
 */
(function() {
  'use strict';

  var map = null;
  var markers = [];
  var userMarker = null;
  var textos = {};

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
      map.setView([lugar.lat, lugar.lon], 17);
      var m = markers.find(function(x) { return x.getLatLng().lat === lugar.lat && x.getLatLng().lng === lugar.lon; });
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

  function cargarLugaresDestacados() {
    var container = document.getElementById('mapa-destacados');
    if (!container) return;
    getTextos();
    fetch('/api/lugares-destacados', { headers: { 'Accept': 'application/json' } })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        var lugares = data.lugares || [];
        container.innerHTML = '';
        if (!lugares.length) {
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
          if (map && lugar.lat != null && lugar.lon != null) {
            var m = L.marker([lugar.lat, lugar.lon])
              .addTo(map)
              .bindPopup(
                '<strong>' + (lugar.nombre || '') + '</strong> (Recomendado)<br>' +
                (lugar.direccion ? lugar.direccion + '<br>' : '') +
                (lugar.email ? '<a href="mailto:' + encodeURIComponent(lugar.email) + '">' + lugar.email + '</a>' : '')
              );
            markers.push(m);
          }
        });
      })
      .catch(function() { container.innerHTML = ''; });
  }

  function buscarPorCoords(lat, lon, radioKm) {
    getTextos();
    showEstado(textos.buscando, false);
    var url = '/api/lugares-cerca?lat=' + encodeURIComponent(lat) + '&lon=' + encodeURIComponent(lon) + '&radio=' + (radioKm || 5);
    fetch(url, { headers: { 'Accept': 'application/json' } })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        hideEstado();
        var lugares = data.lugares || [];
        if (!map) initMapa(lat, lon);
        else map.setView([lat, lon], map.getZoom() || 14);
        addUserMarker(lat, lon);
        addLugarMarkers(lugares, lat, lon);
        renderLista(lugares);
      })
      .catch(function() {
        showEstado(textos.error_red, true);
      });
  }

  function buscarPorCiudad(ciudad, radioKm) {
    getTextos();
    showEstado(textos.buscando, false);
    var url = '/api/lugares-cerca?ciudad=' + encodeURIComponent(ciudad) + '&radio=' + (radioKm || 5);
    fetch(url, { headers: { 'Accept': 'application/json' } })
      .then(function(r) {
        if (!r.ok) throw new Error('No encontrado');
        return r.json();
      })
      .then(function(data) {
        hideEstado();
        var lugares = data.lugares || [];
        var lat = data.lat, lon = data.lon;
        if (!map) initMapa(lat, lon);
        else map.setView([lat, lon], 14);
        addUserMarker(lat, lon);
        addLugarMarkers(lugares, lat, lon);
        renderLista(lugares);
      })
      .catch(function() {
        showEstado(textos.no_resultados + ' (' + ciudad + ')', true);
      });
  }

  function getRadioKm() {
    var sel = document.getElementById('mapa-radio');
    return sel ? parseFloat(sel.value) || 5 : 5;
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
