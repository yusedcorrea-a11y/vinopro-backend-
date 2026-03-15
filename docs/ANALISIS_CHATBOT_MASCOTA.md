# Análisis: creación del chatbot (mascota + panel guía)

## 1. Origen y estructura

### Dónde vive el chatbot
- **HTML:** `templates/base.html` — el chatbot está en la base común a casi todas las páginas (inicio, escanear, bodega, etc.).
- **JS:** `static/js/chatbot-guia.js` — lógica del panel (abrir/cerrar), arrastre de la mascota, doble toque/clic, y respuestas por keywords.
- **CSS:** `static/style.css` — estilos de la mascota flotante, del panel lateral y del avatar.

### Elementos en el DOM (base.html)

| Elemento | ID / clase | Función |
|--------|------------|--------|
| Contenedor flotante | `#chatbot-guia-mascot` `.chatbot-guia-mascot` | Círculo arrastrable; doble toque/clic abre el panel. |
| “Cara” de la mascota | `.chatbot-guia-mascot-face` `.chatbot-guia-mascot-frames` | Contenedor donde se pinta la imagen (vídeo o 3 PNGs). |
| Imágenes mascota | 3× `<img>` con `mascota-1/2/3.png` | Configuración actual: 3 frames animados en bucle (CSS keyframes). |
| Fondo del panel | `#chatbot-guia-backdrop` | Overlay al abrir; clic cierra. |
| Panel lateral | `#chatbot-guia-panel` | Panel deslizable con cabecera (avatar + título) y contenido (intro, input, respuestas). |
| Avatar en cabecera | `.chatbot-guia-avatar` `.chatbot-guia-avatar-frames` | Mismos 3 PNGs que la mascota, en bucle. |

### Dónde se oculta
- En **onboarding** (`body.page-onboarding`): la mascota, el backdrop y el panel tienen `visibility: hidden` y `pointer-events: none` (style.css ~1669–1672).

---

## 2. Flujo de la mascota (JS)

