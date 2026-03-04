# Análisis de la app VINO PRO IA

**Fecha:** 2026-02-19  
**Objetivo:** Revisar rutas, servicios, plantillas y flujos para detectar cosas sueltas, bugs e incoherencias.

---

## 1. Bug corregido

### `/api/vino-por-consulta` (agente local)

- **Problema:** Tras guardar las consultas de escaneo como `{ "vino": vino, "key": key }`, este endpoint devolvía ese objeto completo. El agente local (puerto 8080) hace `vino = data.get("vino")` y esperaba el diccionario del vino; recibía el wrapper y `vino.get("nombre")` fallaba o daba datos incorrectos.
- **Solución:** Se desempaqueta el valor: si es un dict con clave `"vino"`, se devuelve `raw["vino"]`; si no (formato antiguo), se devuelve `raw`. Así el agente siempre recibe el objeto vino correcto.

---

## 2. Coherencia y posibles mejoras

### 2.1 Duplicación de lógica de búsqueda

- **app.py** define `buscar_vinos_avanzado(texto, limite)` y usa la variable global `VINOS_MUNDIALES`.
- **services/busqueda_service.py** define `buscar_vinos_avanzado(vinos_dict, texto, limite)` (misma lógica, recibe el dict).
- **Uso:** Escaneo usa el servicio; `POST /analyze/text` y `GET /buscar` usan la función de `app.py`.
- **Recomendación:** Unificar usando solo `busqueda_service.buscar_vinos_avanzado(request.app.state.vinos_mundiales, texto, limite)` desde `app.py` para evitar que la lógica se desincronice.

### 2.2 Plantillas que no usan `base.html`

Estas páginas son HTML completos (con su propio `<header>`, nav, etc.) y **no** extienden `base.html`:

- `preguntar.html`
- `registrar.html`
- `dashboard.html`
- `adaptador.html`
- `bodega.html`
- `escanear.html`

Las que **sí** usan `base.html` (y por tanto nav común, selector de idioma, tema):  
`index.html`, `planes.html`, `pago-exitoso.html`, `pago-cancelado.html`, `comprar_vino.html`.

**Consecuencia:** En las páginas “sueltas” el menú y el idioma pueden estar duplicados o desalineados respecto al resto. Si quieres una experiencia uniforme, convendría que todas las rutas HTML usen `render_page()` y plantillas que extiendan `base.html`.

### 2.3 Precio PRO: texto vs Stripe

- En **traducciones** (ej. `planes.precio_pro`) aparece **"9,99 €/mes"**.
- En **Stripe** el precio configurado es **4,99 €/mes**.
- **Recomendación:** Igualar el copy (traducciones y/o Stripe) para que no haya discrepancia.

### 2.4 Archivos de plantillas que parecen backup

En `templates/` hay:

- `index_before_fix.html`
- `index_backup_final.html`
- `index_backup.html`

No se usan en las rutas actuales. Puedes borrarlos o moverlos a una carpeta `templates/backup/` si quieres conservarlos.

---

## 3. Comprobaciones realizadas (sin problemas)

- **Rutas:** Todos los routers están incluidos en `app.py` (escaneo, sumiller, bodega con prefix `/api`, analytics, informes, adaptador con prefix `/api`, comprar, planes, pagos).
- **GET /historial-escaneos:** Definido en `routes/escaneo.py`; `preguntar.html` lo llama con `X-Session-ID`. OK.
- **Bodega API:** Las llamadas desde `bodega.html` y `registrar.html` usan `/api/bodega/...` correctamente (router con prefix `/api`).
- **Session ID:** `static/app.js` define `window.getSessionId()`; las páginas que envían `X-Session-ID` (bodega, escanear, preguntar, registrar, planes) pueden usarlo. La clave en `localStorage` es `vino_pro_session_id`.
- **Comprar:** `comprar_vino.html` extiende `base.html` y usa `t()` para i18n. Coherente con el resto.
- **Consultas de escaneo:** Escaneo guarda `{ "vino", "key" }`; sumiller y `api_preguntar_local` desempaquetan bien; `api_vino_por_consulta` ya devuelve solo el vino (corregido arriba).

---

## 4. Resumen de rutas y flujos

| Área        | Rutas principales |
|------------|--------------------|
| Páginas    | `/`, `/escanear`, `/registrar`, `/preguntar`, `/bodega`, `/dashboard`, `/adaptador`, `/planes`, `/pago-exitoso`, `/pago-cancelado`, `/vino/{id}/comprar` |
| API bodega | `/api/bodega`, `/api/bodega/registros-hoy`, `/api/bodega/botellas`, PUT/DELETE botellas, `/api/bodega/alertas`, `/api/bodega/valoracion`, `/api/bodega/stock` |
| Escaneo    | POST `/escanear`, POST `/registrar-vino`, GET `/historial-escaneos` |
| Sumiller   | GET `/preguntar-sumiller`, POST `/api/preguntar-local` (en app.py) |
| Pagos      | POST `/crear-checkout-session`, GET `/pago-exitoso`, GET `/pago-cancelado`, POST `/webhook-stripe` |
| Otros      | `/api/status`, `/api/vino-por-consulta`, `/api/check-limit`, `/analytics/*`, `/informes/*`, `/api/token`, `/api/config`, POST `/analyze/text`, GET `/vinos`, GET `/buscar` |

---

## 5. Próximos pasos opcionales

1. Unificar búsqueda en `busqueda_service` y usarla desde `app.py`.
2. Hacer que preguntar, escanear, registrar, bodega, dashboard y adaptador usen `base.html` (y `render_page`) para nav e i18n unificados.
3. Alinear precio PRO en traducciones con el precio de Stripe (4,99 € o el que elijas).
4. Eliminar o mover los `index_*backup*.html` si ya no los necesitas.

Si quieres, en el siguiente paso podemos implementar solo la unificación de búsqueda o solo la migración de una plantilla (por ejemplo `preguntar.html`) a `base.html`.
