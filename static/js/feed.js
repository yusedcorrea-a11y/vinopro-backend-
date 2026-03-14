/**
 * VINEROS feed: infinite scroll, stories y traducción universal de comentarios.
 */
(function() {
  'use strict';

  var sid = window.getSessionId ? window.getSessionId() : '';
  var htmlLang = (document.documentElement.getAttribute('lang') || 'es').toLowerCase();
  var userLang = htmlLang;
  var LANG_STORAGE_KEY = 'vineros_target_lang';
  var langSelect = document.getElementById('vineros-lang-select');
  var feedList = document.getElementById('feed-list');
  var feedSinPerfil = document.getElementById('feed-sin-perfil');
  var feedLoading = document.getElementById('feed-loading');
  var listEl = document.getElementById('vineros-list');
  var storiesWrap = document.getElementById('vineros-stories-wrap');
  var storiesEl = document.getElementById('vineros-stories');
  var observerEl = document.getElementById('feed-observer');
  var feedTabs = document.getElementById('feed-tabs');
  var offset = 0;
  var limit = 8;
  var loading = false;
  var hasMore = true;
  var currentCanal = 'noticias';
  var FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&fit=crop';

  function resolveAutoLang() {
    var navLang = ((navigator.language || navigator.userLanguage || '') + '').toLowerCase();
    if (navLang.indexOf('ru') === 0) return 'ru';
    if (navLang.indexOf('hi') === 0) return 'hi';
    if (navLang.indexOf('en') === 0) return 'en';
    if (navLang.indexOf('es') === 0) return 'es';
    return (htmlLang || 'es').slice(0, 2);
  }

  function getSelectedLangValue() {
    if (!langSelect) return 'auto';
    return (langSelect.value || 'auto').toLowerCase();
  }

  function getEffectiveTargetLang() {
    var sel = getSelectedLangValue();
    if (sel === 'auto') {
      return (htmlLang || 'es').slice(0, 2);
    }
    return sel;
  }

  function initLangSelector() {
    if (!langSelect) return;
    var saved = '';
    try { saved = (localStorage.getItem(LANG_STORAGE_KEY) || '').toLowerCase(); } catch (_) {}
    var valid = ['auto', 'es', 'en', 'ru', 'hi'];
    if (saved && valid.indexOf(saved) !== -1) {
      langSelect.value = saved;
    } else {
      langSelect.value = 'auto';
    }
    userLang = getEffectiveTargetLang();
    langSelect.addEventListener('change', function() {
      var next = getSelectedLangValue();
      try { localStorage.setItem(LANG_STORAGE_KEY, next); } catch (_) {}
      userLang = getEffectiveTargetLang();
      if (feedList && feedList.style.display !== 'none') setCanal(currentCanal);
    });
  }

  function showLoading() { if (feedLoading) feedLoading.style.display = 'block'; }
  function hideLoading() { if (feedLoading) feedLoading.style.display = 'none'; }
  function showList() {
    if (feedList) feedList.style.display = 'block';
    if (feedSinPerfil) feedSinPerfil.style.display = 'none';
  }
  function showSinPerfil() {
    if (feedList) feedList.style.display = 'none';
    if (feedSinPerfil) feedSinPerfil.style.display = 'block';
    hideLoading();
  }

  function escapeHtml(text) {
    return String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function renderDetail(det) {
    if (!det) return '';
    return '<div class="vineros-detail" data-detail>' +
      '<p><strong>Nombre:</strong> ' + escapeHtml(det.nombre || 'No disponible') + '</p>' +
      '<p><strong>Bodega:</strong> ' + escapeHtml(det.bodega || 'No disponible') + '</p>' +
      '<p><strong>Región:</strong> ' + escapeHtml(det.region || 'No disponible') + ' · <strong>País:</strong> ' + escapeHtml(det.pais || 'No disponible') + '</p>' +
      '<p><strong>Tipo:</strong> ' + escapeHtml(det.tipo || 'No disponible') + (det.anada ? ' · <strong>Añada:</strong> ' + escapeHtml(det.anada) : '') + '</p>' +
      (det.puntuacion ? '<p><strong>Puntuación:</strong> ' + escapeHtml(det.puntuacion) + '</p>' : '') +
      (det.maridaje ? '<p><strong>Maridaje:</strong> ' + escapeHtml(det.maridaje) + '</p>' : '') +
      (det.precio_estimado ? '<p><strong>Precio estimado:</strong> ' + escapeHtml(det.precio_estimado) + '</p>' : '') +
      '</div>';
  }

  function translateComment(descEl, translateBtn) {
    if (!descEl || !translateBtn) return;
    var original = descEl.getAttribute('data-original-text') || descEl.textContent || '';
    if (!original.trim()) return;
    if (descEl.getAttribute('data-translated') === '1') return;

    descEl.classList.add('translating');
    translateBtn.disabled = true;
    translateBtn.textContent = '🌐 Traduciendo...';

    var headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' };
    if (sid) headers['X-Session-ID'] = sid;

    fetch('/api/translate-comment', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        texto_original: original,
        idioma_destino: getEffectiveTargetLang(),
      }),
    })
      .then(function(r) {
        if (!r.ok) throw new Error('No se pudo traducir');
        return r.json();
      })
      .then(function(data) {
        var translated = (data && data.texto_traducido) ? data.texto_traducido : original;
        descEl.textContent = translated;
        descEl.classList.remove('translating');
        descEl.classList.add('translated');
        descEl.setAttribute('data-translated', '1');
        translateBtn.textContent = '🌐 Traducido';
      })
      .catch(function() {
        descEl.classList.remove('translating');
        translateBtn.textContent = '🌐 Traducir';
        translateBtn.disabled = false;
      });
  }

  function renderPost(post, isNoticias) {
    if (!listEl) return;
    isNoticias = !!isNoticias;
    var card = document.createElement('article');
    card.className = 'vineros-card' + (post.post_type === 'sponsor' ? ' sponsor' : '') + (isNoticias ? ' vineros-card--noticia' : '');
    card.setAttribute('data-post-id', post.id || '');
    card.setAttribute('data-post-username', post.username || '');
    if (isNoticias && post.link) card.setAttribute('data-noticia-link', post.link);
    var badge = post.badge ? '<span class="vineros-badge">' + escapeHtml(post.badge) + '</span>' : '';
    var hasImage = !!(post.image_url);
    var hasSponsorImg = post.post_type === 'sponsor' && hasImage;
    var mediaClass = post.post_type === 'sponsor' ? ('vineros-media sponsor-media' + (hasSponsorImg ? ' vineros-media--img' : '')) : (hasImage ? 'vineros-media vineros-media--img' : 'vineros-media');
    var mediaContent = '';
    if (hasImage || post.post_type === 'canal') {
      var imgUrl = post.image_url || FALLBACK_IMAGE;
      mediaContent = '<img class="vineros-media-img" src="' + escapeHtml(imgUrl) + '" alt="" loading="lazy" />';
    } else if (post.post_type === 'sponsor') {
      mediaContent = '<span class="vineros-media-placeholder">Patrocinador PRO</span>';
    } else {
      mediaContent = '<span class="vineros-media-placeholder">VINEROS</span>';
    }
    var safeDescription = escapeHtml(post.description || '');
    var extraBtn = '';
    if (post.post_type === 'canal' && post.link) {
      extraBtn = '<a class="vineros-btn primary" href="' + escapeHtml(post.link) + '" target="_blank" rel="noopener">Leer más</a>';
    } else if (post.post_type === 'sponsor' && post.link) {
      extraBtn = '<a class="vineros-btn primary" href="' + escapeHtml(post.link) + '">Descubre</a>';
    } else if (post.vino_detalle) {
      extraBtn = '<button class="vineros-btn primary" data-action="bodega">Ver en Bodega</button>';
    }
    var actionsHtml = isNoticias
      ? '<div class="vineros-actions">' + (post.link ? ('<a class="vineros-btn primary" href="' + escapeHtml(post.link) + '" target="_blank" rel="noopener">Leer más</a>') : '') + '</div>'
      : '<div class="vineros-actions">' +
          '<button class="vineros-btn" data-action="brindar">🍷 Brindar ' + (post.brindis_count ? '(' + post.brindis_count + ')' : '') + '</button>' +
          '<button class="vineros-btn" data-action="comentar">Comentar ' + (post.comentarios_count ? '(' + post.comentarios_count + ')' : '') + '</button>' +
          '<button class="vineros-btn" data-action="translate">🌐 Traducir</button>' +
          extraBtn +
        '</div>';
    card.innerHTML =
      '<div class="vineros-head">' +
        '<div class="vineros-head-left">' +
          '<div class="vineros-avatar">' + escapeHtml(post.avatar_text || 'V') + '</div>' +
          '<div><div class="vineros-name">' + escapeHtml(post.username || 'vinero') + badge + '</div></div>' +
        '</div>' +
        '<button type="button" class="vineros-head-menu" aria-label="Más opciones" title="Más opciones">⋮</button>' +
      '</div>' +
      '<div class="' + mediaClass + '">' + mediaContent + '</div>' +
      '<div class="vineros-body">' +
        '<h3 class="vineros-title">' + escapeHtml(post.title || 'Publicación') + '</h3>' +
        '<p class="vineros-desc" data-comment data-original-text="' + safeDescription + '" data-translated="0">' + safeDescription + '</p>' +
        actionsHtml +
        (isNoticias ? '' : renderDetail(post.vino_detalle)) +
      '</div>';

    if (isNoticias && post.link) {
      card.style.cursor = 'pointer';
      card.addEventListener('click', function(e) {
        if (e.target.closest('a, button')) return;
        window.open(post.link, '_blank', 'noopener');
      });
    } else {
      card.addEventListener('click', function(e) {
        var btn = e.target.closest('[data-action]');
        if (!btn) return;
        var action = btn.getAttribute('data-action');
        if (action === 'brindar') {
          var n = parseInt((btn.getAttribute('data-count') || '0'), 10) + 1;
          btn.setAttribute('data-count', String(n));
          btn.textContent = '🍷 Brindar (' + n + ')';
          return;
        }
        if (action === 'comentar') {
          var texto = window.prompt('Escribe tu comentario rápido:');
          if (texto && texto.trim()) window.alert('Comentario enviado en VINEROS 🍷');
          return;
        }
        if (action === 'translate') {
          var desc = card.querySelector('[data-comment]');
          translateComment(desc, btn);
          return;
        }
        if (action === 'bodega') {
          var detail = card.querySelector('[data-detail]');
          if (detail) detail.classList.toggle('visible');
        }
      });
    }

    listEl.appendChild(card);
  }

  function renderStories(stories) {
    if (!storiesEl || !storiesWrap) return;
    var list = stories || [];
    if (!list.length) {
      storiesWrap.style.display = 'none';
      storiesEl.innerHTML = '';
      return;
    }
    storiesWrap.style.display = 'block';
    storiesEl.innerHTML = '';
    list.forEach(function(story) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'vineros-story' + (story.post_type === 'sponsor' ? ' sponsor' : '');
      btn.setAttribute('data-post-id', story.post_id || '');
      btn.innerHTML =
        '<span class="vineros-story-ring"><span class="vineros-story-avatar">' + escapeHtml(story.avatar_text || 'V') + '</span></span>' +
        '<span class="vineros-story-label">' + escapeHtml(story.username || 'vinero') + '</span>';
      btn.addEventListener('click', function() {
        var postId = btn.getAttribute('data-post-id') || '';
        if (!postId) return;
        var target = document.querySelector('[data-post-id="' + postId.replace(/"/g, '\\"') + '"]');
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
      storiesEl.appendChild(btn);
    });
  }

  function setCanal(canal) {
    currentCanal = canal || 'para_ti';
    offset = 0;
    hasMore = currentCanal !== 'noticias';
    if (listEl) listEl.innerHTML = '';
    if (feedTabs) {
      var tabs = feedTabs.querySelectorAll('.feed-tab');
      tabs.forEach(function(t) {
        t.classList.toggle('active', (t.getAttribute('data-canal') || '') === currentCanal);
      });
    }
    var noticiasTools = document.getElementById('noticias-tools');
    if (noticiasTools) noticiasTools.style.display = currentCanal === 'noticias' ? 'flex' : 'none';
    if (storiesWrap) storiesWrap.style.display = (currentCanal === 'para_ti' || currentCanal === 'vineros') ? 'block' : 'none';
    if (storiesEl) storiesEl.innerHTML = '';
    if (currentCanal === 'noticias') fetchNoticias(); else fetchNextPage();
  }

  function fetchNoticias() {
    if (loading) return;
    loading = true;
    showLoading();
    if (feedLoading) feedLoading.textContent = 'Cargando noticias de vino…';
    fetch('/api/noticias?limit=20', { headers: { 'Accept': 'application/json' } })
      .then(function(r) {
        if (r.status === 429) return { posts: [], _429: true };
        return r.json();
      })
      .then(function(data) {
        if (data && data._429) {
          loading = false;
          hideLoading();
          if (feedLoading) feedLoading.textContent = 'Demasiadas solicitudes. Espera un momento e inténtalo de nuevo.';
          feedLoading.style.display = 'block';
          showList();
          return;
        }
        loading = false;
        hideLoading();
        var posts = (data && data.posts) ? data.posts : [];
        if (!posts.length) {
          if (feedLoading) feedLoading.textContent = 'No hay noticias por ahora. Toca actualizar en un momento.';
          feedLoading.style.display = 'block';
          showList();
          return;
        }
        showList();
        if (listEl) listEl.innerHTML = '';
        posts.forEach(function(p) { renderPost(p, true); });
        if (feedLoading) {
          feedLoading.textContent = 'Canal de noticias de vino. Arriba/abajo para ver más.';
          feedLoading.style.display = 'block';
        }
      })
      .catch(function() {
        loading = false;
        hideLoading();
        if (feedLoading) feedLoading.textContent = 'Error al cargar noticias. Toca actualizar.';
        feedLoading.style.display = 'block';
        showList();
      });
  }

  function fetchNextPage() {
    if (loading || !hasMore) return;
    loading = true;
    showLoading();
    var headers = { 'Accept': 'application/json' };
    if (sid) headers['X-Session-ID'] = sid;
    var lang = getEffectiveTargetLang() || 'es';
    var url = '/api/feed?canal=' + encodeURIComponent(currentCanal) + '&offset=' + encodeURIComponent(offset) + '&limit=' + encodeURIComponent(limit) + '&lang=' + encodeURIComponent(lang);
    fetch(url, { headers: headers })
      .then(function(r) {
        if (r.status === 401) { showSinPerfil(); return null; }
        if (r.status === 429) return r.json().then(function(d) { return { _429: true, detail: d && d.detail }; });
        return r.json();
      })
      .then(function(data) {
        loading = false;
        hideLoading();
        if (!data) return;
        if (data._429) {
          if (feedLoading) feedLoading.textContent = (data.detail && (typeof data.detail === 'string' ? data.detail : data.detail.detail)) || 'Demasiadas solicitudes. Espera un momento e inténtalo de nuevo.';
          feedLoading.style.display = 'block';
          showList();
          return;
        }
        if (offset === 0) renderStories(data.stories || []);
        var posts = data.posts || [];
        if (!posts.length && offset === 0) {
          showSinPerfil();
          return;
        }
        showList();
        posts.forEach(function(p) { renderPost(p, false); });
        offset = data.next_offset || (offset + posts.length);
        hasMore = !!data.has_more;
        if (!hasMore && feedLoading) {
          feedLoading.textContent = 'Has visto todas las publicaciones de VINEROS.';
          feedLoading.style.display = 'block';
        }
      })
      .catch(function() {
        loading = false;
        showSinPerfil();
      });
  }

  if (feedTabs) {
    feedTabs.querySelectorAll('.feed-tab').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var canal = btn.getAttribute('data-canal') || 'para_ti';
        if (canal === currentCanal) return;
        setCanal(canal);
      });
    });
  }

  if ('IntersectionObserver' in window && observerEl) {
    var io = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting && currentCanal !== 'noticias') fetchNextPage();
      });
    }, { rootMargin: '500px 0px' });
    io.observe(observerEl);
  }

  var noticiasRefresh = document.getElementById('noticias-refresh');
  if (noticiasRefresh) {
    noticiasRefresh.addEventListener('click', function() {
      if (currentCanal === 'noticias') fetchNoticias();
    });
  }
  var noticiasMute = document.getElementById('noticias-mute');
  if (noticiasMute) {
    var muted = false;
    try { muted = localStorage.getItem('vineros_sound_muted') === '1'; } catch (_) {}
    noticiasMute.setAttribute('aria-pressed', muted ? 'true' : 'false');
    var muteIcon = noticiasMute.querySelector('.noticias-mute-icon');
    var muteLabel = noticiasMute.querySelector('.noticias-mute-label');
    if (muteIcon) muteIcon.textContent = muted ? '🔇' : '🔊';
    if (muteLabel) muteLabel.textContent = muted ? 'Silenciado' : 'Sonido';
    noticiasMute.addEventListener('click', function() {
      muted = !muted;
      try { localStorage.setItem('vineros_sound_muted', muted ? '1' : '0'); } catch (_) {}
      noticiasMute.setAttribute('aria-pressed', muted ? 'true' : 'false');
      if (muteIcon) muteIcon.textContent = muted ? '🔇' : '🔊';
      if (muteLabel) muteLabel.textContent = muted ? 'Silenciado' : 'Sonido';
    });
  }

  initLangSelector();
  setCanal('noticias');
})();
