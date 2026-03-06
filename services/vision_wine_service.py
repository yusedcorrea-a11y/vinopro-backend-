"""
Servicio de IA de visión para análisis de etiquetas de vino.
Fallback cuando el OCR local no obtiene texto suficiente.
Soporta OpenAI GPT-4o y Anthropic Claude 3.5 Sonnet.
API keys desde variables de entorno: OPENAI_API_KEY, ANTHROPIC_API_KEY.
"""
import base64
import json
import logging
import os
import re

logger = logging.getLogger(__name__)

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
    # Quitar bloques ```json ... ```
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", t)
    if m:
        t = m.group(1).strip()
    # Buscar primer { hasta último }
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
                v_limpio = re.sub(r"[OoIl]", "0", v)  # 2O22 -> 2022
                v_limpio = re.sub(r"\D", "", v_limpio)
                if len(v_limpio) == 4:
                    anio = int(v_limpio)
                    if 1900 <= anio <= 2030:
                        out[k] = anio
        else:
            if isinstance(v, str) and v.strip():
                out[k] = v.strip()[:200] if k in ("bodega", "nombre") else v.strip()[:150]
    return out


def analizar_etiqueta_vision(imagen_bytes: bytes) -> dict | None:
    """
    Envía la imagen a GPT-4o o Claude 3.5 Sonnet para extraer datos de la etiqueta.
    :param imagen_bytes: bytes de la imagen (JPEG, PNG)
    :return: dict con texto, entidades, origen="vision" o None si falla
    """
    if not imagen_bytes or len(imagen_bytes) < 100:
        return None

    b64 = base64.b64encode(imagen_bytes).decode("utf-8")
    mime = "image/jpeg" if imagen_bytes[:2] == b"\xff\xd8" else "image/png"
    data_url = f"data:{mime};base64,{b64}"

    openai_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    anthropic_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()

    # Intentar OpenAI primero
    if openai_key:
        try:
            return _llamada_openai(data_url, openai_key)
        except Exception as e:
            logger.warning("[Vision] OpenAI falló: %s", e)

    # Fallback a Anthropic
    if anthropic_key:
        try:
            return _llamada_anthropic(imagen_bytes, mime, anthropic_key)
        except Exception as e:
            logger.warning("[Vision] Anthropic falló: %s", e)

    if not openai_key and not anthropic_key:
        logger.debug("[Vision] No hay OPENAI_API_KEY ni ANTHROPIC_API_KEY en .env")
    return None


def _llamada_openai(data_url: str, api_key: str) -> dict | None:
    """Llamada a GPT-4o con imagen."""
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("[Vision] openai no instalado: pip install openai")
        return None

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT_VISION},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "low"}},
                ],
            }
        ],
    )
    texto_resp = (response.choices[0].message.content or "").strip()
    if not texto_resp:
        return None
    entidades_raw = _limpiar_json_vision(texto_resp)
    entidades = _normalizar_entidades_vision(entidades_raw)
    texto = _entidades_a_texto_busqueda(entidades)
    if not texto:
        return None
    logger.info("[Vision] GPT-4o extrajo: %s", texto[:80])
    return {"texto": texto, "entidades": entidades, "origen": "vision"}


def _llamada_anthropic(imagen_bytes: bytes, mime: str, api_key: str) -> dict | None:
    """Llamada a Claude 3.5 Sonnet con imagen."""
    try:
        import anthropic
    except ImportError:
        logger.warning("[Vision] anthropic no instalado: pip install anthropic")
        return None

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime, "data": base64.b64encode(imagen_bytes).decode()}},
                    {"type": "text", "text": PROMPT_VISION},
                ],
            }
        ],
    )
    texto_resp = ""
    for b in msg.content:
        if hasattr(b, "text"):
            texto_resp += b.text
    texto_resp = texto_resp.strip()
    if not texto_resp:
        return None
    entidades_raw = _limpiar_json_vision(texto_resp)
    entidades = _normalizar_entidades_vision(entidades_raw)
    texto = _entidades_a_texto_busqueda(entidades)
    if not texto:
        return None
    logger.info("[Vision] Claude extrajo: %s", texto[:80])
    return {"texto": texto, "entidades": entidades, "origen": "vision"}
