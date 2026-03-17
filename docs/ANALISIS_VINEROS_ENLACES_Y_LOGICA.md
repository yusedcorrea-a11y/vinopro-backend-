# Análisis VINEROS: enlaces y lógica (prueba general)

Solo análisis; no se ha ejecutado nada. Objetivo: comprobar que todos los enlaces estén bien unidos y que el flujo lógico sea correcto para mejorar lo que falle.

---

## 1. Mapa de rutas VINEROS (backend)

| Ruta | Descripción |
|------|-------------|
| `GET /comunidad/feed` | Feed (noticias, para ti, eventos, enoturismo, equipamiento, VINEROs). |
| `GET /comunidad/chat` | Lista de conversaciones. |
| `GET /comunidad/chat/{username}` | Hilo de chat con un usuario. |
| `GET /comunidad/perfil/{username}` | Perfil público de un usuario. |
| `GET /signup` | Registro / inicio de sesión (puerta de entrada a VINEROS). |

**APIs usadas por el front:**
- `GET /api/mi-perfil` — perfil del usuario (para "Ver mi perfil").
- `GET /api/perfil/{username}` — perfil público.
- `GET /api/feed` — posts por canal (requiere sesión para canales sociales).
- `GET /api/conversaciones` — lista de chats.
- `GET /api/chat/{username}` — mensajes con un usuario.
- `POST /api/chat/{username}` — enviar mensaje.
- `POST/DELETE /api/seguir/{username}` — seguir / dejar de seguir.
- `POST /api/crear-perfil` — crear perfil (desde signup/registro).

El router `comunidad.router` está incluido en `app.py`; no hay conflicto con otras rutas.

---

## 2. Mapa de enlaces (templates y JS)

### Desde base.html y menú secreto
- **"Chat" (botón botella):** `href="/comunidad/chat"` ✅
- **"📰 VINEROs y Noticias":** `href="/comunidad/feed"` ✅
- **"💬 Chat":** `href="/comunidad/chat"` ✅
- **"Ver mi perfil":** `href="/comunidad/feed"` en el HTML, pero el **click** está manejado en JS: pide `/api/mi-perfil` y redirige a `/comunidad/perfil/{username}` o a `/comunidad/feed` si no hay perfil ✅

### Desde index.html (inicio)
- **"Entrar en VINEROs":** `href="/signup"` ✅
- **"¿Ya tienes cuenta? Iniciar sesión":** `href="/signup"` ✅

### Desde feed.html
- **"Registrarme" / "¿Ya tienes cuenta? Iniciar sesión":** `href="/signup"` ⚠️ **Sin `?next=`** — tras iniciar sesión el usuario va a `/inicio`, no vuelve al feed.
- **"Mi bodega" (sin perfil):** `href="/bodega"` ✅

### Desde perfil.html
- **"← Feed":** `href="/comunidad/feed"` ✅
- **"Chatear":** `href="/comunidad/chat/{{ perfil_username | e }}"` ✅

### Desde chat.html
- **"Volver" (desde hilo):** `href="/comunidad/chat"` ✅

### Desde chat-vineros.js
- **Cada conversación:** `<a href="/comunidad/chat/{other}">` ✅
- **Sin perfil / error 401:** enlaces a `CHAT_SIGNUP_URL` = `/signup?next=/comunidad/chat` ✅ (el login sí redirige a `next`).

### Desde signup.html
- **Tras registro:** redirige siempre a `'/inicio'` ⚠️ **No usa `?next=`** — si el usuario entró desde "Registrarme" del feed, después de registrarse va a inicio, no al feed.
- **Tras login:** usa `?next=` y redirige a `dest` (p. ej. `/comunidad/chat` si vino con `next`) ✅

### Desde recuperar-password.html
- **"Volver a Entrar en VINEROs":** `href="/signup"` ✅

### Desde onboarding
- **Registrarme:** `href="/signup"` ✅

---

## 3. Lógica de flujo (resumen)

