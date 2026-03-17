# Comparativa: VINO PRO vs el mercado (llamadas, videollamada y traductor)

**Objetivo:** Comparar nuestro trabajo con lo que ofrecen otras apps — tanto de vino como de comunicación — para ver cómo quedamos y qué nos hace distintos.

---

## 1. Qué tenemos nosotros (resumen)

### Comunidad VINEROS + comunicación

| Funcionalidad | Descripción |
|---------------|-------------|
| **Chat entre vineros** | Mensajería por conversación (por usuario), con historial. |
| **Traducción del chat** | Los mensajes se traducen al idioma de lectura del destinatario (LibreTranslate). |
| **Llamada de voz** | Botón en el hilo → WebRTC solo audio, de vinero a vinero. |
| **Videollamada** | Botón en el hilo → WebRTC audio + vídeo. |
| **Traductor en la llamada** | Durante voz/vídeo: quien habla en su idioma → el otro recibe **traducción en tiempo real**. |
| **Cómo recibir la traducción** | **Solo leer:** subtítulos en pantalla. **Oír:** voz sintética (TTS) con elección de voz **femenina o masculina**. |
| **STT** | Reconocimiento de voz en el navegador (Web Speech API), idioma del selector del chat. |
| **Backend** | Servidor traduce (translation_service) y reenvía texto traducido al otro peer. |

Todo esto está **dentro de la app de vino**: mismo producto donde escaneas, consultas al experto, tienes bodega, compras y ahora te comunicas (chat, voz, vídeo) con otros vineros, con traducción si hace falta.

---

## 2. Apps de vino: ¿tienen llamadas o traductor en llamada?

| App | Chat / mensajes | Llamada de voz | Videollamada | Traducción en llamada |
|-----|-----------------|----------------|--------------|------------------------|
| **Vivino** | No chat 1-a-1 entre usuarios. Sí comentarios, @amigos, feed de amigos, compartir fotos. | No | No | No |
| **Delectable** | Social tipo Instagram (fotos, recomendaciones), no chat directo ni llamadas. | No | No | No |
| **CellarTracker** | Feed, actividad, CellarChat (IA sobre tu bodega). No chat persona a persona ni llamadas. | No | No | No |
| **Vinora / Vinozo / Sommo** | Enfoque IA/sommelier y bodega. No se documenta chat entre usuarios ni llamadas. | No* | No* | No |
| **VINO PRO** | Chat 1-a-1, feed, perfil, seguir. | Sí (WebRTC) | Sí (WebRTC) | Sí (subtítulos + TTS, voz fem/masc) |

\* No encontrado en búsquedas ni documentación pública.

**Conclusión (vino):** Ninguna app de vino que hemos revisado ofrece **chat directo + llamada de voz + videollamada + traductor en tiempo real** integrado. En ese bloque, estamos solos.

---

## 3. Apps de comunicación / reuniones: ¿traducción en llamada?

Aquí sí hay oferta, pero en otro contexto: **reuniones (Meet, Zoom, Teams)**, no dentro de una app vertical como el vino.

| Solución | Tipo | Traducción en tiempo real | Subtítulos | Voz (TTS) | Integrado en app de vino |
|----------|------|---------------------------|------------|-----------|---------------------------|
| **Google Meet** (Speech Translation) | Nativo en Meet | Sí (varios idiomas) | Sí | Sí (voz similar al hablante) | No; es reuniones genéricas |
| **Talo AI** | Bot en Meet/Teams/Zoom | Sí, 60 idiomas | Sí | Sí | No |
| **Transync AI** | Integración Meet/Teams/Zoom | Sí, 60 idiomas, baja latencia | Sí | Sí (voces naturales) | No |
| **InterMIND** | Plataforma de videollamada propia | Sí, instantánea | Sí | Sí | No |
| **Speak Freely Pro** | App, 100+ idiomas | Sí (voz/vídeo) | Subtítulos bilingües | Sí | No |
| **PolyTalk, Calingo, VoiceHop** | Extensiones / add-ons para Meet/Zoom/Teams | Sí | Sí | Sí (según producto) | No |
| **VINO PRO** | Dentro de la app (chat VINEROS) | Sí (quien habla → traducido al otro) | Sí | Sí + elegir voz fem/masc | **Sí** |

**Conclusión (comunicación):** Las que traducen en llamada son **herramientas de reunión o complementos** (Meet, Zoom, Teams + add-ons). Ninguna es una **app de vino con comunidad** que lleve voz, vídeo y traductor integrados en el mismo producto.

---

## 4. Dónde quedamos: combinación única

- **Apps de vino:** Tienen comunidad/red social (Vivino, Delectable, CellarTracker), pero **no** chat 1-a-1, **no** llamadas ni videollamadas, **no** traductor en la llamada.
- **Apps de reuniones/traducción:** Tienen traducción en tiempo real (subtítulos + voz), pero son **productos horizontales** (reuniones de trabajo, eventos), no un ecosistema “vinos + comunidad + comunicación traducida”.

**VINO PRO** junta en un solo sitio:

1. **Vertical vino:** escaneo, experto, bodega, compra, guías, noticias, certificaciones.
2. **Comunidad:** perfil, seguir, feed, **chat 1-a-1**.
3. **Comunicación rica:** **llamada de voz** y **videollamada** desde el chat.
4. **Sin barrera de idioma en la llamada:** traductor en tiempo real (subtítulos y/o **voz IA** con elección femenina/masculina).

Eso no significa “revolución tecnológica” a nivel de algoritmo (STT/TTS/traducción ya existen), pero sí es **revolución de producto** en el segmento vino: **ninguna app de vino ofrece hoy esta pila (chat + voz + vídeo + traductor integrado)**. Y en el segmento “traducción en llamada”, nosotros lo tenemos **dentro de nuestra app**, sin depender de Meet/Zoom ni de una app externa.

---

## 5. Resumen en una frase

**En apps de vino:** no hay competidor con chat + llamada + videollamada + traductor en tiempo real (leer + oír con voz elegida). **En apps de reuniones:** hay traducción en llamada, pero son productos genéricos, no una app de vino con comunidad. **Nosotros:** somos la única combinación “app de vino + comunidad + voz/vídeo con traductor integrado”; el trabajo está cerrado y listo para cuando puedan probar con usuarios reales.

---

*Documento basado en: funcionalidades del backend y frontend (call_ws, chat-vineros-calls, translation_service), docs de revisión de llamadas/traductor, y búsquedas sobre Vivino, Delectable, CellarTracker, Google Meet, Talo AI, Transync AI, InterMIND, Speak Freely Pro (2024-2025).*
