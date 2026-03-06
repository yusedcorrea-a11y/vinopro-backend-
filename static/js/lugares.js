(function() {
  'use strict';

  function escapeHtml(text) {
    return String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function normalizeWebUrl(raw) {
    var url = (raw || '').trim();
    if (!url) return '';
    if (!/^https?:\/\//i.test(url)) return 'https://' + url;
    return url;
  }

  function buildRouteUrl(lugar) {
    var destination = (lugar && lugar.direccion) ? lugar.direccion : ((lugar && lugar.lat != null && lugar.lon != null) ? (lugar.lat + ',' + lugar.lon) : '');
    if (!destination) return '';
    return 'https://www.google.com/maps/dir/?api=1&destination=' + encodeURIComponent(destination);
  }

  function buildSponsorMedia(lugar) {
    if (lugar.logo_url) {
      return '<img class="mapa-sponsor-logo-img" src="' + escapeHtml(lugar.logo_url) + '" alt="Logo de ' + escapeHtml(lugar.nombre || 'establecimiento') + '" loading="lazy">';
    }
    var initial = (lugar.nombre || 'L').trim().charAt(0).toUpperCase();
    return '<div class="mapa-sponsor-logo-placeholder">' + escapeHtml(initial || 'L') + '</div>';
  }

  function renderLugarCard(lugar, opts, textos) {
    opts = opts || {};
    textos = textos || {};
    var dist = lugar.distancia_km != null ? lugar.distancia_km + ' ' + (textos.distancia || 'km') : '';
    var isSponsor = !!(opts.destacado || lugar.patrocinador);
    var sponsorBadge = isSponsor ? '<span class="mapa-badge-patrocinador">Patrocinador PRO</span>' : '';
    var destacadoBadge = opts.destacado ? '<span class="mapa-badge-destacado">Recomendado</span>' : '';
    var html = '<div class="mapa-card-top">';
    html += '<div class="mapa-card-media">' + buildSponsorMedia(lugar) + '</div>';
    html += '<div class="mapa-card-main">';
    html += '<h4>' + escapeHtml(lugar.nombre || '—') + ' ' + destacadoBadge + '</h4>';
    html += '<div class="mapa-badges-wrap">' + sponsorBadge + '</div>';
    if (lugar.direccion) html += '<p class="direccion">' + escapeHtml(lugar.direccion) + '</p>';
    if (lugar.descripcion) html += '<p class="direccion">' + escapeHtml(lugar.descripcion) + '</p>';
    html += '<p class="meta">' + escapeHtml(lugar.tipo || '') + (dist ? ' · ' + escapeHtml(dist) : '') + '</p>';
    html += '</div></div>';

    html += '<div class="acciones">';
    html += '<button type="button" class="btn btn-outline" data-action="route">' + escapeHtml(textos.ver_ruta || 'Ver ruta') + '</button>';
    if (lugar.email) html += '<button type="button" class="btn btn-outline" data-action="email">Email</button>';
    if (lugar.web) html += '<button type="button" class="btn btn-outline" data-action="web">Web</button>';
    html += '</div>';
    return html;
  }

  function openAction(lugar, action) {
    if (!lugar) return;
    if (action === 'route') {
      var routeUrl = buildRouteUrl(lugar);
      if (routeUrl) window.open(routeUrl, '_blank', 'noopener');
      return;
    }
    if (action === 'email') {
      if (!lugar.email) return;
      window.location.href = 'mailto:' + encodeURIComponent(lugar.email);
      return;
    }
    if (action === 'web') {
      var url = normalizeWebUrl(lugar.web);
      if (!url) return;
      window.open(url, '_blank', 'noopener');
    }
  }

  window.LugaresUI = {
    renderLugarCard: renderLugarCard,
    openAction: openAction
  };
})();
