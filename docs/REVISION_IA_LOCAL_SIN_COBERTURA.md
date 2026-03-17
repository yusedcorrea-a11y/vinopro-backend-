# Revisión: IA local y servicio mínimo sin cobertura

Resumen de cómo está implementado el **servicio mínimo** cuando el usuario no tiene cobertura (sin internet) y qué componentes intervienen.

---

## 1. Flujo actual (lo que ya tienes)

### Cuando el usuario **sí tiene internet**
- **Nube ☁️:** La pregunta va a `/preguntar-sumiller` (backend) y puede usar IA en la nube (p. ej. Gemini) o lógica rule-based según configuración.
- **IA Local 🖥️ (PRO):** La pregunta va a `POST /api/preguntar-local` → backend llama al **agente local** (puerto 8080). El agente intenta OpenRouter; si falla, usa **respuestas rule-based** sin devolver error al usuario.

### Cuando el usuario **no tiene internet** (sin cobertura)

1. **Frontend (`preguntar.js`):**
   - Si `navigator.onLine === false`, el selector de modo se pone en **IA Local** (solo si el usuario es PRO; si no es PRO, la fila del modo está oculta).
   - Listeners `offline` / `online` actualizan el modo automáticamente.
   - Objetivo: sin internet, intentar usar el agente local en la misma red/PC.

2. **Backend (`app.py` – `POST /api/preguntar-local`):**
   - Solo usuarios **PRO** (403 si no).
   - Llama al agente en `http://127.0.0.1:8080/skill/sumiller`.
   - Si el agente **no responde** (timeout, conexión rechazada): **fallback a lógica rule-based** (`_responder_pregunta`) y devuelve `"modo": "nube"`. El usuario recibe respuesta igualmente.

3. **Agente local (`agente_local/server.py`):**
   - Obtiene el vino del backend (`GET /api/vino-por-consulta` en el mismo backend).
   - Si tiene `OPENROUTER_API_KEY`: intenta OpenRouter; si hay **timeout o error de red** → usa **fallback rule-based** (`_respuesta_rule_based`) y no devuelve 500.
   - Si no tiene API key: solo respuestas rule-based (100 % sin necesidad de internet una vez el backend es accesible).

---

## 2. Dónde está el “servicio mínimo”

| Componente | Servicio mínimo sin cobertura |
|-------------|-------------------------------|
| **Agente local** | Respuestas **rule-based** cuando OpenRouter falla (sin internet) o no hay API key. No devuelve error al usuario. |
| **Backend** | Si el agente (8080) no responde, **fallback a rule-based** y responde con `modo: "nube"`. |
| **Frontend** | Con **sin cobertura** pone modo **IA Local** (si PRO) para que las peticiones vayan a `/api/preguntar-local` y así usen agente + fallback. |

El “servicio mínimo” es, en la práctica: **respuestas basadas en reglas** (datos del vino: maridaje, descripción, bodega, etc.) sin llamar a ninguna IA en la nube.

---

## 3. Requisitos para que funcione “sin cobertura”

- **Backend** y **agente** tienen que ser **accesibles** desde el dispositivo del usuario:
  - **Mismo PC:** navegador en `http://localhost:8001`, agente en `127.0.0.1:8080` → funciona sin internet.
  - **Misma red (WiFi):** app/navegador apuntando al IP del PC (ej. `http://192.168.1.x:8001`), agente en ese mismo PC → funciona sin internet.
- Si el usuario está en **móvil sin datos y sin WiFi** (o en otra red), no puede alcanzar el backend → no hay servicio hasta que tenga conexión a ese backend.

---

## 4. Limitaciones actuales

1. **IA Local solo PRO:** Si el usuario no es PRO, no puede elegir IA Local y no verá el cambio automático a “local” cuando se pone offline.
2. **Sin mensaje específico al fallar la petición:** Si `fetch` a `/api/preguntar-local` o `/preguntar-sumiller` falla (p. ej. sin conexión al backend), el frontend muestra un error genérico; no explica que “sin cobertura” el servicio mínimo requiere estar en la misma red que el PC con el agente.

---

## 5. Mejora opcional aplicada

En `preguntar.js`, cuando la petición falla y el usuario está **offline** (`!navigator.onLine`), se muestra un mensaje claro:

- Que no hay conexión.
- Que el servicio mínimo (IA Local) requiere estar en la **misma red** que el PC donde corre el backend y el agente.

Así el usuario entiende por qué no funciona y qué tiene que hacer (conectarse a la misma WiFi que el PC con VINO PRO / agente).

---

## 6. Cómo probar “sin cobertura”

1. En el PC: arrancar backend (ej. puerto 8001) y agente (`python -m agente_local.server` o `install_local_agent.bat`).
2. Opcional: quitar `OPENROUTER_API_KEY` para simular solo rule-based.
3. En el navegador del mismo PC: desactivar la red (modo avión o desenchufar WiFi) y abrir `http://localhost:8001/preguntar`.
4. Usuario PRO: modo debe pasarse a IA Local; hacer una pregunta (con un `consulta_id` de un escaneo previo). Debe responder con rule-based.
5. Comprobar que la respuesta muestra “IA Local” o “Nube” según corresponda y que no hay error 500.

---

## 7. Resumen

- **Sí tienes** servicio mínimo sin cobertura: el agente y el backend usan **solo rule-based** cuando no hay OpenRouter o cuando el agente no está disponible.
- **Condición:** El dispositivo del usuario debe poder alcanzar al backend (y el backend al agente en 127.0.0.1:8080), típicamente mismo PC o misma red WiFi.
- **Mejora:** Mensaje en frontend cuando falla la petición y el usuario está offline, indicando que el servicio mínimo requiere estar en la misma red que el PC del agente.

---

## 8. Listo para tocar el violín 🎻

Para ponerlo en marcha en 3 pasos (backend → agente → elegir IA Local en la app), ver **`README_AGENTE_LOCAL.md`** → sección **"Para tocar el violín"**.
