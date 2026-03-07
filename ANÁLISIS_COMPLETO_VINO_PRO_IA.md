# ANÁLISIS COMPLETO VINO PRO IA - 2026-02-21

## 📁 ESTRUCTURA DE ARCHIVOS

```
backend_optimized/
├── app.py                    # FastAPI, carga vinos, render_page, rutas /api/preguntar-local, /api/vino-por-consulta
├── main.py                   # Punto de entrada alternativo
├── requirements.txt
├── .env.example              # Stripe, OpenRouter (API_KEY, URL, MODEL)
├── .gitignore
│
├── data/
│   ├── translations/         # es, en, pt, fr, de, it (i18n)
│   ├── conocimiento_vinos.json   # Tipos: Lambrusco, Malbec, Rioja, Champagne, etc. (fallback experto en vinos)
│   ├── usuarios_pro.json     # IDs PRO (Stripe webhook) — NO se carga en vinos_mundiales
│   ├── registros_diarios.json
│   ├── usuarios_reputacion.json
│   ├── analytics.json
│   ├── bodegas.json
│   ├── enlaces_compra.json
│   ├── restaurantes.json
│   ├── registrados.json      # Vinos registrados por usuarios
│   └── *.json                # Catálogo: argentina, espana, chile, francia, italia, etc.
│
├── routes/
│   ├── escaneo.py            # /escanear, /registrar-vino, /historial-escaneos
│   ├── sumiller.py           # GET /preguntar-sumiller (lógica maridaje, recomendación, fallback)
│   ├── bodega.py             # /api/bodega, botellas, registros-hoy, valoración, alertas, stock
│   ├── planes.py             # /planes, /api/check-limit
│   ├── pagos.py              # /crear-checkout-session, /pago-exitoso, /pago-cancelado, /webhook-stripe
│   ├── comprar.py            # /vino/{id}/comprar, /api/vino/{id}/enlaces
│   ├── adaptador.py          # /api/adaptador/token, /api/adaptador/config
│   ├── analytics.py          # /analytics/dashboard, tendencias, por-pais, preguntas-frecuentes
│   └── informes.py           # /informes/bodega, /informes/cata (PDFs)
│
├── services/
│   ├── busqueda_service.py   # buscar_vinos_avanzado (única fuente de búsqueda)
│   ├── sumiller_service.py   # maridaje, preferencias, fallback_sin_resultados (conocimiento_vinos)
│   ├── imagen_service.py
│   ├── validacion_service.py
│   ├── limite_diario_service.py
│   ├── freemium_service.py
│   ├── stripe_service.py
│   ├── i18n.py
│   ├── enlaces_service.py, adaptador_service.py, analytics_service.py
│   ├── ocr_service.py, api_externa_service.py, bodega_service.py
│   └── __init__.py
│
├── agente_local/
│   ├── server.py             # Puerto 8080, POST /skill/sumiller, GET /test-openrouter, OpenRouter + fallback
│   └── __init__.py
│
├── templates/                # Todas extienden base.html
│   ├── base.html
│   ├── index.html, planes.html, pago-exitoso.html, pago-cancelado.html, comprar_vino.html
│   ├── preguntar.html, escanear.html, registrar.html, bodega.html, dashboard.html, adaptador.html
│
├── static/
│   ├── style.css, app.js
│   ├── js/                   # preguntar.js, escanear.js, registrar.js, bodega.js, dashboard.js, adaptador.js
│   └── images/                # Fondos por página, vinos/ (tinto, blanco, rosado, espumoso, generico)
│
├── models/
│   ├── enlaces_compra.py
│   └── __init__.py
│
├── RESUMEN_PARA_NUEVA_CONVERSACION.md
├── ANALISIS_APP.md
├── README_AGENTE_LOCAL.md
├── INSTRUCCIONES_AGENTE_LOCAL.txt
├── ESTADO_VINO_PRO_IA_2026-02-19.md
└── ANÁLISIS_COMPLETO_VINO_PRO_IA.md   # Este archivo
```

---

## ✅ FUNCIONALIDADES CORRECTAS

