# Resumen VINO PRO IA – Para empezar una nueva conversación

**Última actualización:** 2026-02-20  
**Objetivo:** Tener todo el contexto del proyecto al abrir un nuevo chat.

---

## Qué es el proyecto

**VINO PRO IA** es un backend + frontend (FastAPI + plantillas Jinja2) de una app tipo “sumiller virtual”: escaneo de etiquetas, registro de vinos, bodega virtual, preguntas al sumiller, planes (Gratis/PRO), pagos con Stripe, compra (enlaces por vino), adaptador para restaurantes y dashboard de analytics.

- **Puerto:** 8001  
- **Arranque:** `uvicorn app:app --host 127.0.0.1 --port 8001` (o `python app.py` si está configurado)

---

## Lo que está hecho (resumen)

### 1. Núcleo y búsqueda
- Carga de vinos desde `data/*.json` (excluye analytics.json, bodegas.json).
- **Búsqueda unificada** en `services/busqueda_service.py`: `buscar_vinos_avanzado(vinos_dict, texto, limite)`. Usada por escaneo, `app.py` (`/buscar`, `/analyze/text`).
- Endpoints: `/`, `/escanear`, `/registrar`, `/preguntar`, `/bodega`, `/dashboard`, `/adaptador`, `/planes`, `/pago-exitoso`, `/pago-cancelado`, `/vino/{id}/comprar`.

### 2. Escaneo
- **POST /escanear**: imagen, texto y/o código de barras. OCR, búsqueda en BD y en API externa (Open Food Facts). Guarda consultas como `{ "vino", "key" }` en `app.state.consultas_escaneo`.
- **GET /historial-escaneos**: historial por sesión (header `X-Session-ID`).
- **POST /registrar-vino**: registro de vino con validación y límite diario.
- Respuesta de escaneo incluye `vino_key`, `mostrar_boton_comprar`; en el front hay botón “Comprar este vino” a `/vino/{vino_key}/comprar`.

### 3. Sumiller (preguntar)
- **GET /preguntar-sumiller**: por `consulta_id` o `vino_key` responde sobre un vino; sin ellos, maridajes/recomendaciones con contexto (últimas 3 preguntas por sesión).
- **POST /api/preguntar-local**: delega en agente local (puerto 8080) con fallback a lógica rule-based.
- **GET /api/vino-por-consulta**: devuelve el vino para un `consulta_id` (formato desempaquetado `{ "vino", "key" }`).
- Respuesta incluye `imagen_url`, `vino_key`, `mostrar_boton_comprar`. Imágenes en `static/images/vinos/` (tipo: tinto, blanco, rosado, espumoso, generico; opcional `{vino_key}.jpg`). Servicio: `services/imagen_service.py`.
- **Recomendaciones reales:** `sumiller_service.buscar_vinos_por_preferencia` (tipo, país, precio); respuestas con nombre, región, descripción breve y precio. Detección ampliada: "recomendación", "mejor", "qué tinto", "vino argentino", etc.
- **Sin resultados:** `fallback_sin_resultados()` usa `data/conocimiento_vinos.json` (Lambrusco, Malbec, Rioja, Champagne, etc.: origen, ejemplos famosos, maridaje) y ofrece hasta 3 vinos similares de la BD. No se muestran mensajes genéricos tipo "Puede preguntarme por...".
- **Vino concreto por nombre:** "Háblame del Marqués de Riscal" → búsqueda por nombre; si no está, fallback con info + alternativas.

### 4. Bodega (Mi Bodega)
- API bajo **/api/bodega**: GET (lista), POST botellas, PUT/DELETE botellas, GET registros-hoy, valoración, alertas, stock. Requiere `X-Session-ID` (o `X-API-Token` para stock).
- Validación anti-tonterías (`services/validacion_service.py`) y límite diario (`services/limite_diario_service.py`). Niveles: nuevo, normal, verificado, PRO (sin límite). Datos en `data/registros_diarios.json`, `data/usuarios_reputacion.json`.
- Freemium: límite 50 vinos plan Gratis; PRO ilimitado. `data/usuarios_pro.json` se actualiza vía webhook de Stripe.

