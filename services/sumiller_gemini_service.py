"""
Sumiller con Gemini: respuestas en lenguaje natural (plan gratuito).
Usa la misma GOOGLE_API_KEY que el escáner y la traducción.

- Ahora (gratuito): gemini-2.0-flash — rápido y suficiente para dar vida al sumiller.
- Al monetizar: en Render → Variables → SUMILLER_AI_MODEL = gemini-1.5-pro (o gemini-2.5-pro)

Evidence Engine — Capa 3 con File Search:
  Cuando el vino no está en la base local, Gemini busca en el File Search Store
  (mitos_vino.json + conocimiento_vinos.json indexados) antes de responder.
  Las respuestas incluyen citas automáticas del documento fuente.
  Store: fileSearchStores/vinoproiaknowledge-pkm9r4c7564q
"""
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Plan gratuito: gemini-2.0-flash. Al monetizar: gemini-1.5-pro o gemini-2.5-pro
MODELO_SUMILLER = os.environ.get("SUMILLER_AI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"
MAX_OUTPUT_TOKENS = 380
# Temperatura baja para no inventar datos (0.3 con File Search = máxima fidelidad al documento)
TEMPERATURE = 0.5

# File Search Store — cargado desde config en data/
_FILE_SEARCH_STORE: str | None = None

def _get_file_search_store() -> str | None:
    """Devuelve el nombre del File Search Store si está configurado."""
    global _FILE_SEARCH_STORE
    if _FILE_SEARCH_STORE is not None:
        return _FILE_SEARCH_STORE or None
    config_path = Path(__file__).resolve().parent.parent / "data" / "file_search_config.json"
    if not config_path.is_file():
        _FILE_SEARCH_STORE = ""
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        store = (cfg.get("store_name") or "").strip()
        _FILE_SEARCH_STORE = store
        return store if store else None
    except Exception:
        _FILE_SEARCH_STORE = ""
        return None


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
    anada = vino.get("anada") or vino.get("añada") or vino.get("cosecha")
    if anada is not None and str(anada).strip():
        partes.append(f"Añada (edad/cosecha): {anada}")
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


def buscar_con_file_search(pregunta: str, perfil: str = "aficionado") -> str | None:
    """
    Evidence Engine — Capa 3 mejorada: busca en el File Search Store de Google
    (mitos_vino.json + conocimiento_vinos.json indexados).
    Gemini responde basándose SOLO en nuestros documentos verificados, con citas automáticas.
    Devuelve respuesta con fuente citada o None si falla / no hay store configurado.
    """
    store_name = _get_file_search_store()
    if not store_name:
        return None
    client, types = _get_client()
    if not client or not types:
        return None
    perfil_instruccion = {
        "principiante": "Explica de forma sencilla, sin jerga técnica.",
        "aficionado": "Tono cercano y útil, con algún detalle técnico si aporta.",
        "profesional": "Puedes usar lenguaje técnico enológico.",
    }.get(perfil, "Tono cercano y útil.")
    prompt = (
        f"Eres un sumiller experto en vinos. Responde la siguiente pregunta basándote "
        f"ÚNICAMENTE en los documentos del store (mitos_vino.json y conocimiento_vinos.json). "
        f"Si la pregunta toca un mito del vino, corrígelo educadamente con la realidad del documento. "
        f"Si hay datos técnicos (temperatura, guarda, clasificación), inclúyelos. "
        f"Responde en español, máximo 4 frases. {perfil_instruccion}\n\n"
        f"Pregunta: {pregunta}"
    )
    try:
        response = client.models.generate_content(
            model=MODELO_SUMILLER,
            contents=[types.Part.from_text(text=prompt)],
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )
                ],
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=0.3,
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if not text and getattr(response, "candidates", None):
            c0 = response.candidates[0]
            if c0.content and c0.content.parts:
                text = (getattr(c0.content.parts[0], "text", None) or "").strip()
        if not text:
            return None
        # Extraer citas si las hay
        citas = []
        try:
            for candidate in (getattr(response, "candidates", None) or []):
                for part in (getattr(candidate.content, "parts", None) or []):
                    for ref in (getattr(part, "file_search_results", None) or []):
                        nombre_doc = getattr(ref, "display_name", None) or getattr(ref, "name", "")
                        if nombre_doc:
                            citas.append(nombre_doc)
        except Exception:
            pass
        if citas:
            citas_unicas = list(dict.fromkeys(citas))
            texto_cita = ", ".join(citas_unicas)
            text = text + f"\n\n📄 Fuente verificada: {texto_cita}"
        return text
    except Exception as e:
        logger.warning("[SumillerGemini] Error en buscar_con_file_search: %s", e)
        return None


