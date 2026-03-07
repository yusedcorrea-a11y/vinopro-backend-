# ANÁLISIS TÉCNICO COMPLETO — VINO PRO IA (Backend)

**Fecha:** 2 de marzo de 2026  
**Ámbito:** backend_optimized (API, servicios, datos, seguridad, despliegue)

---

## 1. RESUMEN EJECUTIVO

**VINO PRO IA** es un backend en **Python** basado en **FastAPI** que sirve una aplicación web de vinos: escaneo de etiquetas (OCR), experto en vinos virtual (rule-based + opcional IA local), Mi Bodega virtual, planes freemium/PRO, pagos con Stripe, comunidad (perfiles, feed, seguimiento), ofertas entre usuarios, geolocalización, QR personalizados y múltiples idiomas (i18n). Los datos se persisten en **archivos JSON** en la carpeta `data/`; no hay base de datos relacional. La versión declarada del API es **5.0**.

---

## 2. STACK TECNOLÓGICO

| Componente | Tecnología |
|------------|------------|
| Framework | FastAPI 0.104.1 |
| Servidor ASGI | Uvicorn 0.24.0 |
| Plantillas | Jinja2 (FastAPI Templating) |
| HTTP cliente | requests 2.31.0, httpx ≥0.25.0 (async) |
| Pagos | Stripe 7.0.0 |
| OCR | pytesseract 0.3.10 + Pillow 10+ (Tesseract en sistema) |
| Imágenes/QR | Pillow, qrcode[pil] 7.4+, reportlab 4.0+ |
| Configuración | python-dotenv 1.0+ |
| Tests | pytest 7.0+ |
| Validación/serialización | Pydantic (incluido en FastAPI) |

