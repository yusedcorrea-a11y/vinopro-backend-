/**
 * Llamada de voz y videollamada en chat VINEROS.
 * WebSocket /ws/call para signaling; WebRTC para audio/vídeo P2P.
 */
(function() {
  'use strict';

  var sid = (window.getSessionId && window.getSessionId()) || '';
  var initialUsername = (window.CHAT_INITIAL_USERNAME || '').trim().toLowerCase();
  var callWs = null;
  var callPeer = null;
  var callVideo = false;
  var callPc = null;
  var localStream = null;
  var isIncoming = false;
  var pendingOffer = null;
  var acceptPending = false;

  var overlay = document.getElementById('chat-call-overlay');
  var remoteVideo = document.getElementById('chat-remote-video');
  var localVideo = document.getElementById('chat-local-video');
  var callStatus = document.getElementById('chat-call-status');
  var hangupBtn = document.getElementById('chat-call-hangup');
  var incomingPanel = document.getElementById('chat-call-incoming');
  var incomingName = document.getElementById('chat-call-incoming-name');
  var acceptBtn = document.getElementById('chat-call-incoming-accept');
  var rejectBtn = document.getElementById('chat-call-incoming-reject');
  var btnVoice = document.getElementById('chat-btn-voice');
  var btnVideo = document.getElementById('chat-btn-video');
  var subtitlesEl = document.getElementById('chat-call-subtitles');
  var translateOnSelect = document.getElementById('chat-call-translate-on');
  var receiveModeSelect = document.getElementById('chat-call-receive-mode');
  var voiceGenderSelect = document.getElementById('chat-call-voice-gender');
  var voiceRow = document.getElementById('chat-call-voice-row');
  var speechRecognition = null;
  var recognitionLangMap = { es: 'es-ES', en: 'en-US', ru: 'ru-RU', hi: 'hi-IN', fr: 'fr-FR', de: 'de-DE', it: 'it-IT', pt: 'pt-BR', ar: 'ar-SA', zh: 'zh-CN', ja: 'ja-JP', ko: 'ko-KR' };
  var pendingInvite = null;
  var pendingIceCandidates = [];

  function wsUrl() {
    var proto = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
    return proto + '//' + window.location.host + '/ws/call?session_id=' + encodeURIComponent(sid);
  }

  function connectCallWs() {
    if (callWs && callWs.readyState === WebSocket.OPEN) return callWs;
    if (!sid) return null;
    try {
      var ws = new WebSocket(wsUrl());
      ws.onopen = function() {
        if (pendingInvite) {
          sendCall({ type: 'invite', to: pendingInvite.to, video: pendingInvite.video });
          pendingInvite = null;
        }
      };
      ws.onclose = function() { callWs = null; };
      ws.onerror = function() { callWs = null; };
      ws.onmessage = onCallMessage;
      callWs = ws;
      return ws;
    } catch (e) {
      return null;
    }
  }

  function sendCall(msg) {
    if (callWs && callWs.readyState === WebSocket.OPEN) {
      callWs.send(JSON.stringify(msg));
    }
  }

  function showOverlay(status) {
    if (callStatus) callStatus.textContent = status || 'En llamada';
    if (overlay) overlay.classList.add('visible');
  }

  function hideOverlay() {
    stopRecognition();
    showSubtitle('');
    if (overlay) overlay.classList.remove('visible');
    if (remoteVideo) { remoteVideo.srcObject = null; }
    if (localVideo) { localVideo.srcObject = null; localVideo.style.display = ''; }
    if (localStream) {
      localStream.getTracks().forEach(function(t) { t.stop(); });
      localStream = null;
    }
    if (callPc) {
      callPc.close();
      callPc = null;
    }
    callPeer = null;
    pendingOffer = null;
    pendingIceCandidates = [];
  }

  function onCallConnected() {
    sendSetLang();
    if (translateOnSelect && translateOnSelect.value === '1') startRecognition();
    updateVoiceRowVisibility();
  }

  function hideIncoming() {
    if (incomingPanel) incomingPanel.classList.remove('visible');
  }

  function getMyLang() {
    var sel = document.getElementById('chat-lang-select');
    var v = (sel && sel.value) ? sel.value.trim().toLowerCase() : '';
    if (v === 'auto' || !v) v = (document.documentElement.getAttribute('lang') || 'es').slice(0, 2).toLowerCase();
    return v || 'es';
  }

  function sendSetLang() {
    var lang = getMyLang();
    sendCall({ type: 'set_lang', lang: lang });
  }

  function stopRecognition() {
    if (speechRecognition) {
      try { speechRecognition.stop(); } catch (e) {}
      speechRecognition = null;
    }
  }

  function startRecognition() {
    if (speechRecognition) return;
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    var lang = getMyLang();
    var recLang = recognitionLangMap[lang] || lang + '-' + lang.toUpperCase();
    var rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = false;
    rec.lang = recLang;
    rec.onresult = function(ev) {
      var res = ev.results[ev.results.length - 1];
      if (res.isFinal && callPeer) {
        var text = (res[0] && res[0].transcript) ? res[0].transcript.trim() : '';
        if (text) sendCall({ type: 'stt_text', to: callPeer, text: text, source_lang: lang });
      }
    };
    rec.onerror = function() {};
    rec.onend = function() {
      if (speechRecognition === rec && overlay && overlay.classList.contains('visible') && callPeer && translateOnSelect && translateOnSelect.value === '1') {
        try { rec.start(); } catch (e) {}
      }
    };
    try {
      rec.start();
      speechRecognition = rec;
    } catch (e) {}
  }

  function showSubtitle(text) {
    if (!subtitlesEl) return;
    subtitlesEl.textContent = text || '';
  }

  function speakTranslated(text, targetLang, preferFemale) {
    if (!text || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    var langCode = (targetLang || 'es').toLowerCase().split('-')[0];
    u.lang = recognitionLangMap[langCode] || langCode + '-' + langCode.toUpperCase();
    var voices = window.speechSynthesis.getVoices();
    var matches = voices.filter(function(v) {
      var l = (v.lang || '').toLowerCase();
      return l.indexOf(langCode) === 0;
    });
    if (matches.length) {
      var chosen = matches.find(function(v) {
        var n = (v.name || '').toLowerCase();
        if (preferFemale) return n.indexOf('female') >= 0 || n.indexOf('woman') >= 0 || n.indexOf('helena') >= 0 || n.indexOf('mujer') >= 0;
        return n.indexOf('male') >= 0 || n.indexOf('man') >= 0 || n.indexOf('hombre') >= 0;
      });
      if (chosen) u.voice = chosen; else u.voice = matches[0];
    }
    u.rate = 1;
    window.speechSynthesis.speak(u);
  }

  function updateVoiceRowVisibility() {
    if (voiceRow) voiceRow.classList.toggle('visible', receiveModeSelect && receiveModeSelect.value === 'hear');
  }

  function getIceServers() {
    return [{ urls: 'stun:stun.l.google.com:19302' }];
  }

  function createPeerConnection(isOfferer) {
    var pc = new RTCPeerConnection({ iceServers: getIceServers() });
    if (localStream) {
      localStream.getTracks().forEach(function(t) {
        pc.addTrack(t, localStream);
      });
    }
    pc.ontrack = function(ev) {
      if (remoteVideo && ev.streams && ev.streams[0]) {
        remoteVideo.srcObject = ev.streams[0];
      }
    };
    pc.onicecandidate = function(ev) {
      if (ev.candidate && callPeer) {
        sendCall({ type: 'ice', to: callPeer, candidate: ev.candidate });
      }
    };
    pc.onconnectionstatechange = function() {
      if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected' || pc.connectionState === 'closed') {
        hideOverlay();
      }
    };
    return pc;
  }

  function startCall(video) {
    if (!initialUsername || !sid) return;
    callPeer = initialUsername;
    callVideo = !!video;
    isIncoming = false;
    pendingInvite = { to: callPeer, video: callVideo };
    connectCallWs();
    if (callWs && callWs.readyState === WebSocket.OPEN) {
      sendCall({ type: 'invite', to: callPeer, video: callVideo });
      pendingInvite = null;
    }
    if (callStatus) callStatus.textContent = 'Llamando a ' + callPeer + '…';
    showOverlay('Llamando…');
    if (localVideo) localVideo.style.display = callVideo ? '' : 'none';
  }

  function getUserMedia(video, cb) {
    var constraints = { audio: true, video: !!video };
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        localStream = stream;
        if (localVideo) localVideo.srcObject = stream;
        if (cb) cb();
      }).catch(function(err) {
        if (callStatus) callStatus.textContent = 'Error: no se pudo acceder a micrófono' + (video ? ' o cámara' : '');
        if (cb) cb(err);
      });
    } else {
      if (callStatus) callStatus.textContent = 'Tu navegador no soporta llamadas';
      if (cb) cb(new Error('getUserMedia no disponible'));
    }
  }

  function doAcceptIncoming() {
    if (!callPeer) return;
    if (!pendingOffer) {
      acceptPending = true;
      if (callStatus) callStatus.textContent = 'Esperando conexión…';
      return;
    }
    hideIncoming();
    getUserMedia(callVideo, function(err) {
      if (err) return;
      if (localVideo) localVideo.style.display = callVideo ? '' : 'none';
      showOverlay('Conectando…');
      callPc = createPeerConnection(false);
      callPc.setRemoteDescription(new RTCSessionDescription(pendingOffer)).then(function() {
        drainIceCandidates();
        return callPc.createAnswer();
      }).then(function(answer) {
        return callPc.setLocalDescription(answer);
      }).then(function() {
        sendCall({ type: 'answer', to: callPeer, sdp: callPc.localDescription });
        if (callStatus) callStatus.textContent = 'En llamada con ' + callPeer;
        onCallConnected();
      }).catch(function(e) {
        if (callStatus) callStatus.textContent = 'Error al conectar';
        hideOverlay();
      });
      pendingOffer = null;
    });
  }

  function drainIceCandidates() {
    if (!callPc || !pendingIceCandidates.length) return;
    pendingIceCandidates.forEach(function(c) {
      callPc.addIceCandidate(new RTCIceCandidate(c)).catch(function() {});
    });
    pendingIceCandidates = [];
  }

  function onCallMessage(ev) {
    try {
      var msg = JSON.parse(ev.data);
    } catch (e) {
      return;
    }
    var t = (msg.type || '').toLowerCase();
    var from = (msg.from || '').trim().toLowerCase();

    if (t === 'registered') {
      sendSetLang();
    } else if (t === 'error') {
      if (callStatus) callStatus.textContent = msg.message || 'Error';
    } else if (t === 'offline') {
      hideOverlay();
      if (callStatus) callStatus.textContent = 'El usuario no está disponible';
      setTimeout(hideOverlay, 2000);
    } else if (t === 'incoming') {
      callPeer = from;
      callVideo = !!msg.video;
      isIncoming = true;
      pendingOffer = null;
      if (incomingName) incomingName.textContent = from || '';
      if (incomingPanel) incomingPanel.classList.add('visible');
    } else if (t === 'invite_ok') {
      // El otro va a enviar offer; esperamos "offer"
      if (callStatus) callStatus.textContent = 'Conectando…';
      getUserMedia(callVideo, function(err) {
        if (err) return;
        if (localVideo) localVideo.style.display = callVideo ? '' : 'none';
        callPc = createPeerConnection(true);
        callPc.createOffer().then(function(offer) {
          return callPc.setLocalDescription(offer);
        }).then(function() {
          sendCall({ type: 'offer', to: callPeer, sdp: callPc.localDescription });
          if (callStatus) callStatus.textContent = 'En llamada con ' + callPeer;
          onCallConnected();
        }).catch(function() {
          hideOverlay();
        });
      });
    } else if (t === 'offer') {
      pendingOffer = msg.sdp;
      if (!callPeer) callPeer = from;
      if (acceptPending) {
        acceptPending = false;
        doAcceptIncoming();
      }
    } else if (t === 'answer') {
      if (callPc && msg.sdp) {
        callPc.setRemoteDescription(new RTCSessionDescription(msg.sdp)).then(function() {
          drainIceCandidates();
        }).catch(function() {
          hideOverlay();
        });
      }
      if (callStatus) callStatus.textContent = 'En llamada con ' + callPeer;
      onCallConnected();
    } else if (t === 'ice') {
      if (!msg.candidate) return;
      if (callPc && callPc.remoteDescription) {
        callPc.addIceCandidate(new RTCIceCandidate(msg.candidate)).catch(function() {});
      } else {
        pendingIceCandidates.push(msg.candidate);
      }
    } else if (t === 'hangup') {
      hideOverlay();
      hideIncoming();
    } else if (t === 'hangup_ok') {
      hideOverlay();
    } else if (t === 'set_lang_ok') {
      // Idioma registrado para traductor
    } else if (t === 'translated') {
      var text = (msg.text || '').trim();
      var targetLang = (msg.target_lang || '').trim();
      showSubtitle(text);
      if (receiveModeSelect && receiveModeSelect.value === 'hear' && text && window.speechSynthesis) {
        var preferFemale = (voiceGenderSelect && voiceGenderSelect.value === 'female');
        if (window.speechSynthesis.getVoices().length === 0) {
          window.speechSynthesis.onvoiceschanged = function() {
            window.speechSynthesis.onvoiceschanged = null;
            speakTranslated(text, targetLang, preferFemale);
          };
        } else {
          speakTranslated(text, targetLang, preferFemale);
        }
      }
    }
  }

  if (hangupBtn) {
    hangupBtn.addEventListener('click', function() {
      if (callPeer) sendCall({ type: 'hangup', to: callPeer });
      hideOverlay();
    });
  }
  if (acceptBtn) {
    acceptBtn.addEventListener('click', function() {
      doAcceptIncoming();
    });
  }
  if (rejectBtn) {
    rejectBtn.addEventListener('click', function() {
      if (callPeer) sendCall({ type: 'hangup', to: callPeer });
      hideIncoming();
      callPeer = null;
    });
  }
  if (btnVoice) {
    btnVoice.addEventListener('click', function() {
      startCall(false);
    });
  }
  if (btnVideo) {
    btnVideo.addEventListener('click', function() {
      startCall(true);
    });
  }

  if (translateOnSelect) {
    translateOnSelect.addEventListener('change', function() {
      if (overlay && overlay.classList.contains('visible') && callPeer) {
        if (translateOnSelect.value === '1') startRecognition(); else stopRecognition();
      }
    });
  }
  if (receiveModeSelect) {
    receiveModeSelect.addEventListener('change', updateVoiceRowVisibility);
  }
  updateVoiceRowVisibility();

  if (sid) {
    connectCallWs();
  }
  if (window.speechSynthesis && typeof window.speechSynthesis.getVoices === 'function' && window.speechSynthesis.getVoices().length === 0) {
    window.speechSynthesis.onvoiceschanged = function() { updateVoiceRowVisibility(); };
  }
})();
