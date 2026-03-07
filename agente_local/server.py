"""
Agente local Experto en Vinos para VinoPro.
Escucha en puerto 8080, skill POST /skill/sumiller.
Obtiene el vino desde el backend (8001) y responde con OpenRouter (modelo gratuito)
o respuesta rule-based si no hay API key. Errores de IA se capturan y se usa fallback sin devolver 500.
"""
import json
import logging
import os
import time
import hashlib
from collections import OrderedDict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
BACKEND_URL = os.environ.get("VINOPRO_BACKEND_URL", "http://127.0.0.1:8001")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
PORT = int(os.environ.get("AGENTE_PORT", "8080"))
RATE_LIMIT_PER_MIN = 60
CACHE_MAX = 200

app = FastAPI(title="VinoPro Agente Experto en Vinos", version="1.0")

# Rate limit: ventana 1 minuto
_rate_ts: list[float] = []
_cache: OrderedDict = OrderedDict()


def _rate_limit() -> bool:
    now = time.time()
    _rate_ts[:] = [t for t in _rate_ts if now - t < 60]
    if len(_rate_ts) >= RATE_LIMIT_PER_MIN:
        return False
    _rate_ts.append(now)
    return True


def _cache_key(consulta_id: str, pregunta: str) -> str:
    text = f"{consulta_id}|{pregunta.strip().lower()}"
    return hashlib.sha256(text.encode()).hexdigest()[:32]


def _respuesta_rule_based(vino: dict, pregunta: str, perfil: str = "aficionado") -> str:
    """Respuesta sin LLM, solo con datos del vino."""
    pregunta = (pregunta or "").strip().lower()
    nombre = vino.get("nombre") or "este vino"
    maridaje = vino.get("maridaje") or "No tenemos información de maridaje."
    descripcion = vino.get("descripcion") or "No hay descripción."
    notas_cata = vino.get("notas_cata") or "No hay notas de cata."
    bodega = vino.get("bodega") or "No especificada"
    region = vino.get("region") or "Por determinar"
    pais = vino.get("pais") or "Desconocido"
    tipo = vino.get("tipo") or "tinto"
    precio = vino.get("precio_estimado") or "No indicado"
    puntuacion = vino.get("puntuacion")

    if any(p in pregunta for p in ["maridaje", "comer", "comida", "acompañar", "ir bien", "recomienda"]):
        return f"Para {nombre}, recomendamos: {maridaje}"
    if any(p in pregunta for p in ["descripcion", "descripción", "qué es", "cuéntame", "hablar"]):
        return f"{nombre}: {descripcion}"
    if any(p in pregunta for p in ["notas", "cata", "sabor", "aroma", "gusto"]):
        return f"Notas de cata de {nombre}: {notas_cata}"
    if any(p in pregunta for p in ["bodega", "productor", "quién hace"]):
        return f"La bodega de {nombre} es: {bodega}."
    if any(p in pregunta for p in ["región", "region", "origen", "dónde", "donde"]):
        return f"Procede de {region}, {pais}."
    if any(p in pregunta for p in ["tipo", "blanco", "tinto", "rosado"]):
        return f"Es un vino {tipo}."
    if any(p in pregunta for p in ["precio", "cuesta", "valor"]):
        return f"Precio estimado: {precio}."
    if any(p in pregunta for p in ["puntuacion", "puntuación", "puntos", "nota", "valoración"]):
        return f"Tiene una puntuación de {puntuacion} puntos." if puntuacion is not None else "No tenemos puntuación registrada."
    return f"Resumen de {nombre}: {bodega}, {region} ({pais}). {descripcion[:200]}... Maridaje: {maridaje}"


class SumillerRequest(BaseModel):
    consulta_id: str
    pregunta: str
    perfil: str = "aficionado"


@app.get("/health")
def health():
    return {"status": "ok", "service": "agente-sumiller", "port": PORT}


@app.get("/test-openrouter")
def test_openrouter():
    """
    Prueba de conexión a OpenRouter. Devuelve ok, error detallado o que no hay API key.
    Útil para diagnosticar sin afectar al experto en vinos.
    """
    if not OPENROUTER_API_KEY:
        return {"ok": False, "error": "OPENROUTER_API_KEY no configurada", "detalle": "Añádala en .env"}
    try:
        with httpx.Client(timeout=12.0) as client:
            r = client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vinopro.local",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": "Di solo: OK"}],
                    "max_tokens": 10,
                },
            )
            logger.info("OpenRouter: status code %s", r.status_code)
            if r.status_code != 200:
                logger.warning("OpenRouter: status code %s, body: %s", r.status_code, (r.text or "")[:300])
                return {"ok": False, "error": f"HTTP {r.status_code}", "detalle": r.text[:500] if r.text else ""}
            try:
                out = r.json()
            except json.JSONDecodeError as e:
                logger.warning("OpenRouter: JSON decode error: %s, body: %s", e, (r.text or "")[:200])
                return {"ok": False, "error": "Respuesta no es JSON válido", "detalle": str(e), "body": r.text[:300]}
            choices = out.get("choices") or []
            text = (choices[0].get("message") or {}).get("content", "") if choices else ""
            return {"ok": True, "respuesta": text.strip(), "status": r.status_code}
    except httpx.TimeoutException:
        logger.warning("OpenRouter: timeout")
        return {"ok": False, "error": "Timeout", "detalle": "OpenRouter no respondió a tiempo"}
    except Exception as e:
        logger.exception("test_openrouter")
        return {"ok": False, "error": type(e).__name__, "detalle": str(e)}


