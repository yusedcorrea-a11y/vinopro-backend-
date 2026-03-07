"""
Servicio de IA de visión para análisis de etiquetas de vino.
Fallback cuando el OCR local no obtiene texto suficiente.
Usa Google Gemini 2.0 Flash con `google-genai` y API v1 estable.
Incluye resize, caché por imagen, rate limit por sesión y cooldown tras 429.
"""
import hashlib
import io
import json
import logging
import os
import re
import time

logger = logging.getLogger(__name__)

MODELO_GEMINI = os.environ.get("VINO_VISION_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"
MAX_IMAGE_SIDE_VISION = 1280
MAX_OUTPUT_TOKENS_VISION = 280
CACHE_TTL_SECONDS = 600
VISION_LIMIT_PER_MINUTE = 3
VISION_LIMIT_PER_HOUR = 10
VISION_COOLDOWN_429_SECONDS = 60
RETRY_DELAYS_SECONDS = (0.5, 1.0)

_VISION_CACHE: dict[str, dict] = {}
_VISION_CALLS_BY_SESSION: dict[str, list[float]] = {}
_VISION_COOLDOWN_BY_SESSION: dict[str, float] = {}

ESQUEMA_ENTIDADES = {
    "bodega": None,
    "nombre": None,
    "añada": None,
    "denominacion_origen": None,
    "variedad": None,
    "tipo_vino": None,
    "pais": None,
    "crianza": None,
}

PROMPT_VISION = """Analiza UNA etiqueta de vino y devuelve SOLO JSON válido, sin markdown ni texto extra.

Reglas:
- No inventes datos.
- Usa null si no estás seguro.
- Prioriza lo que realmente se ve en la etiqueta.
- Si la identidad no es fiable, deja la ficha del experto en vinos en null.

Devuelve exactamente este objeto:
{
  "texto_visible": [],
  "confidence_global": 0.0,
  "calidad_imagen": {
    "baja_luz": false,
    "reflejos": false,
    "borrosa": false,
    "texto_parcial": false
  },
  "entidades": {
    "bodega": {"valor": null, "confianza": 0.0},
    "nombre": {"valor": null, "confianza": 0.0},
    "añada": {"valor": null, "confianza": 0.0},
    "denominacion_origen": {"valor": null, "confianza": 0.0},
    "variedad": {"valor": null, "confianza": 0.0},
    "tipo_vino": {"valor": null, "confianza": 0.0},
    "pais": {"valor": null, "confianza": 0.0},
    "crianza": {"valor": null, "confianza": 0.0}
  },
  "ficha_sumiller": {
    "notas_cata": null,
    "maridaje": null,
    "temperatura_servicio_c": null,
    "potencial_guarda": null
  }
}"""


def _limpiar_json_vision(texto: str) -> dict:
    if not texto or not texto.strip():
        return dict(ESQUEMA_ENTIDADES)
    t = texto.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", t)
    if m:
        t = m.group(1).strip()
    inicio = t.find("{")
    fin = t.rfind("}")
    if inicio >= 0 and fin > inicio:
        t = t[inicio : fin + 1]
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        logger.warning("[Vision] No se pudo parsear JSON: %s", texto[:200])
        return dict(ESQUEMA_ENTIDADES)


def _entidades_a_texto_busqueda(ent: dict) -> str:
    partes = []
    for k in ("nombre", "bodega", "denominacion_origen", "variedad"):
        v = ent.get(k)
        if isinstance(v, dict):
            v = v.get("valor")
        if v and isinstance(v, str) and v.strip():
            partes.append(v.strip())
    anada = ent.get("añada")
    if isinstance(anada, dict):
        anada = anada.get("valor")
    if anada:
        partes.append(str(anada))
    return " ".join(partes) if partes else ""


def _normalizar_entidades_vision(ent: dict) -> dict:
    out = dict(ESQUEMA_ENTIDADES)
    if ent.get("entidades") and isinstance(ent.get("entidades"), dict):
        ent = ent.get("entidades") or {}
    for k in out:
        v = ent.get(k)
        if v is None:
            continue
        if isinstance(v, dict):
            v = v.get("valor")
        if k == "añada":
            if isinstance(v, int) and 1900 <= v <= 2030:
                out[k] = v
            elif isinstance(v, str):
                v_limpio = re.sub(r"[OoIl]", "0", v)
                v_limpio = re.sub(r"\D", "", v_limpio)
                if len(v_limpio) == 4:
                    anio = int(v_limpio)
                    if 1900 <= anio <= 2030:
                        out[k] = anio
        elif isinstance(v, str) and v.strip():
            max_len = 200 if k in ("bodega", "nombre") else 150
            out[k] = v.strip()[:max_len]
    return out


def _mensaje_error_especifico(exc: Exception) -> str:
    err = str(exc).lower()
    if "404" in err or "not found" in err:
        return "El modelo de IA no está disponible. Contacta al administrador."
    if "429" in err or "quota" in err or "rate limit" in err or "resource exhausted" in err or "resource_exhausted" in err:
        return "Límite de uso de la IA alcanzado. Espera un minuto o escribe el nombre del vino abajo."
    if "401" in err or "403" in err or "invalid" in err or "api_key" in err or "permission" in err:
        return "Error de autenticación con la IA. Verifica GOOGLE_API_KEY en el servidor."
    if "500" in err or "503" in err or "unavailable" in err:
        return "El servicio de IA no está disponible temporalmente. Prueba más tarde."
    return f"Error al analizar la imagen con IA: {str(exc)[:150]}"


def _image_hash(imagen_bytes: bytes) -> str:
    return hashlib.sha256(imagen_bytes).hexdigest()


def _resize_image_bytes(imagen_bytes: bytes) -> tuple[bytes, str]:
    try:
        from PIL import Image, ImageOps
        image = Image.open(io.BytesIO(imagen_bytes))
        image = ImageOps.exif_transpose(image).convert("RGB")
        w, h = image.size
        if max(w, h) > MAX_IMAGE_SIDE_VISION:
            ratio = MAX_IMAGE_SIDE_VISION / max(w, h)
            image = image.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        image.save(out, format="JPEG", quality=88, optimize=True)
        return out.getvalue(), "image/jpeg"
    except Exception:
        mime = "image/jpeg" if imagen_bytes[:2] == b"\xff\xd8" else "image/png"
        return imagen_bytes, mime


def _prune_session_calls(session_key: str, now: float) -> list[float]:
    calls = _VISION_CALLS_BY_SESSION.get(session_key, [])
    calls = [ts for ts in calls if now - ts < 3600]
    _VISION_CALLS_BY_SESSION[session_key] = calls
    return calls


def _session_guard(session_key: str) -> str | None:
    now = time.time()
    cooldown_until = _VISION_COOLDOWN_BY_SESSION.get(session_key, 0)
    if cooldown_until > now:
        espera = int(cooldown_until - now)
        return f"La IA está en espera por límite de uso. Reintenta en {espera}s o escribe el nombre del vino."
    calls = _prune_session_calls(session_key, now)
    last_minute = [ts for ts in calls if now - ts < 60]
    if len(last_minute) >= VISION_LIMIT_PER_MINUTE:
        return "Has hecho demasiados escaneos seguidos. Espera unos segundos antes de volver a intentar."
    if len(calls) >= VISION_LIMIT_PER_HOUR:
        return "Has alcanzado el límite horario de escaneos con IA. Prueba más tarde o usa texto manual."
    return None


def _register_session_call(session_key: str) -> None:
    now = time.time()
    calls = _prune_session_calls(session_key, now)
    calls.append(now)
    _VISION_CALLS_BY_SESSION[session_key] = calls


def _should_retry(exc: Exception) -> bool:
    err = str(exc).lower()
    if "503" in err or "unavailable" in err or "deadline exceeded" in err or "timeout" in err:
        return True
    if "429" in err and "quota" not in err and "resource_exhausted" not in err and "limit: 0" not in err:
        return True
    return False


def _extract_response_text(response) -> str:
    try:
        return (response.text or "").strip()
    except AttributeError:
        texto = ""
        if getattr(response, "candidates", None):
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text"):
                    texto += part.text or ""
        return texto.strip()


def analizar_etiqueta_vision(imagen_bytes: bytes, session_key: str | None = None) -> dict | None:
    """
    Envía la imagen a Gemini solo cuando compensa.
    Usa caché por imagen, reduce tamaño y limita frecuencia por sesión.
    """
    if not imagen_bytes or len(imagen_bytes) < 100:
        return None

    api_key = (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    if not api_key:
        logger.debug("[Vision] No hay GOOGLE_API_KEY en .env")
        return None

    session_key = (session_key or "anon").strip() or "anon"
    guard_msg = _session_guard(session_key)
    if guard_msg:
        return {"error": guard_msg}

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.warning("[Vision] google-genai no instalado: pip install google-genai")
        return {"error": "Falta instalar google-genai. Contacta al administrador."}

    imagen_reducida, mime = _resize_image_bytes(imagen_bytes)
    cache_key = _image_hash(imagen_reducida)
    now = time.time()
    cached = _VISION_CACHE.get(cache_key)
    if cached and now - cached["ts"] < CACHE_TTL_SECONDS:
        logger.info("[Vision] Cache hit para imagen %s", cache_key[:12])
        return cached["value"]

    _register_session_call(session_key)
    client = genai.Client(api_key=api_key)

    last_exc = None
    for attempt, delay in enumerate((0.0,) + RETRY_DELAYS_SECONDS):
        if delay:
            time.sleep(delay)
        try:
            response = client.models.generate_content(
                model=MODELO_GEMINI,
                contents=[
                    types.Part.from_text(text=PROMPT_VISION),
                    types.Part.from_bytes(data=imagen_reducida, mime_type=mime),
                ],
                config=types.GenerateContentConfig(max_output_tokens=MAX_OUTPUT_TOKENS_VISION, temperature=0),
            )
            texto_resp = _extract_response_text(response)
            if not texto_resp:
                return None
            entidades_raw = _limpiar_json_vision(texto_resp)
            entidades = _normalizar_entidades_vision(entidades_raw)
            texto = _entidades_a_texto_busqueda(entidades)
            if not texto:
                return None
            result = {
                "texto": texto,
                "entidades": entidades,
                "origen": "vision",
                "structured": entidades_raw if isinstance(entidades_raw, dict) else {},
            }
            _VISION_CACHE[cache_key] = {"ts": now, "value": result}
            logger.info("[Vision] Gemini extrajo: %s", texto[:80])
            return result
        except Exception as exc:
            last_exc = exc
            if _should_retry(exc) and attempt < len(RETRY_DELAYS_SECONDS):
                logger.warning("[Vision] Reintento %d tras error temporal: %s", attempt + 1, exc)
                continue
            break

    if last_exc is not None:
        err = str(last_exc).lower()
        if "429" in err or "quota" in err or "resource_exhausted" in err or "limit: 0" in err:
            _VISION_COOLDOWN_BY_SESSION[session_key] = time.time() + VISION_COOLDOWN_429_SECONDS
        msg = _mensaje_error_especifico(last_exc)
        logger.warning("[Vision] Gemini falló: %s", last_exc)
        return {"error": msg}
    return None
