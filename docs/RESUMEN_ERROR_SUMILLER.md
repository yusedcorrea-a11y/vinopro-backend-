# Resumen: Error en Preguntar al sumiller

## Qué pasa

En la página **Preguntar al sumiller**, al enviar preguntas como:
- *"hoy toca comida japonesa que vino pongo ?"*
- *"tengo pelmeni para cenar que vino me aconsejas para acompañar mis pelmeni"*
- *"tengo cocido hoy que vino me aconsejas..."*

el usuario ve:
**"Error al procesar la pregunta. Inténtalo de nuevo."**

El backend devuelve **HTTP 500** y el frontend muestra ese mensaje (en `static/js/preguntar.js` cuando `!r.ok` y se usa `data.detail`).

---

## Qué se ha hecho hasta ahora

1. **Respuesta inválida / JSON**
   - Se dejó de devolver un *generador* en `fallback_sin_resultados` y se devuelve una **lista** para no agotar el iterador al usarlo dos veces en la ruta.
   - Se envolvió la lógica en **try/except** en la ruta del sumiller y se devuelve JSON con `detail` en el 500 (ya no HTML).

2. **Defensas en datos**
   - **Keys solo string:** `vinos_ref_para_guardar` se filtra para que solo contenga strings (evitar dicts en historial que rompían `registrar_busqueda` / `get_recomendaciones_personalizadas`).
   - **`recomendaciones_service`:** `registrar_busqueda` y `get_recomendaciones_personalizadas` aceptan/usan solo keys string; try/except para no tumbar la respuesta si fallan.
   - **`formatear_respuesta_maridaje`:** Se usa `item.get("vino")` y se comprueba que sea dict; si `partes` queda vacío, se devuelve mensaje de fallback en vez de acceder a `partes[-1]`.
   - **`buscar_vinos_por_maridaje` y `fallback_sin_resultados`:** Comprobación de que `vinos_dict` sea `dict`; si no, devuelven lista vacía / mensaje sin iterar.

3. **Causa identificada: `patrocinadores.json` en el catálogo**
   - En `app.py`, `cargar_todos_los_vinos()` hace `vinos.update(data)` con **todos** los JSON de `data/` que no están en la lista de exclusión.
   - **`patrocinadores.json`** tiene estructura `{"_comentario": "...", "enlaces": [...]}` (no es clave → ficha de vino). Al mezclarlo con el catálogo, en el diccionario global quedan entradas cuyo valor es **string** o **list**.
   - En `buscar_vinos_avanzado` (y en cualquier iteración `for key, vino in vinos_dict.items()` que haga `vino.get("tipo")` o similar) eso provoca **AttributeError** (p. ej. `'str' object has no attribute 'get'`).
   - **Solución aplicada:** Se añadió `patrocinadores.json` a la lista **excluir** en `app.py` y se añadió en `busqueda_service.py` un `if not isinstance(vino, dict): continue` al iterar en `buscar_vinos_avanzado`.

4. **Depuración**
   - En el 500 del sumiller se incluye el mensaje de la excepción en el JSON: `detail = "... [Debug: {err_msg}]"` para poder ver en pantalla qué falla si sigue ocurriendo.
   - Script de prueba: `scripts/test_sumiller_flow.py` (simula request y llama a `_preguntar_sumiller_general` con BD real). Usar **scope como dict** (`{"type": "http", "method": "GET", ...}`), no `Scope(...)`. En local, con `patrocinadores.json` excluido, el test pasa (899 vinos, respuesta OK).

5. **Defensa extra en `app.py`**
   - En `GET /vinos` (`listar_vinos`), se filtra por `isinstance(v, dict)` y se usa `.get()` para no caer si falta algún campo; así ningún valor no-dict en el catálogo rompe ese endpoint.

---

## Dónde está el flujo (por si hay que seguir depurando)

- **Ruta:** `GET /preguntar-sumiller?texto=...&perfil=aficionado`
- **Archivos:**  
  - `routes/sumiller.py` (endpoint, `_preguntar_sumiller_general`, extracción de “comida”, construcción de la respuesta).  
  - `services/sumiller_service.py` (maridaje, cocinas tradicionales, `buscar_vinos_por_maridaje`, `formatear_respuesta_maridaje`, `fallback_sin_resultados`).  
  - `services/busqueda_service.py` (`buscar_vinos_avanzado`, `buscar_vinos_con_sugerencia`).  
  - `app.py` (`cargar_todos_los_vinos`, lista **excluir** de JSON que no son catálogo).
- **Estado en request:** `request.app.state.vinos_mundiales` debe ser un diccionario donde **cada valor** sea un dict de ficha de vino (con `nombre`, `tipo`, etc.). Cualquier valor que no sea dict (string, list, null) puede provocar el mismo tipo de error en cualquier iteración que use `.get(...)`.

---

## Cómo seguir en un nuevo chat

1. **Confirmar despliegue:** Que en Render esté desplegada la versión que incluye:
   - exclusión de `patrocinadores.json` en `app.py`,
   - `isinstance(vino, dict)` en `buscar_vinos_avanzado`,
   - defensa en `listar_vinos` (solo entradas dict),
   - y el `[Debug: ...]` en el 500 del sumiller.
   - Si en local `python scripts/test_sumiller_flow.py` pasa pero en producción sigue el 500, el fallo es casi seguro por **código no desplegado** o por **otro JSON en data/** con estructura no-catálogo cargado solo en producción.
2. **Si el error continúa:** Pedir que se copie el mensaje completo que aparece en pantalla (incluido el texto después de `[Debug: ...]`) y pegarlo en el nuevo chat.
3. **En local:** Ejecutar `python scripts/test_sumiller_flow.py` desde la raíz del backend; si falla, el traceback indicará la línea exacta.
4. **Revisar otros JSON:** Comprobar si algún otro archivo en `data/` se carga con `cargar_todos_los_vinos()` y tiene estructura que no sea `{ "key": { "nombre", "tipo", ... } }`; en ese caso, añadirlo a **excluir** o filtrar por `isinstance(v, dict)` donde se use el diccionario de vinos.

---

## Resumen en una frase

El error viene de que el diccionario global de “vinos” incluye entradas que **no son fichas de vino** (p. ej. de `patrocinadores.json`), y al hacer `vino.get("tipo")` sobre un string o lista se produce una excepción; la corrección es excluir esos JSON del catálogo y/o comprobar `isinstance(vino, dict)` en todas las iteraciones sobre ese diccionario.
