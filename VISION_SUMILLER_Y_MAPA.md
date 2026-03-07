# Visión: Experto en Vinos IA y mapa "Dónde tomarlo"

Documento de referencia del proyecto: cómo debe responder el experto en vinos y cómo encaja el mapa con futuros patrocinadores.

---

## 1. Respuesta del experto en vinos (estructura deseada)

Cuando un usuario pregunte por **cualquier vino**, el experto en vinos debe entregar (en este orden):

| Orden | Bloque | Contenido |
|-------|--------|-----------|
| 1 | **Info básica** | Nombre, bodega, región, país, tipo, puntuación (resumen breve). |
| 2 | **Especificación técnica** | Graduación, variedad de uva, añada si aplica, notas de cata, temperatura de servicio, etc. |
| 3 | **Maridaje** | Maridaje específico para ese vino (con qué comerlo). |
| 4 | **Dónde comprarlo** | Enlace Amazon (si tiene ese país); si no, enlace a donde pueda comprarlo (tienda local / internacional). |
| 5 | **Dónde tomarlo** | No ese vino en concreto (no sabemos si el local lo tiene), sino **lugares cerca de su zona** donde pueda tomar vino (restaurantes, vinotecas, bares) → **aquí aparece el mapa**. |

---

## 2. Lo que ya tenemos en backend

- **Experto en Vinos:** `GET /preguntar-sumiller` (rule-based), `POST /api/preguntar-local` (IA local + fallback). Responde con texto, maridaje, descripción; ya detecta "dónde sirven" y redirige a `/mapa`.
- **Enlaces de compra:** `GET /api/vino/{vino_id}/enlaces`, `GET /vino/{vino_id}/comprar`. Amazon por país + tiendas locales (enlaces_service).
- **Lugares cercanos:** `GET /api/lugares-cerca` (lat, lon, radio_km) y `GET /api/lugares-destacados` (partners).
- **Geocodificación:** `GET /api/geocode?ciudad=...` (lat, lon).
- **Mapa web:** página `/mapa` (lugares en mapa).

Falta en **app móvil**: pantalla Experto en Vinos, pantalla/componente Mapa, y que la respuesta del experto en vinos venga **estructurada** (bloques 1–5) para pintarlos en la UI.

---

## 3. Patrocinadores en el mapa (tu idea)

- En "Dónde tomarlo" mostramos sitios cercanos donde el usuario puede tomar vino.
- **Más adelante:** dar **prioridad en el mapa a negocios patrocinadores** de la app (restaurantes, vinotecas, bares que paguen por destacar).
- Ya existe `lugares_destacados.json` y el endpoint `/api/lugares-destacados` (partners). Solo habría que:
  - Añadir un campo tipo `patrocinador: true` o `prioridad: 1` a esos lugares.
  - En la app: al listar lugares (cercanos + destacados), ordenar primero por patrocinador/prioridad y luego por distancia o valoración.

**Valoración:** La idea encaja muy bien con el producto: el usuario ya está en contexto "quiero tomar vino"; dar prioridad a quien patrocina la app es justo y monetiza sin romper la experiencia. Conviene dejar el modelo de datos preparado (ej. `prioridad` o `es_patrocinador` en lugares) para activarlo cuando quieras.

---

## 4. Plan por fases (resumen)

| Fase | Qué hacer | Dónde |
|------|-----------|--------|
| **Fase 1** | Respuesta del experto en vinos **estructurada**: bloques info básica, técnica, maridaje, enlace compra. Backend devuelve JSON con secciones; app pinta cada bloque. | Backend (experto en vinos) + App (pantalla Experto en Vinos) |
| **Fase 2** | En la misma respuesta, incluir **enlace(s) de compra** (ya tenemos API enlaces por vino/país). En app: botón "Comprar" que use ese enlace o la pantalla de enlaces. | Backend (incluir enlaces en respuesta) + App |
| **Fase 3** | **Mapa "Dónde tomarlo"** en la app: llamar a `lugares-cerca` (con ubicación o ciudad) y `lugares-destacados`, mostrar mapa con pins. | App (pantalla/componente Mapa + permisos ubicación) |
| **Fase 4** | **Patrocinadores:** en backend, campo prioridad/patrocinador en lugares; en app, ordenar por prioridad y destacar (badge "Patrocinador" o similar). | Backend (modelo lugares) + App (orden + UI) |

---

## 5. Siguiente paso concreto

Empezar por **Fase 1**: definir en backend un formato de respuesta del experto en vinos con secciones (info_basica, especificacion_tecnica, maridaje, enlaces_compra, texto_respuesta) y en la app una pantalla "Preguntar al experto en vinos" que muestre esos bloques. Cuando eso esté, añadimos enlaces (Fase 2) y luego el mapa (Fase 3) y patrocinadores (Fase 4).

Este documento se puede ir actualizando según avancemos (endpoints, nombres de campos, diseños).
