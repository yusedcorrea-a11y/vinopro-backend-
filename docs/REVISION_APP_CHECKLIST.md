# Revisión de la app Vino Pro IA – Acción por acción

Lista para revisar **cada acción** de la app y confirmar que funciona. Marca ✅ cuando lo compruebes.

---

## Cómo revisar

1. **Arranca el backend** (en una terminal):
   ```bash
   cd c:\Users\yused\Documents\VINO_PRO_FINAL\backend_optimized
   uvicorn app:app --host 127.0.0.1 --port 8001
   ```
2. Abre el navegador en **http://127.0.0.1:8001**
3. Sigue la lista abajo y comprueba cada ítem (o ejecuta el script de comprobación automática).

---

## 1. Páginas principales (GET)

| # | Acción | URL | Qué comprobar | ✅ |
|---|--------|-----|----------------|---|
| 1.1 | Inicio | `/` | Página de inicio carga, menú visible, selector de idioma | |
| 1.2 | Escanear | `/escanear` | Página de escaneo (subir imagen / texto / código de barras) | |
| 1.3 | Registrar vino | `/registrar` | Formulario de registro manual de vino | |
| 1.4 | Preguntar (experto en vinos) | `/preguntar` | Página del experto en vinos IA (preguntas por texto/voz) | |
| 1.5 | Mi Bodega | `/bodega` | Página de la bodega virtual | |
| 1.6 | Planes | `/planes` | Página de planes Gratis/PRO y precio 4,99 €/mes | |
| 1.7 | Comprar (ejemplo) | `/vino/vega_sicilia_unico/comprar` | Página de compra con pestañas y guía "¿Dónde tomarlo?" | |
| 1.8 | Dashboard | `/dashboard` | Solo si tienes ruta; si no existe, omitir | |
| 1.9 | Adaptador | `/adaptador` | Página del adaptador para restaurantes (token, config) | |
| 1.10 | Pago exitoso | `/pago-exitoso` | Página de confirmación tras pago Stripe | |
| 1.11 | Pago cancelado | `/pago-cancelado` | Página de pago cancelado | |

---

## 2. Escaneo

| # | Acción | Cómo probar | Qué comprobar | ✅ |
|---|--------|-------------|----------------|---|
| 2.1 | Escanear por texto | En `/escanear`, escribe "Vega Sicilia" o "Rioja" y envía | Respuesta con vino(s) encontrado(s), botón Comprar si aplica | |
| 2.2 | Historial de escaneos | GET con sesión: header `X-Session-ID` | `GET /historial-escaneos` devuelve lista (puede estar vacía) | |

---

## 3. Experto en Vinos (preguntar)

| # | Acción | Cómo probar | Qué comprobar | ✅ |
|---|--------|-------------|----------------|---|
| 3.1 | Pregunta sin vino | En `/preguntar`, escribe "¿Qué vino va bien con carne?" | Respuesta con recomendaciones (nombres, precios) o maridaje | |
| 3.2 | Pregunta sobre un vino | Primero escanea "Marqués de Riscal" (o similar), luego en Preguntar haz una pregunta sobre ese vino | Respuesta referida al vino escaneado | |
| 3.3 | Recomendación por región | "¿Dónde me puedo tomar un Ribera del Duero?" | Respuesta con vinos de Ribera del Duero (si está en BD) | |

---

## 4. Bodega (API bajo /api)

| # | Acción | Método y ruta | Qué comprobar | ✅ |
|---|--------|----------------|----------------|---|
| 4.1 | Listar bodega | GET `/api/bodega` con header `X-Session-ID: test-session-1` | 200, JSON con lista (puede estar vacía) | |
| 4.2 | Añadir botella | POST `/api/bodega/botellas` con body (nombre, bodega, tipo, etc.) y `X-Session-ID` | 200/201, botella añadida | |
| 4.3 | Registros de hoy | GET `/api/bodega/registros-hoy` con `X-Session-ID` | 200, número de registros hoy | |
| 4.4 | Valoración | GET `/api/bodega/valoracion` con `X-Session-ID` | 200, total botellas y valoración estimada | |
| 4.5 | Alertas | GET `/api/bodega/alertas` con `X-Session-ID` | 200, lista de alertas (temp/humedad) | |

---

## 5. Comprar y guías por país

| # | Acción | Cómo probar | Qué comprobar | ✅ |
|---|--------|-------------|----------------|---|
| 5.1 | Comprar por país | `/vino/vega_sicilia_unico/comprar?pais=ES` | Pestañas nacional/internacional/subastas; en España aparece Guía Repsol en "¿Dónde tomarlo?" | |
| 5.2 | Otro país | `?pais=IT` | Guía tipo Gambero Rosso para Italia | |
| 5.3 | API enlaces | GET `/api/vino/vega_sicilia_unico/enlaces` | JSON con enlaces nacional/internacional/subastas | |

---

## 6. Planes y límites

| # | Acción | Cómo probar | Qué comprobar | ✅ |
|---|--------|-------------|----------------|---|
| 6.1 | Comprobar límite | GET `/api/check-limit` con header `X-Session-ID` | JSON con límite (ej. 50 para gratis) y uso | |

---

## 7. Pagos (Stripe)

| # | Acción | Cómo probar | Qué comprobar | ✅ |
|---|--------|-------------|----------------|---|
| 7.1 | Crear sesión checkout | POST `/crear-checkout-session` con `X-Session-ID` | 200 y `url` de Stripe (o 402/500 si Stripe no configurado) | |
| 7.2 | Páginas resultado | Visitar `/pago-exitoso` y `/pago-cancelado` | Ambas cargan sin error | |

---

## 8. Adaptador restaurantes

| # | Acción | Cómo probar | Qué comprobar | ✅ |
|---|--------|-------------|----------------|---|
| 8.1 | Obtener token | GET `/api/adaptador/token` | 200, JSON con `token` | |
| 8.2 | Actualizar config | POST `/api/adaptador/config?token=XXX` con body (nombre, programas, webhook_url) | 200, `success: true` | |

---

## 9. Analytics e informes

| # | Acción | Ruta | Qué comprobar | ✅ |
|---|--------|------|----------------|---|
| 9.1 | Dashboard analytics | GET `/analytics/dashboard?dias=30` | 200, HTML o JSON según implementación | |
| 9.2 | Informe bodega | GET `/informes/bodega` (con sesión si aplica) | 200 o descarga PDF | |

---

## 10. API auxiliares

| # | Acción | Ruta | Qué comprobar | ✅ |
|---|--------|------|----------------|---|
| 10.1 | Estado | GET `/api/status` | 200, backend OK | |
| 10.2 | Buscar vinos | GET `/buscar?q=rioja` | 200, lista de vinos | |
| 10.3 | Países | GET `/paises` | 200, lista de países en BD | |
| 10.4 | Idioma | GET `/set-lang?lang=en` | Redirige y cookie de idioma en EN | |

---

## Comprobación automática (script)

Para comprobar de golpe que las rutas responden (sin probar toda la lógica a mano):

```bash
python scripts/revision_app_acciones.py
```

El script hace peticiones HTTP a `http://127.0.0.1:8001` y muestra OK/FAIL por cada ítem. **El servidor debe estar arrancado** en otra terminal antes de ejecutarlo.

Cuando termines la revisión, todas las casillas ✅ deberían estar marcadas para las acciones que uses. Si algo falla, anota el número de ítem y el error para corregirlo.
