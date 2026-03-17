# Revisión de la app: qué funciona, qué no y por qué

**Fecha:** Marzo 2026  
**Alcance:** App móvil (Expo, `app/` + `lib/api.ts`) y backend (FastAPI) que usa.

---

## 1. Lo que **SÍ funciona** (y por qué)

### Inicio (pestaña Inicio)
- **Botones y enlaces:** Los botones "Escanear etiqueta" y "Preguntar al sumiller" llevan a `/scan` y a la pestaña Sumiller. "Más opciones" (Sumiller, Lugares, Mi Bodega) enlaza bien.
- **Feed Comunidad:** La app llama a `GET /api/feed?canal=para_ti&limit=20`. El backend (`routes/comunidad.py`) devuelve `posts` con `image_url`, `title`, `description`, etc. Las tarjetas se muestran a ancho completo. Si el backend o la red fallan, se muestra el mensaje de error y el texto de fallback.

### Escanear (`app/scan.tsx`)
- **Código de barras / QR:** Se envía `POST /escanear` con `{ codigo_barras: codigo }`. El backend acepta JSON y responde con el vino o mensaje. Correcto.
- **Foto / galería:** Se envía `POST /escanear` con `FormData` y campo `imagen`. El backend espera `form.get("imagen")` en multipart. Coincide.
- **Buscar por texto:** Se envía `POST /escanear` con `{ texto }`. El backend lo acepta. Correcto.
- **Preguntar al sumiller (después de escanear):** Se usa `consulta_id` del resultado y `GET /preguntar-sumiller?texto=...&consulta_id=...&lang=...`. El backend responde y, si `lang` no es `es`, traduce. Correcto.
- **Añadir a mi bodega (desde resultado):** Se usa `POST /api/bodega/botellas` con `vino_nombre`, `vino_key`, `cantidad`. El backend tiene la ruta y valida. Correcto.

### Sumiller (pestaña Sumiller)
- **Chat:** Se envía `GET /preguntar-sumiller?texto=...&perfil=aficionado&lang=...`. El backend responde (y traduce si `lang` no es `es`). Correcto.
- **Idioma:** La app envía `lang` con el idioma del dispositivo (`expo-localization`). La respuesta se traduce en backend. Correcto.

### Mi Bodega
- **Listar:** `GET /api/bodega` con `X-Session-ID`. El backend devuelve `botellas`, `limite_max`, `es_pro`, `total_botellas`. La app usa ahora ese `limite_max` y `es_pro` para el subtítulo (corregido en esta revisión).
- **Añadir:** `POST /api/bodega/botellas`. Requiere sesión. Correcto.
- **Eliminar:** `DELETE /api/bodega/botellas/{id}`. Correcto.
- **Exportar PDF:** La app hace `GET` a `{api.baseUrl}/informes/bodega` con los headers de sesión. El backend tiene `GET /informes/bodega`. Hoy la app solo muestra un aviso de que el PDF está en la web; no descarga el archivo en el móvil (limitación de React Native sin módulo de descarga). Funciona en la web.

### Mapa (Lugares destacados)
- **Cargar lugares:** La app llama a `GET /api/lugares-destacados`. El router de geolocalización tiene `prefix="/api"` y la ruta `/lugares-destacados`, así que la URL final es correcta.
- **Datos:** Existe `data/lugares_destacados.json` con al menos un lugar (Casa Paca). Si el archivo está vacío o falta, la lista saldría vacía pero no rompe.
- **Ver ruta:** Se abre Google Maps con `Linking.openURL`. Correcto.

### API y sesión
- **Base URL:** La app usa `extra.apiUrl` de `app.json` (ahora `https://vinopro-backend-1.onrender.com`) o `EXPO_PUBLIC_API_URL` o, por defecto, `https://vinoproia.com`. Si el backend real está en Render, hay que tener `apiUrl` en `app.json` apuntando a esa URL (ya está así).
- **X-Session-ID:** Se genera una vez con `getSessionId()` y se envía en todas las peticiones. El backend lo usa para bodega, historial y contexto del sumiller. Correcto.

---

