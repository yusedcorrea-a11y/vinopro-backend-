# Agente local Sumiller - VinoPro

El **agente local** permite usar el Sumiller Virtual con IA generativa (OpenRouter, modelos gratuitos) o con respuestas rule-based **sin conexión a APIs de pago**, optimizado para hardware modesto (p. ej. Lenovo IdeaPad 3 Slim).

## Requisitos

- **Python 3.10+** (ya usado por el backend VinoPro)
- **Backend VinoPro** en marcha en `http://localhost:8001`
- Opcional: **OpenRouter API Key** (200K tokens/mes gratis) para respuestas con IA generativa

No es obligatorio tener Go ni PicoClaw/ZeroClaw instalados: el agente se ejecuta como servicio Python en el puerto 8080.

## Arquitectura

```
[Frontend /preguntar] --> [Backend :8001 POST /api/preguntar-local]
                              |
                              v
                    [Agente local :8080 POST /skill/sumiller]
                              |
              +---------------+---------------+
              v                               v
    [Backend :8001 GET /api/vino-por-consulta]   [OpenRouter API] (opcional)
              |                               |
              v                               v
         consulta_id --> vino              LLM --> respuesta
```

- El backend recibe la pregunta y el `consulta_id`, obtiene el vino de su estado y reenvía la petición al agente en 8080.
- El agente (opción A) pide el vino al backend con `GET /api/vino-por-consulta?consulta_id=...` y (opción B) si tiene `OPENROUTER_API_KEY`, llama a OpenRouter con el contexto del vino; si no, responde con reglas fijas.
- Respuesta en JSON: `{ "respuesta": "...", "vino": { ... } }`.

## Cómo arrancar el agente

### Windows (recomendado)

```batch
cd backend_optimized
install_local_agent.bat
```

El script comprueba Python, dependencias y arranca el agente en el puerto 8080. Deje la ventana abierta.

### Manual (cualquier SO)

```bash
cd backend_optimized
python -m venv venv   # solo la primera vez
source venv/bin/activate   # Linux/Mac  |  venv\Scripts\activate  en Windows
pip install fastapi uvicorn httpx pydantic
export AGENTE_PORT=8080
export VINOPRO_BACKEND_URL=http://127.0.0.1:8001
export OPENROUTER_API_KEY=sk-or-v1-xxx   # opcional
python -m agente_local.server
```

Con variables por defecto:

```bash
python -m agente_local.server
```

- **Puerto:** 8080 (cambiable con `AGENTE_PORT`)
- **Backend:** `http://127.0.0.1:8001` (cambiable con `VINOPRO_BACKEND_URL`)

## Inicio automático (Windows)

- Copie un acceso directo de `install_local_agent.bat` en la carpeta de Inicio de Windows (`Win+R` → `shell:startup`). El agente se iniciará al abrir sesión (con una ventana de consola).
- Para ejecutarlo como tarea en segundo plano sin ventana, puede usar `pythonw -m agente_local.server` desde una tarea programada.

## Cómo detener el agente

- En la ventana donde está corriendo: **Ctrl+C**.
- Si lo ha puesto como servicio, detenga ese servicio (p. ej. `sc stop` o el gestor de servicios en Windows).

## Modelos gratuitos (OpenRouter)

Con **OpenRouter** puedes usar modelos gratuitos sin tarjeta:

| Modelo | Uso recomendado |
|--------|------------------|
| `google/gemini-2.0-flash-exp:free` | General (por defecto en el agente) |
| `meta-llama/llama-3.2-3b-instruct:free` | Hardware muy justo |

- Límites típicos del tier gratis: ~20 req/min, ~200 req/día (consulte [OpenRouter](https://openrouter.ai/docs/faq)).
- Obtenga la API Key: [OpenRouter Keys](https://openrouter.ai/keys).
- Defina la variable de entorno: `OPENROUTER_API_KEY=sk-or-v1-...`
- Modelo por defecto del agente: `OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free` (puede cambiarlo).

## Uso en la interfaz

1. Arranque el backend (`uvicorn` en 8001) y el agente (`install_local_agent.bat` o `python -m agente_local.server`).
2. En **Preguntar al sumiller** elija **Modo: IA Local**.
3. Indique un Consulta ID (obtenido al escanear un vino) y haga la pregunta.
4. Se mostrará el tiempo de respuesta y si la respuesta viene de **IA Local** o **Nube** (fallback).

Si el agente no está disponible o da error, el backend hace **fallback** a la lógica rule-based (Nube) y la respuesta sigue mostrándose con “Nube”.

## Solución de problemas

### "Backend VinoPro no disponible"
- Compruebe que el backend está en marcha en `http://127.0.0.1:8001`.
- Si usa otra URL/puerto, configure `VINOPRO_BACKEND_URL` antes de arrancar el agente.

### "Vino no encontrado para ese consulta_id"
- El `consulta_id` debe corresponder a un escaneo reciente en la misma instancia del backend (estado en memoria). Escanee de nuevo el vino y use el nuevo ID.

### "Demasiadas solicitudes" (429)
- El agente aplica límite de 60 peticiones/minuto para proteger el tier gratis. Espere un minuto o reduzca la frecuencia de preguntas.

### Respuestas siempre “rule-based”, sin IA
- Sin `OPENROUTER_API_KEY` el agente solo usa reglas. Defina la variable con su clave de OpenRouter y reinicie el agente.

### Puerto 8080 en uso
- Cambie el puerto: `set AGENTE_PORT=8082` (Windows) o `export AGENTE_PORT=8082` (Linux/Mac) y reinicie.
- En el backend, el agente se llama a `http://127.0.0.1:8080` por defecto; si cambia el puerto del agente, tendría que ajustar la URL en el backend (variable o constante donde se construye la URL del agente).

### Consumo de memoria
- El agente está pensado para usar poca memoria (cache en memoria acotado, sin modelos locales). En reposo suele estar muy por debajo de 50 MB.

## Endpoints del agente (puerto 8080)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio |
| POST | `/skill/sumiller` | Body: `{"consulta_id":"uuid","pregunta":"texto","perfil":"aficionado"}`. Respuesta: `{"respuesta":"...","vino":{...}}` |

## Prueba rápida

Con el backend y el agente en marcha:

```bash
# Health
curl http://localhost:8080/health

# Skill (necesita un consulta_id válido obtenido tras escanear)
curl -X POST http://localhost:8080/skill/sumiller -H "Content-Type: application/json" -d "{\"consulta_id\":\"SU-UUID-AQUI\",\"pregunta\":\"¿Con qué marida?\"}"
```

Si no tiene un `consulta_id` real, primero escanee un vino en la web y use el ID que le devuelva la respuesta del escaneo.
