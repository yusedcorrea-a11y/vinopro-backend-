# Recorrido de Usuario (User Journey) – MVP VINO PRO

Informe de simulación del estado actual de la app: cómo interactúa un usuario con cada flujo y cómo quedan integrados **Casa Paca** y **Catas Divertidas**. Sirve para validar partners, detectar enlaces rotos y presentar el producto a tus 40 contactos de Turín.

---

## 1. Pantalla de inicio y acceso a recomendaciones

### 1.1 Landing (/) y Inicio (/inicio)

- **Landing (/)**: Logo VINO PRO IA, tagline, “Probar la app web” → `/inicio`, “Próximamente en Google Play”, formulario “Avísame” (guarda en `notificaciones_landing.json`).
- **Inicio (/inicio)**: Dos CTAs principales:
  - **Preguntar al experto en vinos** → `/preguntar`
  - **Escanear etiqueta** → `/escanear`

Las recomendaciones de **Restaurante Asador Casa Paca** no están en la pantalla de inicio; están en la sección **Mapa / Lugares cerca**.

### 1.2 Dónde se ven Casa Paca y “Lugares recomendados”

- **Ruta:** `/mapa` (en el menú: “Lugares cerca” / “Places nearby”).
- **Flujo:**
  1. Al cargar la página, el JS llama a `GET /api/lugares-destacados`.
  2. El backend lee `data/lugares_destacados.json` y devuelve la lista (Casa Paca con nombre, dirección, descripción, email `casapaca@hotmail.es`).
  3. Se muestra la sección **“Lugares recomendados”** arriba del mapa, con tarjetas que incluyen:
     - Nombre + badge “Recomendado”
     - Dirección: Puebla de Sanabria, Zamora, Castilla y León
     - Descripción (maridajes, descorches)
     - Botones: Ver ruta (Google Maps), Email (mailto)
  4. Los marcadores de estos lugares se añaden al mapa al cargar.
- **Persistencia:** JSON estático; no depende de sesión. Los 14 idiomas aplican a los títulos de sección vía `t('comunidad.lugares_recomendados')` (es/en/it ya tienen clave).

**Resumen:** Un usuario que entra a “Lugares cerca” ve desde el primer momento a Casa Paca como establecimiento destacado, con contacto visible.

---

## 2. Escáner OCR: de la etiqueta a la información

### 2.1 Entrada

- **Ruta API:** `POST /escanear`
- **Acepta:** `multipart/form-data` (texto, imagen, codigo_barras) o `application/json` (texto, codigo_barras).
- **Identificación:** Header opcional `X-Session-ID` (para historial y límites).

### 2.2 Flujo paso a paso

1. **Si se envía imagen:**
   - Backend usa `ocr_service.extraer_texto_de_imagen(contenido)` (Tesseract).
   - El texto extraído se concatena a `texto_busqueda`.
   - Si Tesseract no está disponible → respuesta con `error_imagen: true` y mensaje para el usuario.

2. **Si se envía código de barras y no hay texto:**
   - `api_externa_service.buscar_por_codigo_barras(codigo_barras)` → **Open Food Facts** (`/api/v0/product/{barcode}.json`).
   - Si OFF devuelve producto: se normaliza a ficha vino (nombre, bodega, país, región, etc.), se guarda en `registrados.json` y en memoria (`consultas_escaneo`), y se devuelve al cliente con `encontrado_en_bd: false` y mensaje de “información externa guardada”.

3. **Búsqueda por texto (OCR o manual):**
   - `busqueda_service.buscar_vinos_avanzado(vinos, texto_busqueda, limite=5)` sobre el catálogo cargado (JSON de todos los países).
   - Si hay coincidencia con score ≥ 1.0 → se devuelve como `encontrado_en_bd: true` con `vino`, `vino_key`, `otros_resultados`.
   - Si no hay match en BD:
     - `api_externa_service.buscar_por_texto(texto_busqueda, limite=1)` → búsqueda en **Open Food Facts** por texto.
     - Si hay resultado: mismo flujo que código de barras (guardar en `registrados.json`, devolver con mensaje).
   - Si tampoco hay resultado externo: se devuelve un vino “genérico” con nombre = texto buscado y descripción indicando que no se encontró en BD ni fuentes externas; no se persiste en `registrados.json` (origen genérico).

