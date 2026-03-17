# Resumen para Gemini: implementación de hoy en VINO PRO IA (backend)

**Fecha:** 6 de marzo de 2026 (sesión con Cursor)  
**Objetivo:** Dejar la app estable en Render, con canal de noticias, mejoras de UX y diagnóstico de GNews.

---

## 1. Canal de noticias (VINEROs)

- **Backend:** Servicio `services/news_service.py` que consulta **GNews** con la búsqueda "wine" (y fallback "vino" en español). Caché de 2 horas en `data/noticias_cache.json`. Si no hay `GNEWS_API_KEY` o la API falla, se usan noticias estáticas de `canales_feed.json`.
- **Endpoint:** `GET /api/noticias?limit=20` devuelve noticias en el mismo formato que el feed (posts con `post_type: canal`).
- **Frontend:** En la página del feed (`/comunidad/feed`) la pestaña **Noticias** es la primera y por defecto. Al entrar se llama a `/api/noticias` y se muestran tarjetas (imagen, título, fuente, descripción). Al tocar una tarjeta se abre el enlace en nueva pestaña. Botones "Actualizar" y "Sonido" (mute) en la barra cuando está activa la pestaña Noticias.
- **Menú:** El ítem del menú que antes era "Comunidad" pasó a **"VINEROs y Noticias"** y sigue enlazando a `/comunidad/feed`.
- **Inicio:** No se muestra enlace a noticias en la pantalla principal (se quitó "Canal de noticias de vino" para no saturar la home).

---

## 2. GNews: diagnóstico y robustez (para Render)

- **API Key:** Se usa `os.getenv("GNEWS_API_KEY", "").strip()` para evitar espacios.
- **Error 400:** Si GNews devuelve 400, se hace log del cuerpo: `print("DEBUG GNews Error: {r.text}")` para ver en logs de Render si es "Invalid API Key", "Out of quota", etc.
- **Resiliencia:** Ante 400, otro HTTP error o excepción, la función devuelve **noticias de respaldo** (estáticas) y no propaga el error; el frontend no se rompe.
- **Script de prueba:** `test_api.py` en la raíz. Ejecutar con `python test_api.py` (con `GNEWS_API_KEY` en .env o entorno) para comprobar si el token es válido antes de desplegar.

---

## 3. Archivos estáticos y caché

- **StaticFiles:** Sigue montado en `/static` con `html=True`. Se añadió un **middleware** que pone `Cache-Control: public, max-age=3600` en las respuestas de `/static` para reducir 304 y ruido en los logs de Render.

---

## 4. Páginas de error amigables

- **404:** `templates/404.html` con mensaje claro y enlace "Volver al inicio".
- **500:** `templates/500.html` con mensaje y enlace al inicio.
- **app.py:** Handlers de excepción para `HTTPException` (404 → plantilla 404) y para `Exception` genérica (500 → plantilla 500, con fallback HTML si falla el render).

---

## 5. Mejoras de prioridad media (plan de mejoras)

- **¿Olvidaste tu contraseña?** En el formulario de login (`/signup`) hay enlace a `/recuperar-password`. Esa página muestra texto tipo "Contacta con soporte" y un `mailto` con `support_email` (ej. soporte@vinoproia.com).
- **Inicio:** En la pantalla principal se añadió la línea **"¿Ya tienes cuenta? Iniciar sesión"** con enlace a `/signup`.
- **Chat sin sesión:** Cuando la API del chat devuelve 401, además del mensaje se muestran botones **"Registrarme"** e **"Iniciar sesión"** que llevan a `/signup?next=/comunidad/chat`. Tras iniciar sesión, si existe `?next=`, se redirige a esa ruta. Si se entra a signup con `?next=`, se muestra por defecto el formulario de "Iniciar sesión".

---

## 6. Mejoras de prioridad baja

- **Avatar en registro:** Label "Foto de perfil (opcional, máx. 5 MB)" y validación en el cliente: si la foto supera 5 MB, se muestra un aviso y no se envía el formulario.
- **Rate limit 429:** El backend ya devolvía un mensaje claro. En el front (escaneo y feed) cuando la respuesta es 429 se muestra ese mensaje en lugar del error genérico.
- **Escaneo:** Tras un error se muestra un botón **"Reintentar"** que oculta el error, limpia el resultado y hace scroll al formulario.
- **Privacidad:** Enlace visible a **Privacidad** en el menú (a `/privacidad`) y en un **footer** en todas las páginas. Estilos de la página legal/privacidad mejorados para mejor legibilidad (texto más oscuro, fondo claro en tarjetas).

---

## 7. Adaptador (legibilidad)

- En la página del adaptador se mejoró contraste y tamaños de fuente: contenedor con fondo más sólido (claro/oscuro), títulos y textos más grandes, bloques de código con mejor lectura.

---

## 8. Feed sin perfil (ya estaba; se mantiene)

- Cuando no hay sesión o no hay posts, se muestra un bloque con "Crea tu perfil…", botón "Registrarme", enlace "¿Ya tienes cuenta? Iniciar sesión" y enlace a Bodega. Estilos para ese bloque en `feed.html`.

---

## Despliegue (Render)

- Todo está en **GitHub** (rama `main`). Render hace deploy automático al hacer push.
- Variables de entorno relevantes en Render: `GNEWS_API_KEY` (para noticias en vivo), `GOOGLE_API_KEY`, `SUPPORT_EMAIL`, etc.
- Tras el deploy, si GNews falla con 400, en los **logs de Render** aparecerá `DEBUG GNews Error: ...` con el cuerpo de la respuesta para diagnosticar (token inválido, cuota, etc.). La app seguirá mostrando noticias de respaldo.

---

## Cómo probar la key GNews en local

Desde la raíz del backend:

```bash
python test_api.py
```

Comprueba que `GNEWS_API_KEY` esté en `.env` o en el entorno; el script hace una petición a gnews.io e indica si el token es válido.

---

*Resumen generado para pasar contexto a Gemini (otra sesión / otro agente).*
