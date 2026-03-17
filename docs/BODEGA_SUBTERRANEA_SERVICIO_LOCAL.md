# Bodega subterránea: servicio local sin cobertura

Visión y mejoras para que el usuario (bodeguero, sumiller, aficionado) tenga **servicio útil en local** cuando está en bodega subterránea y **pierde cobertura**.

---

## 1. Escenario

- El usuario está **en la bodega** (muchas son subterráneas).
- **Sin cobertura** (sin datos móviles, WiFi solo en la entrada).
- Necesita: **registrar vinos en local**, **consultar dudas sobre un vino** y que la **IA local** use la **base de datos local** para encontrar el vino y dar una respuesta acertada.

---

## 2. Lo que ya está implementado

### 2.1 Registrar en local (Mi Bodega)

- **POST /api/bodega/botellas**: añade una botella a la bodega del usuario (header `X-Session-ID`).
- Requiere que el backend sea alcanzable (misma red que el PC/servidor donde corre el backend). En bodega sin cobertura, el registro se puede hacer cuando el dispositivo se conecte a la WiFi de la bodega (entrada) o desde un terminal en red local.
- Los datos se guardan en **data/bodegas.json** (local al servidor).

### 2.2 IA local busca en la base local y responde

- **POST /api/preguntar-local** acepta ahora:
  - **consulta_id**: vino del último escaneo (como antes).
  - **nombre_o_key** o **texto_busqueda**: nombre del vino o clave para **buscar en la base local** (catálogo + Mi Bodega).
- Flujo:
  1. El usuario elige **IA Local** y escribe el **nombre del vino** (o lo elige del desplegable si antes escaneó).
  2. El backend busca el vino en: (a) catálogo por key, (b) catálogo por nombre (búsqueda avanzada), (c) **Mi Bodega** del usuario por nombre.
  3. Si lo encuentra, la IA local (agente 8080 o fallback rule-based) responde con maridaje, descripción, temperatura, etc.
- En **Preguntar al experto** (web) hay un campo **"Nombre del vino (si no escaneaste)"** que solo se muestra en modo IA Local; permite escribir el nombre y preguntar sin haber escaneado (ideal para bodega sin cobertura).

### 2.3 Sin cobertura: mismo PC o misma red

- Si el **backend y el agente** están en un PC/servidor en la bodega (o en la oficina con WiFi), los dispositivos en esa **misma red** pueden usar:
  - Registrar botellas (cuando haya conexión a ese backend).
  - Preguntar por nombre y obtener respuesta desde la base local + IA local.
- Sin internet, OpenRouter no funciona; el agente usa **respuestas rule-based** con los datos del vino encontrado en la BD local.

---

## 3. Resumen de cambios recientes

| Qué | Dónde |
|-----|--------|
| Preguntar por nombre/key en IA Local | Backend: `POST /api/preguntar-local` acepta `nombre_o_key` o `texto_busqueda`; busca en catálogo y en Mi Bodega. |
| Campo "Nombre del vino (si no escaneaste)" | `templates/preguntar.html` + `static/js/preguntar.js`: visible solo en modo IA Local; se envía como `nombre_o_key` cuando no hay consulta_id. |
| Búsqueda en Mi Bodega | Backend: si no hay match en catálogo, busca en las botellas del usuario por nombre y opcionalmente enriquece con el vino del catálogo por `vino_key`. |

---

## 4. Qué más se puede añadir en local (ideas)

- **Registro offline en la app**: cola de altas en el móvil cuando no hay red; al recuperar conexión (WiFi de la bodega), sincronizar con **POST /api/bodega/botellas**. Requiere cambios en la app (Expo/React Native) y opcionalmente un endpoint de sincronización por lote.
- **Listado "Mi Bodega" en la IA**: que el agente pueda recibir el listado de botellas del usuario (o el backend lo inyecte en el contexto) para respuestas del tipo "¿Qué vino de los que tengo va bien con cordero?" sin tener que nombrar uno por uno.
- **Preguntas frecuentes en local**: respuestas rápidas tipo "temperatura de servicio", "cuántas botellas me quedan de X" leyendo de la bodega y del catálogo, sin llamar a OpenRouter.
- **Voz en bodega**: ya existe el botón de micrófono en Preguntar; asegurar que en modo IA Local la pregunta por voz también pueda ir con `nombre_o_key` (por ejemplo, leyendo el nombre del vino del campo "Nombre del vino").
- **Exportar catálogo/bodega para uso 100 % offline en el dispositivo**: que la app pueda descargar un subconjunto del catálogo + Mi Bodega y usar lógica rule-based en el propio dispositivo cuando no hay conexión al backend (requiere lógica en la app y posiblemente un bundle descargable).
- **Indicador "Modo bodega"**: en la app, un modo que priorice IA Local y el campo de nombre de vino, y muestre un aviso cuando no hay conexión pero sí hay red local (WiFi bodega).

---

## 5. Cómo probar (bodega subterránea)

1. Backend y agente en marcha (misma máquina o servidor en la red de la bodega).
2. En **Preguntar al experto**: modo **IA Local**.
3. Sin escanear: escribe en **"Nombre del vino (si no escaneaste)"** por ejemplo "Rioja Crianza" o el nombre de un vino de tu bodega.
4. Pregunta: "¿Qué marida?" o "¿A qué temperatura lo sirvo?".
5. Debe responder con datos del vino encontrado en la base local (catálogo o Mi Bodega).

Si cortas la conexión a internet pero mantienes la red local, el agente seguirá respondiendo con rule-based usando ese vino.
