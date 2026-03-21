# VINEROS: movimiento y vídeo embebido (YouTube, sin API key)

## Objetivo

- Sensación de **red viva**: animaciones CSS (aurora en el hero, Ken Burns en imágenes de tarjetas tipo canal, hover suave).
- **Reproductor** en la pestaña **En vivo** cuando el backend resuelve un **ID de vídeo de 11 caracteres** y el cliente muestra un iframe `youtube-nocookie` (autoplay **silenciado** salvo `prefers-reduced-motion: reduce`).

## Datos en `data/canales_feed.json` (sección `en_vivo`)

Por cada entrada puedes usar **una** de estas opciones (el backend las prueba en este orden):

1. **`youtube_embed_video_id`** — ID fijo del vídeo (11 caracteres), copiado de la URL `watch?v=XXXXXXXXXXX`.
2. **`youtube_playlist_id`** — ID de lista (`list=PL…` en la URL del playlist). El servidor lee el RSS público de YouTube y toma el **primer** vídeo de la lista (caché ~10 min).
3. **`youtube_channel_uc`** — ID de canal (`UC…`, 24 caracteres). Mismo RSS `channel_id=…` y primer vídeo subido.

Si las tres están vacías, la tarjeta sigue mostrando imagen + enlace, pero con **animación** en la foto (Ken Burns).

> **Nota:** El RSS de YouTube a veces devuelve 404 según canal, región o cambios de plataforma. Si falla, usa `youtube_embed_video_id` con un vídeo reciente del canal.

## Cómo obtener IDs

- **Vídeo:** Abre el vídeo → Compartir → el enlace contiene `v=`.
- **Lista:** Abre la playlist → URL `...&list=PLxxxx` (copia solo el valor de `list`).
- **Canal UC:** En la página del canal, “Acerca de” / “Compartir canal” o la URL `youtube.com/channel/UC...`.

## Privacidad y UX

- Dominio **youtube-nocookie.com** para el embed.
- Autoplay solo **muteado**; con *reducir movimiento* del sistema, autoplay desactivado en el iframe.
- Los campos internos `youtube_playlist_id` y `youtube_channel_uc` **no** se envían al cliente en la respuesta JSON del feed (solo el `youtube_embed_video_id` resuelto).

## Competencia / diferenciación

Combinación poco habitual en feeds tipo “solo foto”: **editorial tipográfico + micro‑movimiento + opción de vídeo in‑app** sin clonar el patrón de una sola red grande.
