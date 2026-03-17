# Revisión extensa: Llamadas, videollamada y traductor IA en chat VINEROS

**Objetivo:** Dejar cerrada y funcional la implementación de llamada de voz, videollamada y traductor en tiempo real, con revisión de código y correcciones aplicadas.

---

## 1. Resumen de lo implementado

| Funcionalidad | Dónde | Estado |
|---------------|--------|--------|
| **Llamada de voz** | Botón 📞 en hilo del chat; WebRTC solo audio | ✅ |
| **Videollamada** | Botón 📹 en hilo del chat; WebRTC audio + vídeo | ✅ |
| **Signaling WebSocket** | `/ws/call?session_id=...` en `routes/call_ws.py` | ✅ |
| **Traductor IA en llamada** | Opción en overlay: Activado/Desactivado | ✅ |
| **Recibir traducción** | Solo leer (subtítulos) / Oír voz IA | ✅ |
| **Voz IA** | Femenina / Masculina (cuando "Oír voz IA") | ✅ |
| **STT** | Web Speech API en el navegador (quien habla) | ✅ |
| **Traducción** | Backend: `translation_service.traducir` (LibreTranslate o configurado) | ✅ |
| **TTS** | `SpeechSynthesis` en el navegador (quien recibe la traducción) | ✅ |

---

## 2. Flujo técnico revisado

### 2.1 Conexión WebSocket

- **URL:** `ws(s)://host/ws/call?session_id=<sid>`
- **Requisito:** `session_id` debe corresponder a un usuario con perfil (`usuario_svc.get_username_por_session`).
- Al conectar, el servidor responde `{ "type": "registered", "username": "..." }`.
- **Cambio aplicado:** El frontend envía `set_lang` al recibir `registered`, para que el idioma quede registrado antes de que empiece la llamada.

### 2.2 Iniciar llamada (quien llama)

1. Usuario está en conversación con X (por ejemplo `/comunidad/chat/bob` → `initialUsername = "bob"`).
2. Pulsa 📞 (voz) o 📹 (vídeo).
3. `startCall(video)`:
   - Se guarda `pendingInvite = { to: callPeer, video }`.
   - Se llama a `connectCallWs()`. Si el WebSocket **aún no está abierto**, el `invite` se envía en `ws.onopen`; si **ya está abierto**, se envía en el acto.
4. Se muestra overlay "Llamando a bob…".
5. En **solo voz** se oculta el `<video>` local (`localVideo.style.display = 'none'`).

**Corrección aplicada:** Antes el `invite` podía enviarse antes de que el WS estuviera abierto y se perdía. Ahora se usa `pendingInvite` y se envía al abrir o inmediatamente si ya está abierto.

### 2.3 Recibir llamada (quien recibe)

1. El servidor reenvía `{ "type": "incoming", "from": "alice", "video": true/false }`.
2. Se muestra el modal "Te llama alice" con Aceptar / Rechazar.
3. Si acepta: se pide permiso de micrófono (y cámara si es vídeo), se crea `RTCPeerConnection`, se hace `setRemoteDescription(offer)` (el offer llega en un mensaje previo o posterior), se crea answer, se envía `answer` al servidor.
4. **ICE:** Si llegan candidatos ICE antes de tener `remoteDescription`, se guardan en `pendingIceCandidates` y se aplican al hacer `setRemoteDescription` (y al recibir `answer` en el otro lado).

**Corrección aplicada:** Cola `pendingIceCandidates` y `drainIceCandidates()` al fijar la descripción remota, para no perder ICE que lleguen antes que el answer/offer.

### 2.4 Traductor en llamada

- **Quien habla:** Con "Traductor IA" activado se inicia `SpeechRecognition` (Web Speech API) en el idioma del selector del chat. Cada resultado final se envía como `{ type: "stt_text", to: callPeer, text: "...", source_lang: "es" }`.
- **Servidor:** Recibe `stt_text`, obtiene el idioma del destinatario (`_user_lang[to_user]`), llama a `translation_service.traducir(text, target_lang, source_lang)` y envía al destinatario `{ type: "translated", from: "...", text: "...", target_lang: "..." }`.
- **Quien recibe:** Muestra el texto en la zona de subtítulos. Si tiene "Oír voz IA", reproduce el texto con `SpeechSynthesis` y la voz elegida (Femenina/Masculina) según el idioma de la traducción.

**Idioma:** Se envía `set_lang` al recibir `registered` y también en `onCallConnected()`, para que ambos tengan idioma registrado al hablar.

---

## 3. Archivos tocados

| Archivo | Cambios |
|---------|---------|
| `routes/call_ws.py` | WebSocket `/ws/call`; mensajes invite, offer, answer, ice, hangup, set_lang, stt_text, translated; `_user_lang` y traducción con `translation_svc.traducir`. |
| `static/js/chat-vineros-calls.js` | Lógica de llamada/vídeo, overlay, invitación, WebRTC, cola ICE, traductor (STT, envío stt_text, recepción translated, subtítulos, TTS con voz), `pendingInvite`, `sendSetLang()` en `registered`, ocultar vídeo local en voz, `drainIceCandidates()`. |
| `templates/chat.html` | Botones 📞/📹 en el hilo; overlay con vídeos, subtítulos, opciones Traductor (On/Off), Recibir (Leer/Oír), Voz (Femenina/Masculina); estilos para opciones y subtítulos. |
| `app.py` | Inclusión de `call_ws.router`. |

---

## 4. Comportamiento esperado (cuando haya dos usuarios)

1. **Mismo idioma, sin traductor:** Llamada o videollamada normal; cada uno oye/ve al otro sin traducción.
2. **Idiomas distintos, traductor activado (quien habla):** Lo que dice se transcribe, se traduce al idioma del otro y el otro lo ve en subtítulos o lo oye con la voz IA elegida.
3. **Solo leer:** Solo se muestran los subtítulos traducidos.
4. **Oír voz IA:** Se muestran subtítulos y además se reproduce la traducción con la voz (femenina o masculina) elegida.

---

## 5. Limitaciones conocidas (sin errores)

- **Web Speech API:** Depende del navegador y del idioma (no todos los idiomas están igual de soportados).
- **SpeechSynthesis:** Voces disponibles según navegador/OS; la elección Femenina/Masculina se hace por nombre de voz cuando existe.
- **Traducción:** Depende de `translation_service` (p. ej. LibreTranslate); si la API no está disponible, el texto no se traduce pero el resto de la llamada sigue.
- **WebRTC:** Solo STUN (Google); sin TURN puede fallar en redes/NAT estrictos.

---

## 6. Cómo probar cuando haya usuarios

1. Dos usuarios con perfil en VINEROS y al menos una conversación entre ellos.
2. Uno abre la conversación y pulsa 📞 o 📹.
3. El otro recibe "Te llama X", acepta o rechaza.
4. Durante la llamada, activar "Traductor IA" (quien quiera que se traduzca su voz) y en el otro elegir "Solo leer" o "Oír voz IA" y, si aplica, tipo de voz.
5. Hablar; el otro debe ver subtítulos y/o oír la voz traducida.

---

*Revisión aplicada: correcciones de invite con WS no abierto, set_lang en registered, vídeo local oculto en voz, cola de ICE. Implementación considerada cerrada y lista para pruebas con usuarios reales.*