- **Escaneo de etiquetas**: POST /escanear (imagen, texto, código de barras), OCR, búsqueda BD + Open Food Facts, historial por sesión.
- **Registro de vinos**: POST /registrar-vino con validación anti-tonterías y límite diario por nivel (nuevo, normal, verificado, PRO).
- **Mi Bodega**: CRUD bajo /api/bodega (lista, botellas, registros-hoy, valoración, alertas, stock), límite 50 vinos plan Gratis, PRO ilimitado.
- **Dashboard**: GET /analytics/dashboard con totales, tendencias, por país, preguntas frecuentes (data/analytics.json).
- **Enlaces de compra**: GET /vino/{id}/comprar con pestañas nacional, internacional, subastas (enlaces_service).
- **Adaptador restaurantes**: GET /api/adaptador/token, POST /api/adaptador/config, página /adaptador con token y formulario.
- **6 idiomas**: es, en, pt, fr, de, it (cookie vino_pro_lang, data/translations/*.json, services/i18n.py).
- **Imágenes por género**: static/images/vinos/ (tinto, blanco, rosado, espumoso, generico) + fondos por página (planes, adaptador).
- **Pagos Stripe**: POST /crear-checkout-session (4,99 €/mes), /pago-exitoso, /pago-cancelado, webhook-stripe; configuración en .env.
- **Búsqueda unificada**: services/busqueda_service.buscar_vinos_avanzado usada por escaneo, /buscar, /analyze/text.
- **Informes**: GET /informes/bodega, POST /informes/cata (PDFs).

---

## ❌ ERRORES DETECTADOS Y SOLUCIONES APLICADAS

### Error 1: AttributeError: 'list' object has no attribute 'get' (sumiller_service)

- **Archivo:** `services/sumiller_service.py` (línea ~275 en `_buscar_similares_por_tipo_o_pais` y otras).
- **Causa:** `cargar_todos_los_vinos()` en app.py cargaba **todos** los JSON de `data/`, incluidos `usuarios_pro.json` (contiene `"pro_users": []`), `conocimiento_vinos.json`, `enlaces_compra.json`, `restaurantes.json`, etc. Al iterar `vinos_dict.items()`, algún valor era una lista y al llamar `vino.get("tipo")` se producía el error.
- **Solución aplicada:**
  1. En **app.py**: ampliada la lista `excluir` para no cargar como vinos: `analytics.json`, `bodegas.json`, `conocimiento_vinos.json`, `enlaces_compra.json`, `restaurantes.json`, `registros_diarios.json`, `usuarios_reputacion.json`, `usuarios_pro.json`.
  2. En **services/sumiller_service.py**: comprobaciones defensivas `isinstance(vino, dict)` en todos los bucles que iteran `vinos_dict` (`_buscar_similares_por_tipo_o_pais`, `buscar_vinos_por_maridaje`, `buscar_vinos_por_preferencia`, `fallback_sin_resultados`, `resolver_contexto_esos`). Solo se procesan entradas cuyo valor es un dict.

### Error 2: Pregunta "que lambrusco es la mas famosa" → Error 500 / "Respuesta inválida del servidor"

- **Causa:** El Error 1 provocaba 500 al usar el experto en vinos; además, el frontend podía mostrar "Respuesta inválida del servidor" si el backend devolvía HTML o cuerpo no-JSON en errores.
- **Solución:** Corregido con las mismas medidas del Error 1. Además (en sesión anterior): sin Consulta ID en modo Local se usa GET /preguntar-sumiller (nube), que aplica `_es_pregunta_tipo_famoso` y `fallback_sin_resultados` con `conocimiento_vinos.json` (Lambrusco, ejemplos famosos, maridaje + hasta 3 alternativas de la BD). El frontend usa `.catch()` en `r.json()` para no romper si la respuesta no es JSON.

### Error 3: Modo local sin escaneo no respondía correctamente

- **Archivo:** `static/js/preguntar.js`.
- **Causa:** Si el usuario elegía "IA Local" y no rellenaba Consulta ID, se mostraba "En modo IA Local indica un Consulta ID" y no se enviaba la pregunta.
- **Solución (ya aplicada):** Si está en modo Local pero **no** hay Consulta ID, el frontend llama a **GET /preguntar-sumiller** (misma ruta que Nube). Solo si hay Consulta ID se llama a POST /api/preguntar-local. Así preguntas como "que lambrusco es la mas famosa" se responden con conocimiento + BD sin exigir escaneo.

### Error 4: Modo nube / OpenRouter → error de conexión o JSON inválido

- **Archivo:** `agente_local/server.py`.
- **Causa:** Si OpenRouter devolvía 5xx con cuerpo "Internal Server Error" (texto), se intentaba parsear como JSON y se propagaba el error.
- **Solución (ya aplicada):** Solo se parsea JSON cuando `status_code == 200`. En 4xx/5xx, timeout o error de conexión se usa fallback local y se devuelve siempre 200 con JSON. Logs: "OpenRouter: status code X", "OpenRouter: timeout", "OpenRouter: usando fallback local". El usuario nunca ve el error técnico.

---

## 🔧 PENDIENTES CONOCIDOS

- **Stripe en producción:** Cambiar a claves live y configurar webhook en producción.
- **Ampliar base de datos:** Más vinos en data/*.json o integración con fuentes externas.
- **App nativa:** No iniciada; el backend está pensado para web.
- **Imágenes reales:** Completar static/images/vinos/ (tinto, blanco, rosado, espumoso, generico) si faltan.
- **Probar agente 8080:** GET http://127.0.0.1:8080/test-openrouter para validar OPENROUTER_API_KEY y modelo.

---

## 🎯 PRIORIDADES RECOMENDADAS

1. **Verificar experto en vinos tras los cambios:** Probar "que lambrusco es la mas famosa" en modo Nube y en modo Local (sin Consulta ID). Debe devolver texto de conocimiento + alternativas, sin 500 ni "Respuesta inválida del servidor".
2. **Probar OpenRouter:** Tener `.env` con `OPENROUTER_API_KEY`, `OPENROUTER_URL` y `OPENROUTER_MODEL`; levantar agente 8080 y llamar a `/test-openrouter`. Si falla, el experto en vinos local seguirá usando fallback sin romper.
3. **Stripe en producción:** Cuando se pase a producción, sustituir claves test por live y configurar el webhook de Stripe.
4. **Revisar otros consumidores de `vinos_mundiales`:** Asegurarse de que busqueda_service y demás asumen solo claves de vino (ahora que se excluyen los JSON no-vino, no debería haber sorpresas).

---

## 📊 NOTAS ADICIONALES

- **conocimiento_vinos.json** no se carga en `vinos_mundiales`; se usa solo en `services/sumiller_service.fallback_sin_resultados()` (ruta desde el propio servicio).
- **registrados.json** sí se carga como catálogo (formato key → vino dict).
- Tras excluir los JSON no-vino, el número de vinos cargados en arranque será menor; los archivos de país + registrados siguen siendo la fuente del catálogo.