## 2. Lo que se **corrigió** en esta revisión

### Límite de bodega (plan Gratis)
- **Problema:** En el frontend se mostraba "X / 50 botellas (plan Gratis)" pero el backend tiene `LIMITE_GRATIS = 30` en `freemium_service.py`. El usuario podía creer que podía tener 50 y el backend rechazaba a partir de 31.
- **Solución:** El tipo `BodegaResponse` incluye ahora `limite_max`, `total_botellas` y `es_pro`. La pantalla Bodega usa `limite_max` que devuelve el API (30 para Gratis, `null` para PRO) y muestra "X / 30 botellas (plan Gratis)" o "X botellas (PRO)" si es PRO.

---

## 3. Lo que **no funciona** o puede fallar (y por qué)

### ~~App.js y ScannerScreen (código legacy)~~ **Corregido**
- **Qué era:** `App.js` importaba `src/screens/ScannerScreen.tsx` y `src/services/api.ts` (localhost:8000, rutas `/scan` que no existen en el backend).
- **Qué se hizo:** Se eliminaron `App.js`, `App.js.backup`, `src/screens/ScannerScreen.tsx` y `src/services/api.ts`. En `frontend/src/` queda un `README.md` explicando que la app usa `app/` y `lib/api.ts`.

### Informe PDF de bodega en el móvil
- **Qué hace la app:** Al pulsar "Exportar PDF" se hace `GET /informes/bodega` y se muestra un aviso de que el informe está en la web.
- **Por qué no descarga:** En React Native/Expo, descargar un PDF y abrirlo requiere algo tipo `expo-file-system` + compartir o abrir con otra app. No está implementado.
- **Conclusión:** Funciona en la web; en la app es solo informativo. No es un fallo, es una limitación asumida.

### Feed si el backend no devuelve `posts`
- **Comportamiento:** Si la API devuelve solo `actividad` y `eventos` (formato antiguo) y no `posts`, la app muestra el bloque de "eventos" y "actividad" en formato de lista antigua, no las tarjetas tipo Instagram. Si no hay nada, muestra "Eventos y actividad de la comunidad aparecerán aquí".
- **Conclusión:** No rompe; hay fallback. Para ver las tarjetas con imagen hace falta que el backend envíe `posts` (canal `para_ti` ya lo hace).

### Traducción del sumiller
- **Dependencia:** La traducción usa LibreTranslate (URL por defecto o `LIBRETRANSLATE_URL`). Si ese servicio no está disponible o falla, el backend devuelve la respuesta en español (fallback en el código).
- **Conclusión:** Siempre hay respuesta; a lo sumo sin traducir.

### URL del backend en producción
- **app.json** tiene `apiUrl: "https://vinopro-backend-1.onrender.com"`. Si en producción el backend está realmente en `https://vinoproia.com` (mismo dominio que la web), habría que unificar: o la app apunta a `vinoproia.com` o el backend de Render está detrás de ese dominio. Si no, la app en producción seguiría usando la URL de Render, que es correcto si ese es tu backend.

---

## 4. Resumen rápido

| Área | Estado | Nota |
|------|--------|------|
| Inicio, botones, feed | OK | Feed con posts e imagen; fallback si no hay posts. |
| Escanear (código, foto, texto) | OK | Backend acepta imagen, texto y codigo_barras. |
| Sumiller (chat + idioma) | OK | Traducción según `lang`. |
| Mi Bodega (listar, añadir, eliminar) | OK | Límite corregido: se usa `limite_max` y `es_pro` del API. |
| Mapa (lugares destacados) | OK | `/api/lugares-destacados` y JSON existen. |
| Exportar PDF (móvil) | Limitado | Solo aviso; descarga real en la web. |
| App.js / ScannerScreen / src/services/api | Eliminado | Código legacy eliminado; solo queda app/ y lib/api.ts. |

Si quieres, el siguiente paso puede ser: eliminar o aislar el código legacy (`App.js`, `src/screens/ScannerScreen.tsx`, `src/services/api.ts`) para evitar confusiones, o revisar otra parte concreta de la app o del backend.
