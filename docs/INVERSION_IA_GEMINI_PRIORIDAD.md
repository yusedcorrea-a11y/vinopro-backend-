# Inversión de prioridad: Gemini primero, IA local para offline

Resumen de cómo queda el flujo cuando **invertimos** las IAs: con datos/WiFi **siempre** responde **Gemini** (sumiller en la nube, información veraz en tiempo real); lo que Gemini encuentra y no estaba en la base local **se guarda** para futuras respuestas offline.

---

## 1. Prioridad con conexión (datos / WiFi)

- **Gemini (nube)** es el sumiller principal: da información veraz y en tiempo real.
- Si el usuario pregunta sobre un vino que **sí está** en la base local (por escaneo o por nombre):
  - Se intenta primero **Gemini** (`responder_sobre_vino`) con la ficha del vino.
  - Si Gemini responde, se devuelve esa respuesta con `modo: "nube"`.
  - Si Gemini falla (sin API key, timeout, etc.), se usa el agente local (8080) o el fallback rule-based.
- Si el usuario pregunta sobre un vino que **no está** en la base local:
  - Se llama a **Gemini** (`buscar_vino_en_nube`) para buscar en la nube.
  - Gemini devuelve respuesta + ficha del vino (nombre, bodega, tipo, maridaje, etc.).
  - Ese vino **se guarda** en `data/vinos_aprendidos.json` y se añade al catálogo en memoria.
  - La próxima vez (incluso sin cobertura) la IA local encontrará ese vino en la base local y podrá responder offline.

---

## 2. Flujo resumido

| Situación | Qué pasa |
|-----------|----------|
| Usuario tiene cobertura + vino **en** BD local | Gemini responde con la ficha local → respuesta veraz en tiempo real. |
| Usuario tiene cobertura + vino **no** en BD local | Gemini busca en la nube → responde → **guardamos el vino en BD local** (vinos_aprendidos.json) → siguiente vez ya está en local. |
| Usuario sin cobertura | Se usa IA local / agente 8080 o rule-based; la búsqueda es solo en la base local (catálogo + vinos_aprendidos + Mi Bodega). |

---

## 3. Dónde está implementado

- **Prioridad Gemini cuando hay vino:** `app.py` → `POST /api/preguntar-local`: antes de llamar al agente 8080 se llama a `sumiller_gemini_service.responder_sobre_vino`; si hay respuesta, se devuelve con `modo: "nube"`.
- **Búsqueda en nube cuando el vino no está en BD:** `app.py` → mismo endpoint: si la búsqueda local no encuentra el vino, se llama a `sumiller_gemini_service.buscar_vino_en_nube`; si Gemini devuelve respuesta + ficha, se guarda con `vinos_aprendidos_service.guardar_vino_aprendido` y se actualiza `app.state.vinos_mundiales`.
- **Persistencia:** `services/vinos_aprendidos_service.py` → escribe en `data/vinos_aprendidos.json`; ese archivo se carga al arrancar el backend (al final del catálogo) para que los vinos aprendidos estén disponibles sin reiniciar.

---

## 4. Respuesta a “¿el vino pasa a ser uno más en la base?”

**Sí.** El vino que Gemini encuentra en la nube y que no estaba en la base local:
1. Se persiste en **data/vinos_aprendidos.json**.
2. Se añade al catálogo en memoria (`app.state.vinos_mundiales`) en esa misma petición.
3. En los siguientes arranques del backend se carga con el resto del catálogo.

Así, ese vino queda **registrado** en la base y la IA local puede usarlo en futuras respuestas offline.
