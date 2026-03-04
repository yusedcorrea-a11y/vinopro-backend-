# 📊 ESTADO ACTUAL VINO PRO IA (19/02/2026)

## 📁 ESTRUCTURA DEL PROYECTO

```
backend_optimized/
├── app.py
├── main.py
├── requirements.txt
├── routes/
│   ├── __init__.py
│   ├── bodega.py
│   ├── comprar.py
│   ├── adaptador.py
│   ├── escaneo.py
│   ├── sumiller.py
│   ├── analytics.py
│   └── informes.py
├── models/
│   ├── __init__.py
│   └── enlaces_compra.py
├── services/
│   ├── __init__.py
│   ├── enlaces_service.py
│   ├── bodega_service.py
│   ├── adaptador_service.py
│   ├── busqueda_service.py
│   ├── sumiller_service.py
│   ├── ocr_service.py
│   ├── api_externa_service.py
│   ├── analytics_service.py
│   └── i18n.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── escanear.html
│   ├── registrar.html
│   ├── preguntar.html
│   ├── bodega.html
│   ├── dashboard.html
│   ├── adaptador.html
│   └── comprar_vino.html
├── static/
│   ├── style.css
│   └── app.js
├── data/
│   ├── vinos por país: espana.json, argentina.json, francia.json, italia.json, etc.
│   ├── registrados.json
│   ├── enlaces_compra.json
│   ├── analytics.json
│   ├── bodegas.json
│   ├── translations/
│   │   ├── es.json
│   │   └── en.json
│   └── (restaurantes.json se crea al usar el adaptador)
└── agente_local/
    ├── server.py
    └── INSTRUCCIONES_AGENTE_LOCAL.txt
```

## ✅ COMPLETADO (100%)

- **Escaneo de etiquetas**: imagen (OCR), texto manual y código de barras; búsqueda en BD + Open Food Facts; historial por sesión (X-Session-ID).
- **Registro de vinos**: POST `/registrar-vino` guarda en `data/registrados.json` y se integra en la búsqueda.
- **Búsqueda avanzada**: por nombre, bodega y región con fuzzy matching (app y `busqueda_service`).
- **Mi Bodega Virtual**: CRUD de botellas, alertas temp/humedad, valoración, potencial de guarda; header X-Session-ID; persistencia en `bodegas.json`.
- **Sumiller virtual**: preguntas sobre vino concreto (consulta_id/vino_key), maridaje y recomendaciones; contexto “de esos” (últimas 3); perfiles principiante/aficionado/profesional; integración agente local (puerto 8080) con fallback rule-based.
- **Enlaces de compra**: página `/vino/{vino_id}/comprar` con 3 pestañas (Nacional, Internacional, Subastas); detección de país por IP; API `/api/vino/{vino_id}/enlaces`; datos en `enlaces_compra.json`.
- **Adaptador restaurantes**: token API, configuración (nombre, programas, webhook); GET `/api/bodega/stock` con X-Session-ID o X-API-Token; webhook al actualizar bodega; `restaurantes.json` se crea bajo demanda.
- **Analytics**: dashboard, tendencias, por país, preguntas frecuentes; persistencia en `analytics.json` (límite 5000 eventos por tipo).
- **Informes PDF**: informe de cata y informe de bodega (reportlab); GET `/informes/bodega` (X-Session-ID), POST `/informes/cata`.
- **i18n (ES/EN)**: cookie `vino_pro_lang`, `services/i18n.py`, `data/translations/es.json` y `en.json`; selector en `base.html`; `render_page()` inyecta `t`, `lang`, `recognition_lang` en todas las páginas que usan base.
- **Páginas HTML**: Inicio, Escanear, Registrar, Preguntar, Mi Bodega, Dashboard, Adaptador; todas con navegación y tema claro/oscuro.

## 🚧 EN PROGRESO (parcialmente implementado)

- **Página “Comprar vino”**: No usa `render_page()` ni `base.html`; texto fijo en español (sin traducciones ni selector de idioma). La lógica de enlaces y pestañas está completa.
- **Traducciones**: Algunos templates pueden tener cadenas hardcodeadas además de `t('...')`; comprobar cobertura en todas las vistas.

## ❌ PENDIENTE (0% implementado)

- **Modelo freemium (límite 50 vinos en bodega)**: No existe límite por sesión ni por usuario; la bodega crece sin tope. El único “50” en el código es el historial de escaneos por sesión (`hist[session_id][-50:]`).
- **Sistema multilingüe ampliado**: Solo ES y EN; no hay más idiomas ni detección automática de idioma del navegador (solo cookie).
- **Ruta dedicada “preguntar”**: No hay `routes/preguntar.py`; la UI es `preguntar.html` y la lógica está en `routes/sumiller.py` y en `app.py` (`/api/preguntar-local`). Funcional, pero la organización podría documentarse como “preguntar = sumiller”.

## 🐛 POSIBLES MEJORAS O BUGS DETECTADOS

- **comprar_vino.html**: Debería usar `render_page()` y extender `base.html` para tener i18n y navegación consistente (incl. selector de idioma).
- **restaurantes.json**: No existe hasta que se usa el adaptador; el servicio lo crea correctamente; conviene documentarlo para despliegue.
- **Dependencia de reportlab**: Informes PDF devuelven 503 si reportlab no está instalado; está en `requirements.txt`; asegurar instalación en entornos de producción.
- **Agente local**: `/api/preguntar-local` y sumiller asumen agente en `http://127.0.0.1:8080`; si no está levantado, se usa fallback; no hay health check desde el backend hacia el agente en la UI.
- **Bodega sin límite**: Si se quiere freemium, hay que añadir comprobación de número de botellas (o entradas) por sesión antes de `add_botella`.

## 📊 MÉTRICAS

- **Número total de vinos en base de datos**: 564 (sumando todos los JSON de `data/` excepto analytics, bodegas; incluye por país y registrados).
- **Número de rutas/endpoints**: ~35 (app: 15, bodega: 6, escaneo: 3, sumiller: 1, analytics: 4, adaptador: 2, comprar: 2, informes: 2).
- **Número de templates HTML**: 9 páginas principales (base, index, escanear, registrar, preguntar, bodega, dashboard, adaptador, comprar_vino) + 3 backups (index_*).
- **Idiomas soportados**: ES (por defecto) y EN vía cookie y archivos en `data/translations/`.

## 🎯 PRÓXIMO PASO RECOMENDADO

1. **Unificar “Comprar vino” con el resto de la app**: Hacer que la ruta de comprar use `render_page()` y que `comprar_vino.html` extienda `base.html` y use `t()` para todos los textos, para que tenga idioma y navegación coherentes.
2. **Si se quiere freemium**: Implementar en `bodega_service.add_botella()` (o en la ruta POST) un límite de 50 botellas (o 50 líneas) por `session_id`, devolviendo un error claro cuando se supere.
3. **Opcional**: Añadir detección de idioma del navegador en la primera visita (sin cookie) y documentar que “preguntar” = sumiller para quien mantenga el código.