4. **Persistencia:**
   - Vinos de OFF o de búsqueda externa → `data/registrados.json` (y se inyectan en el catálogo en memoria para futuras búsquedas).
   - Historial de escaneos por sesión → `request.app.state.historial_escaneos` (en memoria, últimas 50).
   - Analytics (si existe el servicio) → registro de escaneo (en BD / archivo según tu configuración).

### 2.3 Respuesta típica al cliente

- `encontrado_en_bd`: true/false  
- `consulta_id`: para usar en “Preguntar al experto en vinos” y comprar  
- `vino`, `vino_key`, `mostrar_boton_comprar`  
- `es_pro`: según `freemium_service.is_pro(session_id)`  

**Resumen:** OCR (Tesseract) → texto; texto/código → BD local o Open Food Facts; resultado unificado y, si procede, guardado en JSON. La “IA local” del experto en vinos no interviene en el escaneo; interviene en **Preguntar** (ver más abajo).

---

## 3. Sección Comunidad: Catas Divertidas y “seguir”

### 3.1 Feed de actividad (/comunidad/feed)

- **API:** `GET /api/feed`  
  No exige sesión: si no hay `X-Session-ID` o no hay perfil, igualmente se devuelven los **eventos destacados**.

- **Respuesta:**  
  `{ "actividad": [ ... ], "eventos": [ ... ] }`
  - **eventos:** Publicaciones de tipo `"evento"` en `data/actividad.json` (ordenadas por fecha). Ahí está la publicación de **Catas Divertidas**: título “Wine Tasting Experiences con Catas Divertidas”, texto promocional, enlace a perfil.
  - **actividad:** Solo si el usuario tiene sesión **y** perfil **y** sigue a alguien: valoraciones, “probado”, “deseado” de los usuarios seguidos.

- **Plantilla (feed.html):**
  - Primero se renderizan los **eventos** (tarjeta con username, badge “Evento”, título, texto, enlace “Ver perfil” → `/comunidad/perfil/catas_divertidas`).
  - Luego la **actividad** clásica (usuario X valoró/probó/quiere probar [vino] con link a oferta/crear).

- **Persistencia:**  
  - Eventos: `data/actividad.json` (tipo `"evento"` con `titulo`, `texto`, `link`).  
  - Actividad de usuarios: mismo archivo (tipo `valoracion`|`probado`|`deseado`).  
  - Perfiles: `data/usuarios_perfiles.json`.

### 3.2 Cómo “seguir” a Catas Divertidas

- El perfil **catas_divertidas** existe en `usuarios_perfiles.json` (session_id de seed para no colisionar con usuarios reales).
- **Flujo:**
  1. Usuario con sesión crea perfil: `POST /api/crear-perfil` (username, bio, ubicación).
  2. Luego puede seguir: `POST /api/seguir/catas_divertidas` (con `X-Session-ID`).
  3. Se crea relación en `data/seguidores.json` y se envía notificación “nuevo_seguidor” al seguido.
  4. A partir de ahí, su feed incluirá también la **actividad** de Catas Divertidas (si en el futuro se añaden valoraciones/probado/deseado con ese username).

**Resumen:** En Comunidad, el usuario ve primero el evento de Catas Divertidas; puede entrar al perfil y seguirles. La publicidad queda integrada en el flujo de la red social.

---

## 4. Bodega y pago PRO (Stripe)

### 4.1 Límite bodega (Gratis vs PRO)

- **Servicio:** `freemium_service`
  - **Límite plan Gratis:** 50 vinos (suma de cantidades en `data/bodegas.json` por `session_id`).
  - **PRO:** `session_id` en `data/usuarios_pro.json` → sin límite.

- **Al añadir botella:** `POST /api/bodega/botellas` (o la ruta que use el frontend bajo el prefijo correcto).  
  Backend llama a `freemium_svc.puede_anadir_botella(session_id, cantidad)`. Si no es PRO y supera 50, devuelve error con mensaje “Pasa a PRO para bodega ilimitada”.

### 4.2 Cómo se refleja que un usuario es PRO (webhook Stripe)

1. Usuario entra en **Planes** (`/planes`), elige PRO y el frontend pide URL de checkout:  
   `POST /api/crear-checkout` (o equivalente) con `session_id` (y URLs de éxito/cancelación).  
   Backend: `stripe_service.crear_checkout_session(session_id, success_url, cancel_url)` → devuelve URL de Stripe Checkout (4,99 €/mes, `client_reference_id = session_id`).