### 5. Pagos (Stripe)
- **POST /crear-checkout-session**: header `X-Session-ID` obligatorio; crea sesión Stripe 4,99 €/mes; devuelve `{ "url": "..." }`.
- **GET /pago-exitoso**, **GET /pago-cancelado**: páginas de éxito/cancelación (heredan `base.html`).
- **POST /webhook-stripe**: recibe eventos de Stripe; en `checkout.session.completed` marca usuario PRO con `freemium_service.add_pro_user(session_id)` (usa `client_reference_id`).
- Configuración: `.env` con `STRIPE_SECRET_KEY` y `STRIPE_WEBHOOK_SECRET`. `.env.example` y `.gitignore` ya configurados.

### 6. Planes y precio PRO
- Precio PRO alineado a **4,99 €/mes** en todas las traducciones (`planes.precio_pro`) y en Stripe.
- En `templates/planes.html` el botón “Actualizar a PRO” hace POST a `/crear-checkout-session` con `X-Session-ID` (desde `localStorage.vino_pro_session_id`) y redirige a la URL de Stripe.

### 7. Comprar (enlaces por vino)
- **GET /vino/{vino_id}/comprar**: página con pestañas (nacional, internacional, subastas). Usa `services/enlaces_service.py`. Plantilla `comprar_vino.html` hereda `base.html` y usa `t()`.

### 8. Adaptador restaurantes
- **GET /api/adaptador/token**: obtiene o crea token para el restaurante.
- **POST /api/adaptador/config**: actualiza nombre, programas, webhook_url (query `token`).
- Página `/adaptador` con token, copiar y formulario de configuración.

### 9. Analytics e informes
- **GET /analytics/dashboard?dias=30**: totales (búsquedas, escaneos, preguntas), tendencias, por país, preguntas frecuentes. Datos en `data/analytics.json`.
- **GET /informes/bodega**, **POST /informes/cata**: PDFs (session id / body con vino).

### 10. i18n y plantillas
- **Idiomas:** es, en, pt, fr, de, it. Cookie `vino_pro_lang`, `services/i18n.py`, `data/translations/*.json`.
- **Todas las páginas** usan `base.html`: menú común, selector de idioma, botón modo oscuro. `app.py` usa `render_page(request, "*.html", page_class="page-*", active_page="...")`.
- **Plantillas migradas a base.html:** index, planes, pago-exitoso, pago-cancelado, comprar_vino, preguntar, escanear, registrar, bodega, dashboard, adaptador.
- **JS externo** en `static/js/`: preguntar.js, escanear.js, registrar.js, bodega.js, dashboard.js, adaptador.js. Donde hace falta, la plantilla inyecta `window.ERROR_MSGS` y `window.INFO_REGISTROS_HOY` desde `t()` antes de cargar el .js.
- **Estilos unificados (modo claro):** En `static/style.css`, clases `.page-title`, `.page-subtitle`, `.section-title`, `.stat-number`; Dashboard/Bodega/Adaptador con texto legible en modo claro (`html:not([data-theme="dark"])`) y overlay; sin mensajes de ayuda genéricos en el sumiller.
- **Imágenes de fondo por página:** Planes: `vino-pro-ia-fondo-planes-claro.jpg` / `-oscuro.jpg`. Adaptador: `vino-pro-ia-fondo-adaptador-claro.jpg` / `-oscuro.jpg`. Documentadas en `static/images/README-FONDOS.md`.

### 11. Session ID y app.js
- `static/app.js` define `window.getSessionId()`. Clave en `localStorage`: `vino_pro_session_id`. Se usa en bodega, escaneo, preguntar, registrar, planes (checkout).

### 12. Limpieza y análisis
- Backups de plantillas antiguas movidos a `backups/` (index_before_fix.html, index_backup_final.html, index_backup.html).
- **ANALISIS_APP.md** describe estado de rutas, posibles mejoras y un bug ya corregido en `/api/vino-por-consulta`.

---

## Estructura de carpetas relevante