def buscar_vino_en_nube(pregunta_o_nombre: str, perfil: str = "aficionado") -> tuple[str | None, dict | None]:
    """
    Busca un vino en la nube cuando no está en la base local.
    Evidence Engine — Capa 3:
      Intenta primero File Search (documentos verificados con citas).
      Si no hay store o falla, usa Gemini libre marcado con [Estimación IA].
    Devuelve (respuesta_texto, vino_dict).
    - respuesta_texto: respuesta del sumiller en español (2-4 frases).
    - vino_dict: ficha del vino para guardar en BD local (nombre, bodega, tipo, etc.) o None si Gemini no pudo identificar el vino.
    Si no hay API key o falla, devuelve (None, None).
    """
    client, types = _get_client()
    if not client or not types:
        return None, None
    texto = (pregunta_o_nombre or "").strip()
    if not texto:
        return None, None

    # Intentar primero con File Search (documentos verificados, con citas)
    respuesta_file_search = buscar_con_file_search(texto, perfil=perfil)
    if respuesta_file_search:
        logger.info("[SumillerGemini] Respondido desde File Search Store")
        return respuesta_file_search, None

    # Fallback: Gemini libre marcado como [Estimación IA]
    perfil_instruccion = {
        "principiante": "Explica de forma sencilla.",
        "aficionado": "Tono cercano y útil.",
        "profesional": "Puedes usar lenguaje técnico.",
    }.get(perfil, "Tono cercano y útil.")
    prompt = f"""El usuario pregunta sobre un vino que podría no estar en nuestra base de datos local. Usa tu conocimiento para:
1) Dar una respuesta breve de sumiller (2-4 frases) en español. {perfil_instruccion}
2) Si identificas el vino con claridad, añade al final una línea que empiece exactamente con VINO_JSON= y después un JSON válido (sin saltos de línea dentro) con estas claves: nombre, bodega, anada (año de cosecha, 4 dígitos, ej. 2019; muy importante para no confundir distintas añadas del mismo vino), tipo, region, pais, maridaje, descripcion, notas_cata, precio_estimado. Usa strings salvo anada que puede ser número; si no conoces un campo, usa "".
Si no puedes identificar el vino, responde solo con la respuesta de sumiller y no pongas VINO_JSON.

Pregunta o nombre del vino: {texto}"""
    try:
        response = client.models.generate_content(
            model=MODELO_SUMILLER,
            contents=[types.Part.from_text(text=prompt)],
            config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=TEMPERATURE,
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if not text and getattr(response, "candidates", None):
            c0 = response.candidates[0]
            if c0.content and c0.content.parts:
                text = (getattr(c0.content.parts[0], "text", None) or "").strip()
        if not text:
            return None, None
        respuesta = text
        vino = None
        if "VINO_JSON=" in text:
            try:
                idx = text.index("VINO_JSON=") + len("VINO_JSON=")
                raw_line = text[idx:].strip().split("\n")[0].strip()
                # Extraer JSON aunque Gemini añada texto o markdown: primer { hasta último }
                start = raw_line.find("{")
                end = raw_line.rfind("}")
                if start != -1 and end != -1 and end > start:
                    json_str = raw_line[start : end + 1]
                else:
                    json_str = raw_line
                vino = json.loads(json_str)
                if isinstance(vino, dict) and (vino.get("nombre") or vino.get("bodega")):
                    respuesta = text[:text.index("VINO_JSON=")].strip()
                else:
                    vino = None
            except (json.JSONDecodeError, ValueError):
                pass
        # Evidence Engine — Capa 3: marcar SOLO la respuesta visible, nunca el bloque VINO_JSON
        if respuesta and not respuesta.startswith("[Estimación IA]"):
            respuesta = "[Estimación IA] " + respuesta
        return respuesta, vino
    except Exception as e:
        logger.warning("[SumillerGemini] Error en buscar_vino_en_nube: %s", e)
        return None, None


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
