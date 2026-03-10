# Revisión del plan Open Food Facts + Global Wine Score

## Resumen ejecutivo

- **Open Food Facts**: La idea encaja muy bien; **ya está integrado** en `api_externa_service.py`. Propuesta: enriquecer ese servicio (certificaciones Bio/Vegano, opcional v2) y, cuando el vino venga de la BD local por EAN, añadir una llamada opcional a OFF para "información extendida" sin romper el flujo.
- **Global Wine Score**: La estrategia de "búsqueda automatizada + parsear primer resultado" es **arriesgada** (scraping, ToS, fragilidad). Recomendación: no implementarla así; dejar placeholder o usar solo puntuaciones propias hasta tener API oficial.

---

## 1. Open Food Facts — Revisión con lupa

### Qué ya tenemos

- **Servicio**: `services/api_externa_service.py`.
- **API usada**: v0 — `https://world.openfoodfacts.org/api/v0/product/{barcode}.json`.
- **Flujo**: En `routes/escaneo.py`, si el usuario envía código de barras (o se detecta EAN en la imagen), se busca primero en la BD local (`buscar_por_codigo_barras_bd` con `vinos_mundiales` desde `data/*.json`); si no está, se llama a `buscar_por_codigo_barras()` que usa OFF y devuelve un vino mapeado.
- **Campos que ya extraemos**: nombre, bodega (brands), país (countries_tags), región, tipo, descripción.

### Qué falta respecto al plan

- **Certificaciones (Bio, Vegano, etc.)**: OFF expone `labels_tags` y `labels`. No los estamos mapeando. Podemos añadir al vino algo como `certificaciones: ["Bio", "Vegano"]` (o `etiquetas`) para mostrarlos en la ficha y reutilizarlos en filtros.
- **Opcional**: usar **API v2** con `fields=...` para respuestas más ligeras y menos tiempo de respuesta.

### Sobre “crear un servicio nuevo” (external_data_service.py)

- **Recomendación**: No crear un segundo servicio. Mantener una sola fuente de verdad para OFF en `api_externa_service.py` y:
  1. Enriquecer `_mapear_producto_a_vino()` con `labels_tags` → `certificaciones` (o `etiquetas`).
  2. Opcional: añadir una función `get_informacion_extendida_por_barcode(barcode)` que devuelva solo `{ certificaciones, bodega, paises }` para **enriquecer un vino que ya vino de la BD local** (cuando el escaneo fue por EAN y el vino está en `data/*.json`). Si OFF no tiene el producto, devolver `None` y en la ruta mostrar "Información extendida no disponible" sin romper el flujo.

### Posibles usos extra en la app

- **Ficha de vino**: Mostrar badges "Bio", "Vegano", "Sin gluten" cuando existan.
- **Filtros en catálogo/búsqueda**: "Solo ecológico", "Solo vegano" (si en el futuro guardamos o exponemos estas etiquetas en más vinos).
- **Ingredientes**: OFF tiene `ingredients_text`; ya se usa en la descripción genérica; se podría exponer como campo aparte para alergenos o preferencias dietéticas.

---

## 2. Global Wine Score — Revisión con lupa

### Qué propone el plan

- No tener API key → usar un "filtro de agregación": búsqueda automatizada (DuckDuckGo o Google) con "[Nombre del vino] global wine score", leer el primer resultado y buscar un número entre 80 y 100.

### Riesgos

- **Scraping / ToS**: Las búsquedas automatizadas y el parseo de HTML suelen estar restringidas en los términos de uso de Google/DuckDuckGo.
- **Fragilidad**: Cualquier cambio de estructura de la página rompe el parser; el "primer resultado" puede no ser Global Wine Score.
- **Rate limits / bloqueos**: Riesgo de bloqueo por uso masivo.
- **Calidad**: Resultados irrelevantes o puntuaciones de otras fuentes (no GWS).

### Recomendación

- **No implementar** la búsqueda automatizada + scraping como está descrito.
- **Alternativas**:
  - Usar solo nuestra puntuación (`puntuacion` en `data/*.json`) y/o texto tipo "Puntuación: no disponible" o "Puntuación estimada según ficha".
  - Cuando exista una API pública de Global Wine Score, integrarla con clave.
  - Si en el futuro se quiere "puntuación externa", valorar APIs de wine con términos de uso claros (ej. Wine-Searcher u otros con API).

---

## 3. Plan de implementación sugerido (solo OFF)

1. **En `api_externa_service.py`**
   - Añadir extracción de `labels_tags` / `labels` en el producto OFF y mapear a una lista legible (ej. `certificaciones`) en el diccionario vino que ya devolvemos.
   - Opcional: soportar consulta a API v2 con `fields` para reducir payload y tiempo.

2. **En `routes/escaneo.py`**
   - Cuando el vino **venga de la BD local por EAN** (respuesta con `encontrado_en_bd: True` y tenemos el EAN), llamar a `get_informacion_extendida_por_barcode(ean)`.
   - Si hay resultado: añadir al JSON de respuesta algo como `informacion_extendida: { certificaciones: [...] }` (o fusionar `certificaciones` en el objeto `vino`).
   - Si no hay resultado en OFF: incluir `informacion_extendida: null` o `mensaje: "Información extendida no disponible"` sin cambiar el resto del flujo.

3. **Global Wine Score**
   - Dejar sin implementar el scraping; opcional: en la UI mostrar un texto fijo tipo "Puntuación GWS: no disponible" o usar solo `puntuacion` de nuestra base.

Con esto se cumple el objetivo de "puerta de atrás" con OFF, se evita duplicar servicios y se deja la puerta abierta a más uso (badges, filtros) sin asumir riesgos con GWS.
