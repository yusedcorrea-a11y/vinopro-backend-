# Mejoras posibles del flujo Gemini + vinos aprendidos

Análisis antes de commit: qué podemos mejorar en el nuevo flujo (prioridad Gemini + guardar vinos de la nube en BD local).

---

## 1. Estado actual del flujo

- Con cobertura: Gemini responde primero (sobre vino en BD o buscando en nube).
- Si el vino no está en BD → Gemini busca en nube → guardamos en `vinos_aprendidos.json` y respondemos.
- Sin cobertura: IA local + catálogo (incluye vinos aprendidos).

---

## 2. Mejoras que sí se pueden hacer (y aportan)

### 2.1 Indicar al usuario que el vino se ha añadido a la base

**Qué:** Cuando guardamos un vino nuevo desde Gemini, devolver en la respuesta un flag `vino_anadido_a_base: true`.

**Por qué:** El usuario entiende que ese vino ya quedará disponible para futuras consultas (incluso offline). Mejora la confianza y la percepción del servicio.

**Esfuerzo:** Bajo (un campo en el JSON de respuesta).

---

### 2.2 Evitar duplicados al guardar

**Qué:** Antes de guardar en `vinos_aprendidos.json`, comprobar si ya existe un vino con el mismo nombre (+ bodega) en el catálogo o en aprendidos. Si existe, no crear otra entrada; opcionalmente actualizar la existente con datos nuevos de Gemini.

**Por qué:** Evita duplicados (ej. "Rioja Crianza" con distinta key) y mantiene el archivo más limpio.

**Esfuerzo:** Bajo (normalizar nombre+bodega y buscar en dict antes de guardar).

---

### 2.3 Normalizar y limitar el vino que devuelve Gemini

**Qué:** Antes de guardar, normalizar: `tipo` en minúsculas y uno de (tinto, blanco, rosado, espumoso); recortar strings largos (descripcion, notas_cata a un máximo de caracteres); asegurar que `nombre` y `bodega` existen.

**Por qué:** Gemini a veces devuelve "Tinto" o "Espumoso" con mayúsculas, o textos muy largos. Un formato uniforme evita sorpresas en IA local y en la UI.

**Esfuerzo:** Bajo (función de normalización en `vinos_aprendidos_service` o en el caller).

---

### 2.4 Que el flujo Nube también aprenda

**Qué:** En `GET /preguntar-sumiller` (modo Nube), si en el futuro se pasa un parámetro tipo "nombre_vino" y ese vino no está en la BD, llamar a Gemini, guardar el vino aprendido y responder (igual que en preguntar-local).

**Por qué:** Hoy solo aprendemos cuando el usuario usa IA Local. Si pregunta por un vino por nombre en modo Nube, no se guarda. Unificar comportamiento en ambos modos.

**Esfuerzo:** Medio (añadir parámetro opcional y rama en preguntar-sumiller).

---

### 2.5 Parseo más robusto del JSON de Gemini

**Qué:** A veces Gemini incluye markdown o texto extra alrededor del JSON. Usar un fallback: buscar el primer `{` y el último `}` en la línea de VINO_JSON y extraer ese substring para `json.loads`.

**Por qué:** Reduce fallos de parseo y hace el flujo más estable.

**Esfuerzo:** Bajo (mejorar el extract en `buscar_vino_en_nube`).

---

## 3. Mejoras opcionales (más coste o menos prioritarias)

- **Límite de tamaño de vinos_aprendidos:** Por ejemplo máximo 500 entradas; si se supera, borrar las más antiguas o menos “usadas”. Útil a largo plazo; no crítico para el primer commit.
- **Cache de “no encontrado”:** No volver a llamar a Gemini por el mismo nombre en X minutos si ya devolvió “no identifico el vino”. Ahorra llamadas; añade lógica de cache.
- **Idioma de la respuesta:** Pasar `lang` a Gemini para que responda en el idioma del usuario. Ya existe traducción a posteriori; es una alternativa o complemento.

---

## 4. Resumen

- **Implementadas antes del commit:**  
  - (2.1) Flag `vino_anadido_a_base` en la respuesta + mensaje en la UI: "Este vino se ha añadido a la base local para futuras consultas (también sin cobertura)."  
  - (2.2) Evitar duplicados: mismo nombre+bodega en aprendidos → se actualiza la entrada existente en lugar de crear otra.  
  - (2.3) Normalizar vino antes de guardar: tipo en (tinto, blanco, rosado, espumoso, dulce), recorte de descripcion/notas_cata/maridaje a 500 caracteres y de nombre/bodega/region/pais a 150.  
  - (2.5) Parseo más robusto del JSON de Gemini: se extrae el substring entre el primer `{` y el último `}` en la línea VINO_JSON para tolerar texto o markdown alrededor.  

- **(2.4) Implementado:** El flujo Nube (`GET /preguntar-sumiller`) también aprende: cuando la pregunta es tipo "háblame del X" / "qué es el X" y ese vino no está en la BD, se llama a `buscar_vino_en_nube`, se guarda en `vinos_aprendidos.json` y se responde con `vino_anadido_a_base: true`.

---

## 5. Añada (edad del vino) en el control

Para que no haya duplicados cuando el mismo vino existe en distintas cosechas (solo cambia la añada), se incorporó la **añada** (año de cosecha) en todo el flujo:

- **Gemini:** En `_vino_a_texto` se incluye "Añada (edad/cosecha)" cuando el vino la tiene; en `buscar_vino_en_nube` el JSON pedido a Gemini incluye la clave **anada** (año de 4 dígitos). Así, al identificar un vino por etiqueta o nombre, Gemini puede devolver la añada.
- **Clave y duplicados:** La key del vino aprendido incluye la añada cuando existe (ej. `rioja-crianza-bodega-x-2019` vs `rioja-crianza-bodega-x-2020`). El control de duplicados compara **nombre + bodega + añada**: misma añada → actualizar entrada; distinta añada → nueva entrada.
- **Persistencia:** En `vinos_aprendidos.json` cada vino puede llevar el campo **anada** (string de 4 dígitos). Se normaliza desde número o string (ej. 2019, "2019", "cosecha 19" → "2019").
