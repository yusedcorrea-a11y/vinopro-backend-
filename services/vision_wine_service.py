"""
Servicio de IA de visión para análisis de etiquetas de vino.
Fallback cuando el OCR local no obtiene texto suficiente.
Usa Google Gemini 2.0 Flash (google-genai, API v1 estable).
Variable de entorno: GOOGLE_API_KEY.
"""
import io
import json
import logging
import os
import re

logger = logging.getLogger(__name__)

# Modelo estable (evitar 404 de gemini-1.5-flash)
MODELO_GEMINI = "gemini-2.0-flash"

# Estructura esperada del JSON
ESQUEMA_ENTIDADES = {
    "bodega": None,
    "nombre": None,
    "añada": None,
    "denominacion_origen": None,
    "variedad": None,
}

PROMPT_VISION = """Analiza esta etiqueta de vino y extrae en formato JSON exactamente estos campos:
- bodega: nombre del productor o bodega
- nombre: nombre del vino
- añada: año de cosecha (solo número, ej: 2021)
- denominacion_origen: región, DO, DOC o denominación
- variedad: variedad(es) de uva

Si no estás seguro de algún campo, usa null. Si no ves la etiqueta o no es una botella de vino, devuelve todos null.
Responde ÚNICAMENTE con un objeto JSON válido, sin markdown ni texto adicional."""


def _limpiar_json_vision(texto: str) -> dict:
    """Extrae y parsea JSON de la respuesta (puede venir envuelta en markdown)."""
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
    """Convierte entidades a texto para búsqueda en BD."""
    partes = []
    for k in ("nombre", "bodega", "denominacion_origen", "variedad"):
        v = ent.get(k)
        if v and isinstance(v, str) and v.strip():
            partes.append(v.strip())
    if ent.get("añada"):
        partes.append(str(ent["añada"]))
    return " ".join(partes) if partes else ""


def _normalizar_entidades_vision(ent: dict) -> dict:
    """Asegura estructura consistente y tipos correctos."""
    out = dict(ESQUEMA_ENTIDADES)
    for k in out:
        v = ent.get(k)
        if v is None:
            continue
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
        else:
            if isinstance(v, str) and v.strip():
                out[k] = v.strip()[:200] if k in ("bodega", "nombre") else v.strip()[:150]
    return out


def _mensaje_error_especifico(exc: Exception) -> str:
    """Traduce excepciones de Gemini a mensajes claros para el usuario."""
    err = str(exc).lower()
    if "404" in err or "not found" in err:
        return "El modelo de IA no está disponible (404). Contacta al administrador."
    if "429" in err or "quota" in err or "rate limit" in err or "resource exhausted" in err or "resource_exhausted" in err:
        return "Límite de uso de la IA alcanzado. Prueba más tarde o escribe el nombre del vino abajo."
    if "401" in err or "403" in err or "invalid" in err or "api_key" in err or "permission" in err:
        return "Error de autenticación con la IA. Verifica GOOGLE_API_KEY en el servidor."
    if "500" in err or "503" in err or "unavailable" in err:
        return "El servicio de IA no está disponible. Prueba más tarde o escribe el nombre del vino."
    return f"Error al analizar la imagen con IA: {str(exc)[:150]}"


def analizar_etiqueta_vision(imagen_bytes: bytes) -> dict | None:
    """
    Envía la imagen a Google Gemini 2.0 Flash para extraer datos de la etiqueta.
    :param imagen_bytes: bytes de la imagen (JPEG, PNG)
    :return: dict con texto, entidades, origen="vision" o None si falla.
             Si falla con excepción conocida: {"error": "mensaje_especifico"}
    """
    if not imagen_bytes or len(imagen_bytes) < 100:
        return None

    api_key = (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    if not api_key:
        logger.debug("[Vision] No hay GOOGLE_API_KEY en .env")
        return None

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.warning("[Vision] google-genai no instalado: pip install google-genai")
        return {"error": "Falta instalar google-genai. Contacta al administrador."}

    mime = "image/jpeg" if imagen_bytes[:2] == b"\xff\xd8" else "image/png"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MODELO_GEMINI,
            contents=[
                types.Part.from_text(text=PROMPT_VISION),
                types.Part.from_bytes(data=imagen_bytes, mime_type=mime),
            ],
            config=types.GenerateContentConfig(max_output_tokens=500),
        )
    except Exception as e:
        msg = _mensaje_error_especifico(e)
        logger.warning("[Vision] Gemini falló: %s", e)
        return {"error": msg}

    try:
        texto_resp = (response.text or "").strip()
    except AttributeError:
        texto_resp = ""
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text"):
                    texto_resp += part.text or ""
        texto_resp = texto_resp.strip()

    if not texto_resp:
        return None

    entidades_raw = _limpiar_json_vision(texto_resp)
    entidades = _normalizar_entidades_vision(entidades_raw)
    texto = _entidades_a_texto_busqueda(entidades)
    if not texto:
        return None

    logger.info("[Vision] Gemini extrajo: %s", texto[:80])
    return {"texto": texto, "entidades": entidades, "origen": "vision"}