- **chatbot-guia.js**:
  - **initMascot(#chatbot-guia-mascot):** arrastre (mouse/touch), guarda posición en `localStorage` (`chatbot-guia-mascot-pos`), doble toque (<400 ms) o doble clic → abre el panel.
  - **openPanel / closePanel:** quitan/añaden la clase `chatbot-guia-panel--closed` y controlan el backdrop.
  - **Respuestas:** input de texto; por Enter se hace `matchTopic()` con KEYWORDS y se muestra el TEXTS correspondiente (soporte, adaptador, negocio, escanear, mapa, planes, default). No hay llamada a backend; todo es cliente.

La mascota **no** depende del JS para mostrarse: solo para arrastrar y abrir el panel. Lo que se ve dentro del círculo es solo HTML + CSS (vídeo o 3 `<img>`).

---

## 3. Visual de la mascota: por qué se ve “solo el círculo”

### Contenedor (círculo)
- `.chatbot-guia-mascot`: 72×72 px (60×60 en móvil), `border-radius: 50%`, con **fondo**:
  - Por defecto: `linear-gradient(160deg, #fff 0%, #f8f2e8 45%, #f0e6d8 100%)`.
  - En **página inicio** (`body.page-inicio`): `background: rgba(255, 255, 255, 0.22)` y borde dorado suave.

Si el **contenido interior** (las 3 imágenes) no se cargan o no se pintan, el usuario solo ve ese círculo (fondo + borde).

### Contenido interior (lo que debería verse)
- `.chatbot-guia-mascot-face` con `overflow: hidden` y `border-radius: 50%`.
- Dentro: 3 `<img>` con `mascota-1.png`, `mascota-2.png`, `mascota-3.png`:
  - `position: absolute`, `inset: 0`, `object-fit: cover`, `border-radius: 50%`.
  - Animación CSS: keyframes `mascota-fade-1/2/3` (3 s en bucle, opacidades 0/1 por frame).

Las URLs de las imágenes en base.html son:
`{{ base_url_str }}/static/images/mascota/mascota-1.png?v=3` (y 2, 3).  
`base_url_str` se inyecta en `app.py` en `render_page()` (desde `BASE_URL` o `request.base_url`).

### Hipótesis de por qué solo se ve el círculo
1. **Las imágenes no llegan al navegador:** 404 en `/static/images/mascota/mascota-*.png` (p. ej. en Render los estáticos no incluyen esa carpeta o la ruta es distinta).
2. **Caché:** Respuesta 404 antigua cacheada; por eso se añadió `?v=3` y preload.
3. **CORS / mixed content:** Poco probable si todo se sirve desde el mismo origen.
4. **Fallos de carga sin fallback:** Si las 3 `<img>` fallan, no hay ningún otro contenido (vídeo ni imagen de respaldo), por eso solo queda el círculo.

---

## 4. Historial de cambios (resumen)

| Fase | Qué se hizo |
|------|-------------|
| Inicial | Mascota con **vídeo** `mascota-chatbot.mp4` (personaje 3D) en flotante y en avatar del panel. |
| “Mascota definitiva” | Sustitución por **3 PNGs** (mascota-1/2/3.png) con animación CSS en bucle. |
| Revert | Se volvió al vídeo porque el usuario veía solo el círculo. |
| Nueva config | De nuevo 3 frames (PNGs); se mantuvo el círculo. |
| Imagen completa | Prueba con contenedor redondeado y `object-fit: contain` para ver “el zorro completo”. |
| Volver al círculo | Se revirtió a círculo y `object-fit: cover`. |
| Fix carga | URLs absolutas con `base_url_str`, `?v=3` y preload del primer frame. |

Estado actual en código: **3 PNGs** con URLs `{{ base_url_str }}/static/images/mascota/mascota-*.png?v=3` y animación CSS; si las imágenes no cargan, solo se ve el círculo.

---

## 5. Archivos implicados (checklist)

| Archivo | Rol |
|---------|-----|
| `templates/base.html` | Estructura mascota (3 img) + panel + avatar; preload mascota-1. |
| `static/style.css` | Estilos mascota, frames, keyframes, panel, avatar, page-inicio. |
| `static/js/chatbot-guia.js` | Arrastre, doble toque/clic, open/close panel, respuestas por keywords. |
| `static/images/mascota/mascota-1.png`, `mascota-2.png`, `mascota-3.png` | Assets (existen en repo, ~800 KB cada uno). |
| `app.py` | `render_page()` inyecta `base_url_str`; montaje de `/static` con StaticFiles. |

No hay ruta de backend específica para “chatbot” o “guía”: el contenido del panel es 100 % cliente (TEXTS en chatbot-guia.js).

---

## 6. Evaluación y próximos pasos sugeridos

### Lo que está bien
- Estructura clara: base.html + JS + CSS.
- Comportamiento (arrastre, doble toque, panel, respuestas) desacoplado del backend.
- Animación de 3 frames definida y mantenible.

### Problema actual
- En producción (p. ej. Render) las imágenes pueden no estar llegando (404 o no desplegadas), por lo que solo se ve el círculo (fondo del contenedor).

### Comprobación en producción (Render)
Tras cada deploy, comprobar en el navegador:
- **Imagen:** `https://<tu-app>.onrender.com/static/images/mascota/mascota-1.png?v=3`  
  - Si responde **200**: los PNG se sirven bien; la mascota mostrará los 3 frames.
  - Si responde **404**: revisar que `static/images/mascota/` esté en el repo y que el build no la excluya (`.slugignore` / `.dockerignore`). Mientras tanto, el **fallback a vídeo** mostrará el personaje.
- **Vídeo fallback:** `https://<tu-app>.onrender.com/static/videos/mascota-chatbot.mp4`  
  - Debe responder 200 para que, cuando las imágenes fallen, se vea el personaje en vídeo.

### Implementado (fallback a vídeo)
- Si la primera imagen (`mascota-1.png`) falla por `onerror` o no carga en 2,5 s (`naturalWidth === 0`), se añade la clase `chatbot-guia-mascot-face--video-fallback` al contenedor, se ocultan los 3 frames y se muestra el vídeo `mascota-chatbot.mp4` en flotante y en el avatar del panel. Así nunca se queda solo el círculo.