2. Usuario paga en Stripe; Stripe envía **webhook** a `POST /webhook-stripe` (en producción debe ser la URL pública configurada en el Dashboard).

3. Backend en `stripe_service.procesar_webhook(payload, signature)`:
   - Verifica firma con `STRIPE_WEBHOOK_SECRET`.
   - Si el evento es `checkout.session.completed`, toma `client_reference_id` (= session_id).
   - Llama a `freemium_service.add_pro_user(session_id)` → añade ese `session_id` a `data/usuarios_pro.json` (lista `pro_users`).

4. A partir de ese momento:
   - `freemium_svc.is_pro(session_id)` devuelve `True`.
   - Las respuestas de bodega y escaneo pueden incluir `es_pro: true`.
   - El límite de 50 deja de aplicarse para esa sesión.

**Persistencia:**  
- PRO: `data/usuarios_pro.json`.  
- Bodega: `data/bodegas.json` (por session_id).

**Resumen:** El estado PRO se refleja solo después de que Stripe confirme el pago vía webhook y el backend actualice `usuarios_pro.json`. No hay “PRO” hasta que ese webhook se ejecute correctamente.

---

## 5. Idiomas (14) y persistencia JSON

### 5.1 Idiomas

- **Servicio:** `services/i18n.py`  
  - `IDIOMAS_SOPORTADOS`: es, en, pt, fr, de, it, ar, ru, tr, zh, ja, ko, hi, he.  
  - Idioma: cookie `vino_pro_lang` (por defecto `es`).  
  - Cambio: `GET /set-lang?lang=it` → redirige y fija cookie 1 año.  
  - Traducciones: `data/translations/{lang}.json`; función `t('clave.subclave')` en plantillas y rutas que pasan `t` al contexto.

- Las páginas HTML se renderizan con `render_page(request, ..., t=t)`; el menú, feed, mapa, planes, etc. usan claves traducidas. La lógica de negocio (APIs) no suele devolver textos traducidos; la UI sí.

### 5.2 Persistencia en JSON (resumen)

| Dato | Archivo | Cuándo se usa |
|------|---------|----------------|
| Catálogo de vinos | Múltiples JSON por país en `data/` (excl. ver abajo) | Carga al arranque en `vinos_mundiales` |
| Vinos añadidos por escaneo/OFF | `registrados.json` | Escaneo y búsquedas |
| Bodega por usuario | `bodegas.json` | GET/POST/DELETE bodega |
| Usuarios PRO | `usuarios_pro.json` | Stripe webhook, freemium |
| Perfiles comunidad | `usuarios_perfiles.json` | Feed, seguir, perfil público |
| Actividad y eventos | `actividad.json` | Feed (eventos + valoraciones/probado/deseado) |
| Seguidores | `seguidores.json` | API seguir / dejar de seguir |
| Lugares destacados | `lugares_destacados.json` | Mapa “Lugares recomendados” |
| Notificaciones landing | `notificaciones_landing.json` | Formulario “Avísame” |

Excluidos de la carga como catálogo de vinos (en `app.py`): analytics, bodegas, conocimiento_vinos, enlaces_compra, restaurantes, registros_diarios, usuarios_reputacion, usuarios_pro, ofertas, valoraciones, wishlist, historial_usuario, notificaciones_landing, usuarios_perfiles, seguidores, actividad, notificaciones, contactos_qr, lugares_destacados.

---

## 6. Escena resumida: Casa Paca y Catas Divertidas

- **Casa Paca:** Aparece en **Mapa → Lugares recomendados**, con descripción de maridajes y descorches, y email `casapaca@hotmail.es` visible. No en la pantalla de inicio.
- **Catas Divertidas:** Aparece en **Comunidad → Feed** como primera “publicación” (evento): título y texto de Wine Tasting Experiences, y enlace al perfil para seguir. El perfil existe y puede recibir seguidores.

Con esto puedes revisar en el código que no haya enlaces rotos entre FastAPI y el frontend (Expo o web) y usar el mismo documento para explicar a tus 40 contactos de Turín qué se descargan y cómo se ve la app con partners reales. Cuando tengas ingresos, el siguiente paso recomendado es migrar estos JSON a una base de datos SQL para endurecer seguridad y escalabilidad.