@app.post("/skill/sumiller")
def skill_sumiller(req: SumillerRequest):
    """
    Skill experto en vinos: recibe consulta_id y pregunta, obtiene el vino del backend,
    responde con OpenRouter (o rule-based si no hay key) y devuelve { respuesta, vino }.
    """
    consulta_id = (req.consulta_id or "").strip()
    pregunta = (req.pregunta or "").strip()
    perfil = (req.perfil or "aficionado").strip() or "aficionado"

    if not consulta_id or not pregunta:
        raise HTTPException(status_code=400, detail="consulta_id y pregunta son obligatorios.")

    # Cache
    ck = _cache_key(consulta_id, pregunta)
    if ck in _cache:
        cached = _cache[ck]
        _cache.move_to_end(ck)
        return cached

    # Rate limit
    if not _rate_limit():
        raise HTTPException(status_code=429, detail="Demasiadas solicitudes. Espere un minuto (límite gratuito).")

    # Obtener vino del backend VinoPro
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(f"{BACKEND_URL}/api/vino-por-consulta", params={"consulta_id": consulta_id})
            if r.status_code != 200:
                raise HTTPException(status_code=404, detail="Vino no encontrado para ese consulta_id. Escanee el vino antes.")
            try:
                data = r.json()
            except json.JSONDecodeError as e:
                logger.warning("Backend vino-por-consulta devolvió no-JSON: %s", e)
                raise HTTPException(status_code=502, detail="Backend devolvió respuesta inválida.")
            vino = data.get("vino") or {}
    except httpx.RequestError as e:
        logger.warning("Backend VinoPro no disponible: %s", e)
        raise HTTPException(status_code=502, detail="Backend VinoPro no disponible.")

    # Intentar OpenRouter si hay API key; solo parsear JSON con status 200; cualquier error -> fallback (nunca 500 ni mostrar error al usuario)
    respuesta_texto = None
    if OPENROUTER_API_KEY:
        try:
            context = (
                f"Vino: {vino.get('nombre', 'N/A')}. "
                f"Bodega: {vino.get('bodega', 'N/A')}. "
                f"Región/País: {vino.get('region', '')} ({vino.get('pais', '')}). "
                f"Tipo: {vino.get('tipo', 'N/A')}. "
                f"Descripción: {(vino.get('descripcion') or '')[:300]}. "
                f"Notas de cata: {(vino.get('notas_cata') or '')[:200]}. "
                f"Maridaje: {vino.get('maridaje', 'N/A')}. "
                f"Precio estimado: {vino.get('precio_estimado', 'N/A')}. "
                f"Puntuación: {vino.get('puntuacion', 'N/A')}."
            )
            with httpx.Client(timeout=15.0) as client:
                r = client.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://vinopro.local",
                    },
                    json={
                        "model": OPENROUTER_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Eres un experto en vinos virtual. Respondes en 1-3 frases breves, en español, "
                                    "solo con la información del vino que te proporciono. No inventes datos. "
                                    "Perfil del usuario: " + perfil + "."
                                ),
                            },
                            {
                                "role": "user",
                                "content": f"Contexto del vino:\n{context}\n\nPregunta del usuario: {pregunta}",
                            },
                        ],
                        "max_tokens": 256,
                        "temperature": 0.4,
                    },
                )
                if r.status_code == 200:
                    try:
                        out = r.json()
                        choices = out.get("choices") or []
                        if choices:
                            msg = choices[0].get("message")
                            if isinstance(msg, dict):
                                respuesta_texto = (msg.get("content") or "").strip()
                        if not respuesta_texto and out.get("error"):
                            logger.info("OpenRouter: error en JSON: %s", out.get("error"))
                    except json.JSONDecodeError as e:
                        logger.warning("OpenRouter: JSON decode error: %s, body: %s", e, (r.text or "")[:200])
                else:
                    logger.warning("OpenRouter: status code %s, body: %s", r.status_code, (r.text or "")[:300])
        except httpx.TimeoutException:
            logger.warning("OpenRouter: timeout")
        except httpx.RequestError as e:
            logger.warning("OpenRouter: error de conexión: %s", e)
        except Exception as e:
            logger.warning("OpenRouter: %s", e, exc_info=True)

    if not respuesta_texto:
        logger.info("OpenRouter: usando fallback local")
        respuesta_texto = _respuesta_rule_based(vino, pregunta, perfil)

    result = {"respuesta": respuesta_texto, "vino": vino}
    if len(_cache) >= CACHE_MAX:
        _cache.popitem(last=False)
    _cache[ck] = result
    return result


if __name__ == "__main__":
    print(f"🖥️ Agente Experto en Vinos local en http://0.0.0.0:{PORT}")
    print(f"   Backend: {BACKEND_URL} | OpenRouter: {'configurado' if OPENROUTER_API_KEY else 'no (respuestas rule-based)'}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
