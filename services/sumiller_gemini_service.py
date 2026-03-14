"""
Sumiller con Gemini: respuestas en lenguaje natural (plan gratuito).
Usa la misma GOOGLE_API_KEY que el escáner y la traducción.

- Ahora (gratuito): gemini-2.0-flash — rápido y suficiente para dar vida al sumiller.
- Al monetizar: en Render → Variables → SUMILLER_AI_MODEL = gemini-1.5-pro (o gemini-2.5-pro)
  para respuestas más ricas y mejor contexto.
"""
import logging
import os

logger = logging.getLogger(__name__)

# Plan gratuito: gemini-2.0-flash. Al monetizar: gemini-1.5-pro o gemini-2.5-pro
MODELO_SUMILLER = os.environ.get("SUMILLER_AI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"
MAX_OUTPUT_TOKENS = 380
# Temperatura baja para no inventar datos (0.5 = más fiel a la ficha)
TEMPERATURE = 0.5


def _get_client():
    api_key = (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    if not api_key:
        return None, None
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        return client, types
    except ImportError:
        logger.debug("[SumillerGemini] google-genai no instalado")
        return None, None


def _vino_a_texto(vino: dict) -> str:
    if not vino or not isinstance(vino, dict):
        return ""
    partes = []
    if vino.get("nombre"):
        partes.append(f"Nombre: {vino.get('nombre')}")
    if vino.get("bodega"):
        partes.append(f"Bodega: {vino.get('bodega')}")
    if vino.get("tipo"):
        partes.append(f"Tipo: {vino.get('tipo')}")
    if vino.get("region") or vino.get("pais"):
        partes.append(f"Origen: {vino.get('region', '')} {vino.get('pais', '')}".strip())
    if vino.get("maridaje"):
        partes.append(f"Maridaje: {vino.get('maridaje')}")
    if vino.get("descripcion"):
        partes.append(f"Descripción: {(vino.get('descripcion') or '')[:300]}")
    if vino.get("notas_cata"):
        partes.append(f"Notas de cata: {(vino.get('notas_cata') or '')[:200]}")
    return "\n".join(partes) if partes else ""


def responder_sobre_vino(pregunta: str, vino: dict, perfil: str = "aficionado") -> str | None:
    """
    Responde como sumiller sobre un vino concreto (el que el usuario acaba de escanear).
    Si no hay API key o falla, devuelve None para usar la lógica rule-based.
    """
    client, types = _get_client()
    if not client or not types:
        return None
    contexto_vino = _vino_a_texto(vino)
    if not contexto_vino:
        return None
    perfil_instruccion = {
        "principiante": "Explica de forma sencilla, sin jerga. Si usas un término técnico, explícalo brevemente.",
        "aficionado": "Tono cercano y útil, con algún detalle técnico si aporta.",
        "profesional": "Puedes usar lenguaje más técnico (crianza, taninos, perfil).",
    }.get(perfil, "Tono cercano y útil.")
    prompt = f"""Eres un sumiller experto. El usuario tiene UN vino (la ficha de abajo) y hace una pregunta.

Ficha del vino (solo puedes usar esta información):
{contexto_vino}

Pregunta: {pregunta}

Reglas: Responde en español, en 2-4 frases. {perfil_instruccion}
- Usa SOLO datos de la ficha de arriba. Si la ficha no incluye algo (ej. precio, puntuación), di "No tenemos ese dato en la ficha" en lugar de inventar.
- No menciones otros vinos ni bodegas que no estén en la ficha. Sé amable y conciso."""
    try:
        response = client.models.generate_content(
            model=MODELO_SUMILLER,
            contents=[types.Part.from_text(text=prompt)],
            config=types.GenerateContentConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=TEMPERATURE,
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if not text and getattr(response, "candidates", None):
            c0 = response.candidates[0]
            if c0.content and c0.content.parts:
                text = (getattr(c0.content.parts[0], "text", None) or "").strip()
        return text if text else None
    except Exception as e:
        logger.warning("[SumillerGemini] Error en responder_sobre_vino: %s", e)
        return None


def reescribir_respuesta_sumiller(pregunta_usuario: str, respuesta_actual: str, perfil: str = "aficionado") -> str | None:
    """
    Reescribe la respuesta rule-based para que suene más natural y con vida.
    Mantiene el contenido (vinos recomendados, etc.) pero con tono de sumiller real.
    Si falla, devuelve None y se usa respuesta_actual.
    """
    client, types = _get_client()
    if not client or not types:
        return None
    if not (respuesta_actual or respuesta_actual.strip()):
        return None
    prompt = f"""Eres un sumiller experto. Reescribe la respuesta de abajo para que suene más natural y cercana, pero SIN CAMBIAR NINGÚN DATO: mismos vinos, mismas bodegas, mismos precios, misma información.

Pregunta del usuario: {pregunta_usuario}

Respuesta actual (copia la información exacta, solo mejora el tono y la redacción):
{respuesta_actual[:800]}

Reglas: Responde SOLO con la versión mejorada, en español, 2-5 frases. No añadas vinos ni datos que no estén en la respuesta actual. No uses prefijos como "Como sumiller..." o "Aquí tienes...". Directo al contenido."""
    try:
        response = client.models.generate_content(
            model=MODELO_SUMILLER,
            contents=[types.Part.from_text(text=prompt)],
            config=types.GenerateContentConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=TEMPERATURE,
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if not text and getattr(response, "candidates", None):
            c0 = response.candidates[0]
            if c0.content and c0.content.parts:
                text = (getattr(c0.content.parts[0], "text", None) or "").strip()
        return text if text else None
    except Exception as e:
        logger.warning("[SumillerGemini] Error en reescribir_respuesta: %s", e)
        return None
