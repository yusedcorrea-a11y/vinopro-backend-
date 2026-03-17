# Análisis: Llamada de voz y videollamada en el chat VINEROS

**Objetivo:** Saber si se puede añadir llamada de voz y videollamada entre usuarios en el chat de la comunidad (VINEROS).

**Respuesta corta:** **Sí, es posible.** Requiere añadir signaling en tiempo real (WebSockets) en el backend y WebRTC en el frontend. Es un desarrollo de complejidad media.

---

## Cómo está hoy el chat VINEROS

- **Backend:** `routes/comunidad.py` + `services/chat_service.py`. Mensajes de texto 1-a-1 entre usuarios, guardados en `data/chat_mensajes.json`.
- **API:** `GET /api/conversaciones`, `GET /api/chat/{username}`, `POST /api/chat/{username}` (solo texto).
- **Frontend:** `templates/chat.html` + `static/js/chat-vineros.js`: lista de conversaciones, hilo de mensajes, traducción automática. **Solo texto**, sin audio ni vídeo.

---

## Qué hace falta para voz y vídeo

### 1. WebRTC (estándar en navegadores)

- **Audio y vídeo** entre dos navegadores (o app) **P2P** (peer-to-peer).
- Cada usuario: micrófono (y cámara si es videollamada), `getUserMedia()` → `RTCPeerConnection` → intercambio de oferta/respuesta SDP y candidatos ICE.

### 2. Signaling (intercambio de ofertas/respuestas)

- WebRTC necesita que ambos peers **intercambien** la oferta SDP, la respuesta SDP y los ICE candidates.
- Hoy el chat solo tiene **REST** (request/response). Para “en tiempo real” hace falta un canal persistente:
  - **WebSockets** en el mismo backend (recomendado): FastAPI soporta WebSockets. Un endpoint tipo `/ws/chat` donde cada usuario se conecta con su `username`/sesión; el servidor reenvía “A quiere llamar a B”, “oferta de A para B”, “respuesta de B para A”, “ICE de A”, “ICE de B”, etc.
- Alternativa: usar un servicio externo de signaling (ej. Socket.io en otro servicio), pero añade dependencia y despliegue.

### 3. Servidores TURN/STUN (recomendado para producción)

- **STUN:** permite descubrir la IP pública; muchos usan uno público (ej. `stun:stun.l.google.com:19302`).
- **TURN:** retransmite el tráfico cuando P2P no puede (NAT/firewall estrictos). Aquí sí suele hace falta un servicio (Twilio, Xirsys, o coturn self-hosted).
- Sin TURN, la llamada puede fallar para parte de los usuarios; con TURN suele funcionar en casi todos los casos.

---

## ¿Se puede añadir?

| Aspecto | Conclusión |
|--------|------------|
| **¿Técnicamente posible?** | Sí. WebRTC + WebSockets es el enfoque estándar. |
| **Backend** | Añadir un endpoint WebSocket (ej. `/ws/chat` o `/ws/signal`) para signaling entre los dos usuarios de la conversación. |
| **Frontend** | En la pantalla del hilo (chat con un usuario), botones “Llamar” y “Videollamada”; al pulsar, abrir WS, `getUserMedia`, `RTCPeerConnection`, intercambiar SDP/ICE por el WS. |
| **Base actual** | El chat ya tiene identidad (usuario A, usuario B) y lista de conversaciones; solo falta el canal en tiempo real y la UI de llamada. |

---

## Esfuerzo aproximado (orientativo)

- **Signaling (WebSocket en backend):** 1–2 días (protocolo mínimo: “invite”, “offer”, “answer”, “ice”, “hangup”; comprobar que solo participen los dos usuarios de esa conversación).
- **Frontend (botones + WebRTC):** 2–3 días (conectar WS, crear oferta/respuesta, mostrar vídeo local/remoto, colgar, manejar errores y permisos de mic/cámara).
- **TURN (opcional pero recomendado):** 0,5–1 día si usas un proveedor; más si montas coturn tú mismo.
- **UX “te están llamando”:** 0,5–1 día (notificación cuando el otro inicia la llamada; depende de si ya tienes notificaciones en tiempo real o polling).

En total, **una semana de desarrollo** (una persona) es una estimación razonable para una primera versión con voz + vídeo y signaling por WebSocket, sin contar integración con app móvil si más adelante se hace.

---

## Resumen

- **Sí se puede** implementar llamada de voz y videollamada en el chat VINEROS.
- **Requisitos principales:** WebSockets en el backend para signaling, WebRTC en el frontend, y opcionalmente un servidor TURN para mejor conectividad.
- El esfuerzo es **medio** (varios días) y encaja con la arquitectura actual del chat (mismo concepto de conversación 1-a-1 entre dos usuarios).

---

## Implementación (primera versión)

- **Backend:** `routes/call_ws.py` — WebSocket `GET /ws/call?session_id=...`. Eventos: register (implícito), invite, incoming, invite_ok, offer, answer, ice, hangup, offline. Solo usuarios con perfil (session → username) pueden conectar.
- **Frontend:** Botones 📞 (voz) y 📹 (videollamada) en el hilo del chat; `static/js/chat-vineros-calls.js` conecta al WS, envía invite, maneja incoming (Aceptar/Rechazar), WebRTC con STUN (stun.l.google.com:19302), overlay de llamada y modal de llamada entrante.
- **Traductor IA en llamada:** Durante la llamada el usuario puede activar "Traductor IA". Su idioma se toma del selector del chat (o del navegador). Lo que habla se envía como texto (STT con Web Speech API) al servidor, que traduce al idioma del otro usuario y le envía el texto traducido. El otro puede elegir "Solo leer" (subtítulos) o "Oír voz IA" (TTS en su idioma) y la voz "Femenina" o "Masculina". Backend: mensajes `set_lang`, `stt_text` y `translated` en `/ws/call`; se usa `translation_service.traducir`.
- **Pruebas:** Abre una conversación con otro usuario (los dos con perfil). Uno pulsa Llamar o Videollamada; el otro recibe "Te llama X" y puede Aceptar o Rechazar. Con "Traductor IA" activado, habla en tu idioma; el otro ve/oye la traducción según haya elegido Leer u Oír y el tipo de voz.
