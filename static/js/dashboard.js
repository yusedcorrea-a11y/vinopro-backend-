/**
 * Dashboard: carga /analytics/dashboard y rellena totales, tendencias, por país, preguntas frecuentes.
 */
(function() {
  fetch('/analytics/dashboard?dias=30')
    .then(function(r) { return r.json(); })
    .then(function(d) {
      var numBusquedas = document.getElementById('num-busquedas');
      var numEscaneos = document.getElementById('num-escaneos');
      var numPreguntas = document.getElementById('num-preguntas');
      if (numBusquedas) numBusquedas.textContent = d.total_busquedas != null ? d.total_busquedas : '-';
      if (numEscaneos) numEscaneos.textContent = d.total_escaneos != null ? d.total_escaneos : '-';
      if (numPreguntas) numPreguntas.textContent = d.total_preguntas != null ? d.total_preguntas : '-';

      var t = document.getElementById('tendencias');
      if (t) {
        (d.tendencias || []).forEach(function(x) {
          var li = document.createElement('li');
          li.textContent = (x.query || '') + ' (' + (x.veces || 0) + ' veces)';
          t.appendChild(li);
        });
        if (!(d.tendencias && d.tendencias.length)) t.innerHTML = '<li class="texto-pequeno">Sin datos aún.</li>';
      }

      var p = document.getElementById('por-pais');
      if (p) {
        (d.por_pais || []).forEach(function(x) {
          var div = document.createElement('div');
          div.className = 'texto-pequeno';
          div.style.marginBottom = '0.5rem';
          div.textContent = (x.pais || '') + ': ' + (x.escaneos || 0) + ' escaneos, ' + (x.busquedas || 0) + ' búsquedas';
          p.appendChild(div);
        });
        if (!(d.por_pais && d.por_pais.length)) p.innerHTML = '<p class="texto-pequeno">Sin datos por país.</p>';
      }

      var pf = document.getElementById('preguntas-frecuentes');
      if (pf) {
        (d.preguntas_frecuentes || []).forEach(function(x) {
          var li = document.createElement('li');
          li.innerHTML = (x.pregunta || '') + ' <em>(' + (x.veces || 0) + ')</em>';
          pf.appendChild(li);
        });
        if (!(d.preguntas_frecuentes && d.preguntas_frecuentes.length)) pf.innerHTML = '<li class="texto-pequeno">Sin preguntas registradas.</li>';
      }
    })
    .catch(function() {
      var t = document.getElementById('tendencias');
      if (t) t.innerHTML = '<li class="mensaje error">Error al cargar datos.</li>';
    });
})();