| Flujo | Estado |
|-------|--------|
| Inicio → Entrar en VINEROs → Signup → (registro) → Redirige a /inicio | ✅ Correcto (pero podría ofrecer ir al feed). |
| Inicio → Entrar en VINEROs → Signup → (login con ?next=) → Redirige a next | ✅ Correcto. |
| Feed sin sesión → Registrarme/Iniciar sesión → Signup (sin next) → Login → /inicio | ⚠️ Usuario no vuelve al feed. |
| Chat sin sesión → CTA → Signup?next=/comunidad/chat → Login → /comunidad/chat | ✅ Correcto. |
| Menú → Ver mi perfil → /api/mi-perfil → /comunidad/perfil/{username} o /comunidad/feed | ✅ Correcto. |
| Menú → VINEROs y Noticias / Chat → /comunidad/feed, /comunidad/chat | ✅ Correcto. |
| Feed → (click en post) | ⚠️ El **username** del post no es enlace a perfil (solo texto). |
| Perfil → Chatear → /comunidad/chat/{username} | ✅ Correcto. |
| Chat lista → click conversación → /comunidad/chat/{username} | ✅ Correcto. |
| Chat hilo → Volver → /comunidad/chat | ✅ Correcto. |

---

## 4. Lo que está bien

1. **Rutas HTML y API** de comunidad definidas y coherentes (feed, chat, perfil, signup).
2. **Menú secreto:** enlaces a feed y chat correctos; "Ver mi perfil" resuelve bien por JS con `/api/mi-perfil` y redirige a perfil o feed.
3. **Chat:** enlaces a lista y a hilo correctos; sin sesión se ofrece signup con `?next=/comunidad/chat` y el login respeta `next`.
4. **Perfil:** enlace al feed y al chat con ese usuario correctos; APIs de seguir/dejar de seguir y de valoraciones/actividad usadas bien.
5. **Onboarding e inicio:** enlaces a signup correctos.

---

## 5. Lo que está mal o falta (mejoras)

### 5.1 Feed sin perfil: volver al feed tras login/registro
- **Dónde:** `templates/feed.html` — botones "Registrarme" e "Iniciar sesión" con `href="/signup"`.
- **Problema:** No llevan `?next=/comunidad/feed`, así que tras login el usuario va a `/inicio` y no vuelve al feed.
- **Mejora:** Usar `href="/signup?next=/comunidad/feed"` en ambos botones del bloque `feed-sin-perfil`.

### 5.2 Registro: respetar `?next=` después de crear cuenta
- **Dónde:** `templates/signup.html` — tras registro exitoso: `window.location.href = '/inicio'`.
- **Problema:** Si el usuario entró desde `/signup?next=/comunidad/feed` (o cualquier otra `next`), tras registrarse siempre va a `/inicio`.
- **Mejora:** Leer `next` de la query (igual que en el login) y, si existe y es ruta segura (p. ej. empieza por `/` y no es absoluta externa), redirigir a `next`; si no, a `/inicio`.

### 5.3 Feed: ir al perfil desde el nombre de usuario del post
- **Dónde:** `static/js/feed.js` — en `renderPost` el nombre de usuario se pinta en `.vineros-name` como texto, no como enlace.
- **Problema:** No se puede ir al perfil de quien publicó desde el feed.
- **Mejora:** Hacer que el nombre de usuario sea un enlace a `/comunidad/perfil/{username}` (solo para posts de tipo usuario/sponsor con username válido; no para "canal" o sistema). Ej.: `<a href="/comunidad/perfil/...">` en el `vineros-name`.

### 5.4 (Opcional) Feed: "Ver en Bodega"
- **Dónde:** `feed.js` — botón `data-action="bodega"` que solo muestra/oculta el detalle del vino en la tarjeta.
- **Observación:** No lleva a `/bodega` ni a la ficha del vino en bodega; puede generar expectativa de "ir a mi bodega". Valorar añadir un enlace real a bodega o a una ficha del vino si existe ruta.

---

## 6. Resumen ejecutivo

- **Enlaces principales (menú, chat, perfil, feed, signup, onboarding):** bien enlazados y coherentes con las rutas.
- **Lógica "Ver mi perfil" y chat con `?next=`:** correcta.
- **Pendiente de mejorar:**
  1. Añadir `?next=/comunidad/feed` en los enlaces a signup desde el feed (sin perfil).
  2. Hacer que el registro respete `?next=` y redirija allí tras crear cuenta.
  3. Hacer que el nombre de usuario en los posts del feed sea enlace a `/comunidad/perfil/{username}`.

Con estos tres cambios, la red social VINEROS queda con enlaces y flujo lógico alineados para la prueba general.