**Entorno:** Python 3.x (tipado con `str | None`, etc., compatible 3.10+). Variables de entorno: `HOST`, `PORT`, `CORS_ORIGINS`, `BASE_URL`, `DATA_FOLDER`, Stripe (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`), OpenRouter (IA local), QR (email, LinkedIn, WhatsApp, Calendly, webhook).

---

## 3. ARQUITECTURA

- **Entrada única:** `app.py` crea la instancia FastAPI, monta estáticos (`/static`), define directorio de plantillas y registra todos los routers.
- **Estado en memoria:** `app.state.vinos_mundiales` (catálogo cargado al arranque), `app.state.consultas_escaneo` (consulta_id → { vino, key }), `app.state.historial_escaneos` y `app.state.historial_sumiller` por sesión.
- **Persistencia:** Carpeta `data/`: JSON para vinos (por país/región), `registrados.json`, `bodegas.json`, `usuarios_pro.json`, `analytics.json`, `valoraciones.json`, `wishlist.json`, perfiles, seguidores, actividad, notificaciones, ofertas, contactos QR, notificaciones landing, etc.
- **Rutas:** Organizadas por dominio en `routes/` (escaneo, experto en vinos, bodega, planes, pagos, ofertas, comunidad, geolocalización, analytics, informes, adaptador, comprar, valoraciones_wishlist, qr_personalizado). Bodega, ofertas y geolocalización usan prefijo `/api` al incluir el router.
- **Servicios:** Lógica de negocio en `services/` (busqueda, ocr, api_externa, bodega, freemium, stripe, experto en vinos, recomendaciones, validación, límite diario, usuario, seguidores, feed, notificaciones, valoraciones, wishlist, ofertas, imagen, i18n, geolocalización, etc.).
- **Modelos:** `models/` con dataclasses (comunidad: PerfilUsuario, ValoracionPublica, etc.), y esquemas Pydantic en las propias rutas (BotellaCreate, VinoRegistro, etc.).

---

## 4. CATÁLOGO DE VINOS Y BÚSQUEDA

- **Carga:** Al inicio, `cargar_todos_los_vinos()` lee todos los `.json` de `data/` excepto los de configuración/estado (analytics, bodegas, usuarios_pro, ofertas, valoraciones, wishlist, etc.) y los fusiona en un único diccionario `VINOS_MUNDIALES` (key → objeto vino).
- **Búsqueda unificada:** `services/busqueda_service.py`: `buscar_vinos_avanzado(vinos_dict, texto, limite)` con normalización, stop words, pesos por campo (nombre, bodega, región, uva), fuzzy matching (difflib), filtros por región prioritaria (Ribera, Rioja), tipo (tinto/blanco/rosado/espumoso) y precio máximo extraído del texto. También `buscar_vinos_con_sugerencia()` para “quizás quisiste decir”.
- **Escaneo:** Si no hay coincidencia en BD, se consulta Open Food Facts (texto o código de barras) y, si hay resultado, se persiste en `registrados.json` y se añade al dict en memoria para futuras búsquedas.

---

## 5. IDENTIFICACIÓN Y SESIÓN

- **Sin login tradicional:** No hay usuarios con email/contraseña. La identificación es por **X-Session-ID** (header), generado en el front (por ejemplo UUID en `localStorage` como `vino_pro_session_id`).
- **Uso:** Bodega, escaneo (historial), experto en vinos (contexto), planes, pagos, comunidad, ofertas, valoraciones, wishlist y límite diario se apoyan en este session_id.
- **PRO:** Lista en `data/usuarios_pro.json` (`pro_users`: array de session_id). Stripe webhook, al completar checkout, añade el `client_reference_id` (session_id) a esa lista.

---

## 6. FUNCIONALIDADES PRINCIPALES

### 6.1 Escaneo de etiquetas
- **POST /escanear:** Acepta multipart (texto, imagen, codigo_barras) o JSON (texto, codigo_barras). Con imagen se usa OCR (Tesseract); el texto resultante se combina con el enviado para buscar. Si hay coincidencia en BD se devuelve vino + consulta_id; si no, se intenta Open Food Facts; si tampoco, se devuelve vino genérico. Cada resultado se guarda en `consultas_escaneo` y opcionalmente en historial por session_id. Límite diario y validación anti-abuso en registro.
- **POST /registrar-vino:** Alta de vino en `registrados.json` con validación (validacion_service) y límite diario (limite_diario_service); requiere X-Session-ID para límite.
- **GET /historial-escaneos:** Historial de escaneos del usuario (X-Session-ID), último N.

### 6.2 Experto en Vinos virtual
- **GET /preguntar-sumiller:** Con `consulta_id` o `vino_key` responde sobre ese vino (rule-based: maridaje, descripción, notas, bodega, región, tipo, precio, puntuación) con perfil principiante/aficionado/profesional. Sin vino: maridajes, recomendaciones, “de esos cuál…”, navegación (mapa, bodega, planes, adaptador, menú, idioma). Mantiene contexto de últimas 3 preguntas por session_id para “de esos”.
- **POST /api/preguntar-local:** Solo PRO. Llama al agente local (http://127.0.0.1:8080/skill/sumiller); si falla, fallback a la misma lógica rule-based.
- **POST /api/feedback-vino:** Registra like/dislike para recomendaciones personalizadas.

### 6.3 Mi Bodega
- **API bajo /api** (router con prefix /api): GET/POST/PUT/DELETE botellas, GET alertas (temperatura/humedad), GET valoración, GET registros-hoy (límite diario), GET stock (también por X-API-Token para restaurantes). Validación de nombre y límite freemium (50 botellas gratis; PRO ilimitado). Adaptador puede notificar webhook y exponer stock para terceros.

### 6.4 Planes y pagos
- **GET /planes:** Página de planes (Gratis, PRO, Restaurante).
- **GET /api/check-limit:** Estado freemium (puede_anadir, es_pro, usado, limite, mensaje).
- **POST /crear-checkout-session:** Crea sesión Stripe (4,99 €/mes), success/cancel URLs, client_reference_id = session_id.
- **GET /pago-exitoso, GET /pago-cancelado:** Páginas post-pago.
- **POST /webhook-stripe:** Recibe eventos Stripe; en checkout.session.completed añade session_id a usuarios_pro.

### 6.5 Ofertas (Premium)
- Crear oferta (foto + email), listar por vino_key, contactar (solicitud de contacto), mis ofertas, marcar respondido, retirar oferta. Fotos en `data/uploads/ofertas/`, servidas por GET /api/uploads/ofertas/{filename}.

### 6.6 Comunidad (Fase 6B)
- Perfiles: crear (username único 3–30 caracteres), mi-perfil, actualizar, perfil público por username.
- Seguir/dejar de seguir, listar seguidores/seguidos.
- Feed de actividad de los que sigo; valoraciones y actividad por perfil.
- Notificaciones (nuevo seguidor, etc.) y marcar leídas.

### 6.7 Valoraciones y wishlist
- Valorar vino, listar valoraciones por vino, editar/borrar valoración; wishlist add/remove/contains/list. Integrado con perfiles para valoraciones públicas.

### 6.8 Comprar y enlaces
- Página /vino/{vino_id}/comprar y API de enlaces de compra por vino_id.

### 6.9 Geolocalización
- GET /api/lugares-cerca (lat/lon o ciudad, radio km, tipo); GET /api/geocode (ciudad → lat, lon). Servicio con datos estáticos o integración externa según implementación.

### 6.10 Analytics e informes
- Dashboard, tendencias, por-pais, preguntas frecuentes; informes bodega y cata (con X-Session-ID).

### 6.11 Adaptador restaurantes
- GET /adaptador/token, POST /adaptador/config; tokens para acceso por X-API-Token al stock.

### 6.12 QR personalizados
- Página por código /c/{codigo}, generador /qr, API contactos, generar, descargar. Datos de contacto configurables por env (email, LinkedIn, WhatsApp, Calendly, webhook).

### 6.13 Landing y notificaciones
- POST /api/landing-notify: registro de email para aviso Google Play; guardado en data/notificaciones_landing.json.

---

## 7. INTERNACIONALIZACIÓN (i18n)

- **14 idiomas:** es, en, pt, fr, de, it, ar, ru, tr, zh, ja, ko, hi, he. Cookie `vino_pro_lang` (1 año). Traducciones en `data/translations/{lang}.json` con estructura anidada; función `t("key.subkey")` en plantillas. Reconocimiento de voz: código por idioma (ej. es-ES, en-US) para Web Speech API.

---

## 8. SEGURIDAD

- **CORS:** Configurable por `CORS_ORIGINS` (producción: dominios concretos, no `*`).
- **Stripe:** Firma del webhook con STRIPE_WEBHOOK_SECRET; rechazo si falla verificación.
- **Session ID:** No es secreto; quien conozca un session_id puede actuar como ese “usuario”. No hay autenticación fuerte.
- **Subida de archivos:** Ofertas: extensión permitida (jpg, jpeg, png, webp), tamaño máx 6 MB; servir fotos con nombre seguro (sin `..` ni path).
- **Validación:** validacion_service y limite_diario_service para evitar spam en registros y bodega.
- **Datos sensibles:** Claves Stripe y OpenRouter solo por entorno; .env no versionado ( .env.example como plantilla).

---

## 9. DESPLIEGUE Y OPERACIÓN

- **Puerto:** Por defecto 8001 (PORT); HOST por defecto 127.0.0.1 (producción 0.0.0.0).
- **Health:** GET /health (siempre 200 si proceso vivo), GET /ready (incluye comprobación de vinos cargados).
- **Sitemap:** GET /sitemap.xml con BASE_URL para URLs canónicas.
- **Scripts:** deploy.ps1 / deploy.sh, verificar_backend.bat; opcional ngrok para webhooks en local. Tesseract debe estar instalado en el sistema para OCR.

---

## 10. PUNTOS DÉBILES Y RIESGOS

1. **Persistencia solo JSON:** Sin transacciones, sin índices; riesgo de corrupción y cuellos de botella con concurrencia y crecimiento de datos.
2. **Estado en memoria:** consultas_escaneo e historiales se pierden al reiniciar; no escalable con múltiples instancias sin estado compartido.
3. **Identificación por session_id:** Cualquiera con el ID puede suplantar al usuario; no hay 2FA ni recuperación de cuenta.
4. **Precio PRO:** Traducciones indican 9,99 €/mes en algunos textos; Stripe está a 4,99 €/mes; inconsistencia a corregir.
5. **Plantillas:** Varias páginas (preguntar, registrar, dashboard, adaptador, bodega, escanear) no extienden base.html; posible menú e i18n desiguales.
6. **Búsqueda:** app.py usa buscar_vinos_avanzado con VINOS_MUNDIALES; ya existe uso unificado en busqueda_service; conviene centralizar todo en el servicio para no duplicar lógica.
7. **Backups de plantillas:** index_before_fix.html, index_backup_final.html, index_backup.html en templates; limpiar o mover a backup/.
8. **Dependencias:** Versiones fijas en requirements; revisar CVE y actualizaciones periódicas.

---

## 11. RECOMENDACIONES TÉCNICAS

1. Unificar toda la búsqueda en `busqueda_service.buscar_vinos_avanzado(app.state.vinos_mundiales, ...)` desde app.py y rutas.
2. Migrar plantillas que no usan base.html a una base común para navegación e i18n consistentes.
3. Alinear copy de precio PRO (9,99 vs 4,99) en traducciones y/o Stripe.
4. En producción: CORS_ORIGINS explícito, BASE_URL correcto, Stripe en modo live y webhook verificado.
5. Valorar migración a base de datos (SQLite/PostgreSQL) para usuarios, bodegas, ofertas, comunidad y analytics si se espera más carga o múltiples instancias.
6. Mantener documentación de API (FastAPI ya expone OpenAPI/Swagger) y tests (pytest) para regresiones.

---

## 12. INVENTARIO DE RUTAS (REFERENCIA RÁPIDA)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | / | Landing |
| GET | /health, /ready | Salud y listo |
| GET | /inicio, /escanear, /registrar, /preguntar, /bodega, /dashboard, /adaptador, /mapa, /planes, /privacidad, /comunidad/feed, /comunidad/perfil/{username} | Páginas HTML |
| GET | /oferta/crear, /mis-ofertas | Ofertas (HTML) |
| GET | /set-lang | Cookie idioma |
| POST | /api/landing-notify | Notificación Google Play |
| POST | /escanear | Escanear etiqueta |
| POST | /registrar-vino | Registrar vino |
| GET | /historial-escaneos | Historial escaneos |
| GET | /preguntar-sumiller | Experto en Vinos (rule-based) |
| POST | /api/preguntar-local | Experto en Vinos IA local (PRO) |
| POST | /api/feedback-vino | Feedback vino |
| GET | /api/vino-por-consulta | Vino por consulta_id (agente) |
| POST | /analyze/text | Análisis por texto |
| GET | /vinos, /buscar, /paises | Catálogo y búsqueda |
| GET | /api/buscar-para-registrar | Búsqueda + externos (OFF) |
| GET | /api/status | Estado API |
| GET/POST/PUT/DELETE | /api/bodega/* | Bodega (botellas, alertas, valoración, stock, registros-hoy) |
| GET | /planes | Página planes |
| GET | /api/check-limit | Límite freemium |
| POST | /crear-checkout-session | Stripe checkout |
| GET | /pago-exitoso, /pago-cancelado | Post-pago |
| POST | /webhook-stripe | Webhook Stripe |
| GET/POST/... | /api/ofertas/* | Ofertas y uploads |
| POST/GET/PUT/DELETE | /api/crear-perfil, /api/mi-perfil, /api/perfil/{username}, /api/seguir/*, /api/feed, /api/notificaciones/* | Comunidad |
| GET | /api/perfil/{username}/valoraciones, /api/perfil/{username}/actividad | Perfil público |
| POST/GET/PUT/DELETE | /api/valorar-vino, /api/vino/{id}/valoraciones, /api/wishlist/*, /api/valoracion/* | Valoraciones y wishlist |
| GET | /vino/{vino_id}/comprar, /api/vino/{vino_id}/enlaces | Comprar |
| GET | /api/lugares-cerca, /api/geocode | Geolocalización |
| GET | /analytics/* | Analytics |
| GET | /informes/bodega, POST /informes/cata | Informes |
| GET | /adaptador/token, POST /adaptador/config | Adaptador |
| GET | /c/{codigo}, /qr, /api/qr/* | QR personalizados |
| GET | /sitemap.xml | Sitemap |

---

*Documento generado para copiar/pegar y uso interno. Revisar con el código actual en cada despliegue.*