```
backend_optimized/
├── app.py                 # FastAPI, render_page, rutas /, /escanear, etc., include_router de todos
├── data/
│   ├── translations/      # es, en, pt, fr, de, it .json
│   ├── conocimiento_vinos.json  # Tipos (Lambrusco, Malbec, Rioja, etc.): origen, ejemplos, maridaje; fallback sumiller
│   ├── usuarios_pro.json   # IDs de sesión PRO (Stripe webhook)
│   ├── registros_diarios.json, usuarios_reputacion.json
│   ├── analytics.json
│   └── *.json             # vinos (se cargan todos salvo analytics, bodegas)
├── routes/
│   ├── escaneo.py         # /escanear, /registrar-vino, /historial-escaneos
│   ├── sumiller.py        # /preguntar-sumiller
│   ├── bodega.py          # bajo /api: bodega, botellas, registros-hoy, valoracion, alertas, stock
│   ├── planes.py          # /planes, /api/check-limit
│   ├── pagos.py           # /crear-checkout-session, /pago-exitoso, /pago-cancelado, /webhook-stripe
│   ├── comprar.py         # /vino/{id}/comprar, /api/vino/{id}/enlaces
│   ├── adaptador.py       # prefix /adaptador -> /api/adaptador/token, /api/adaptador/config
│   ├── analytics.py       # /analytics/dashboard, tendencias, por-pais, preguntas-frecuentes
│   └── informes.py        # /informes/bodega, /informes/cata
├── services/
│   ├── busqueda_service.py   # buscar_vinos_avanzado (única fuente de búsqueda)
│   ├── imagen_service.py     # get_imagen_vino(vino_key, tipo)
│   ├── validacion_service.py # validar nombre, añada, alcohol, vino completo
│   ├── limite_diario_service.py
│   ├── freemium_service.py   # usuarios PRO, puede_anadir_botella
│   ├── stripe_service.py     # crear_checkout_session, procesar_webhook
│   ├── i18n.py
│   ├── enlaces_service.py, adaptador_service.py, analytics_service.py, ocr_service.py, api_externa_service.py, sumiller_service.py, bodega_service.py
├── templates/             # Todas extienden base.html
│   ├── base.html
│   ├── index.html, planes.html, pago-exitoso.html, pago-cancelado.html, comprar_vino.html
│   ├── preguntar.html, escanear.html, registrar.html, bodega.html, dashboard.html, adaptador.html
├── agente_local/
│   └── server.py          # Sumiller en 8080; OpenRouter (opcional); GET /test-openrouter para diagnosticar; fallback rule-based sin 500
├── static/
│   ├── style.css, app.js
│   ├── js/                # preguntar.js, escanear.js, registrar.js, bodega.js, dashboard.js, adaptador.js
│   └── images/            # Fondos: vino-pro-ia-fondo-planes-claro|oscuro.jpg, -adaptador-claro|oscuro.jpg; README-FONDOS.md
│       └── vinos/     # tinto.jpg, blanco.jpg, rosado.jpg, espumoso.jpg, generico.jpg (opcional por vino_key)
├── backups/               # Copias antiguas de plantillas
├── .env.example, .gitignore
├── ANALISIS_APP.md
└── RESUMEN_PARA_NUEVA_CONVERSACION.md  # Este archivo
```

---

## Cómo seguir una nueva conversación

1. **Contexto:** “Estoy con VINO PRO IA (FastAPI, puerto 8001). Tengo un resumen en `RESUMEN_PARA_NUEVA_CONVERSACION.md`.”
2. **Objetivo:** Indicar qué quieres hacer (ej.: “añadir X”, “corregir Y en la bodega”, “cambiar textos de Stripe”).
3. Opcional: “Lee `RESUMEN_PARA_NUEVA_CONVERSACION.md` para ver el estado actual.”

---

## Pendientes / opcionales (por si acaso)

- Añadir imágenes reales en `static/images/vinos/` (tinto, blanco, rosado, espumoso, generico) si aún no están.
- Probar Stripe en vivo (webhook con Stripe CLI o en producción).
- Agente local (8080): opcional; con `OPENROUTER_API_KEY` en `.env` usa IA; sin clave o si OpenRouter falla, respuestas rule-based (nunca 500). Probar conexión: `GET http://127.0.0.1:8080/test-openrouter`.

---

¡Listo, compi! Con este resumen cualquier conversación nueva puede continuar desde el mismo punto.
