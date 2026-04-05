"""
Endpoints de escaneo de etiquetas y registro de vinos.
"""
import asyncio
import difflib
import json
import logging
import os
import re
import uuid
from urllib.parse import quote

logger = logging.getLogger(__name__)


def _es_solo_codigo_barras(texto: str) -> bool:
    """True si el texto son solo dígitos y tiene 8-14 caracteres (EAN/GTIN)."""
    if not texto or not isinstance(texto, str):
        return False
    limpio = re.sub(r"\D", "", texto.strip())
    return 8 <= len(limpio) <= 14


def _normalizar_ean_texto(texto: str) -> str:
    """Extrae solo dígitos para EAN (8-14) desde un texto de búsqueda."""
    if not texto:
        return ""
    limpio = re.sub(r"\D", "", texto.strip())
    if 8 <= len(limpio) <= 14:
        return limpio
    return limpio[:14] if len(limpio) > 14 else limpio


def _extraer_ean_de_url_o_texto(texto: str) -> str | None:
    """
    Extrae un código EAN/GTIN (8-14 dígitos) de una URL o texto.
    Ej.: https://id.aecocescanqr.es/01/08437018575046/22/2024 -> 08437018575046
    """
    if not texto or not isinstance(texto, str):
        return None
    # Buscar secuencias de 8 a 14 dígitos (EAN-8, EAN-13, GTIN-14)
    for m in re.finditer(r"\d{8,14}", texto):
        s = m.group(0)
        if 8 <= len(s) <= 14:
            return s
    return None


from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from services.busqueda_service import buscar_vinos_avanzado, buscar_por_codigo_barras_bd, buscar_por_entidades
from services.ocr_service import extraer_texto_de_imagen, extraer_datos_etiqueta_doble_capa, TesseractNoDisponibleError
from services.api_externa_service import buscar_por_texto, buscar_por_codigo_barras, get_informacion_extendida_por_barcode
from services.ocr_normalizer import limpiar as normalizar_ocr
from services.codigos_service import extraer_primer_ean_de_imagen
from services.wine_label_api4ai_service import recognize_wine_from_image
from services.entity_extractor import extraer_entidades, formatear_entidades_para_json
from services.image_quality_service import evaluar_calidad_imagen, mensaje_calidad_imagen

router = APIRouter(prefix="", tags=["Escaneo"])

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
REGISTRADOS_PATH = os.path.join(DATA_FOLDER, "registrados.json")
ESCANEO_MAX_CONCURRENT = max(1, int(os.environ.get("ESCANEO_MAX_CONCURRENT", "4") or "4"))
ESCANEO_SEMAPHORE = asyncio.Semaphore(ESCANEO_MAX_CONCURRENT)
API4AI_HINTS_ENABLED = os.environ.get("ENABLE_API4AI_SCAN_HINTS", "").strip().lower() in {"1", "true", "yes"}


# Palabras que no llevamos a la query corta para OFF (solo las más cortas/ruido)
_STOP_QUERY = frozenset({"de", "del", "la", "el", "en", "y", "con", "por", "para", "al", "una", "un", "los", "las", "producto", "denominacion", "origen", "españa", "espana"})


def _extraer_query_corta(texto: str, max_palabras: int = 4) -> str:
    """Extrae pocas palabras clave para una segunda búsqueda externa (OFF responde mejor a queries cortas)."""
    if not texto or not isinstance(texto, str):
        return ""
    t = texto.lower().strip()
    t = re.sub(r"[^a-z0-9áéíóúüñ\s]+", " ", t)
    palabras = [p for p in t.split() if len(p) > 2 and p not in _STOP_QUERY]
    return " ".join(palabras[:max_palabras]) if palabras else texto[:50].strip()


def _slug(key: str) -> str:
    """Genera una clave slug a partir de un nombre o key."""
    key = (key or "").lower().strip()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    key = key.strip("_")
    return key or "vino_registrado"


def _get_vinos(request: Request) -> dict:
    """Obtiene el diccionario de vinos desde el estado de la app."""
    return getattr(request.app.state, "vinos_mundiales", {})


def _get_consultas(request: Request) -> dict:
    """Obtiene el almacén de consultas de escaneo (consulta_id -> vino)."""
    if not hasattr(request.app.state, "consultas_escaneo"):
        request.app.state.consultas_escaneo = {}
    return request.app.state.consultas_escaneo


def _es_pro(session_id: str | None) -> bool:
    if not session_id or not session_id.strip():
        return False
    try:
        from services import freemium_service as freemium_svc
        return freemium_svc.is_pro(session_id.strip())
    except Exception:
        return False


def _es_texto_poco_claro(texto: str) -> bool:
    """
    True si el texto extraído (p. ej. por OCR) es demasiado corto o no parece
    un nombre de vino (sin letras). Así no inventamos resultado y devolvemos
    "No se pudo identificar la etiqueta con claridad".
    """
    t = (texto or "").strip()
    if len(t) < 3:
        return True
    # Que tenga al menos una letra (incl. acentos y ñ)
    if not re.search(r"[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]", t):
        return True
    return False


def _normalizar_para_coincidencia(t: str) -> str:
    """Normaliza para comparación: minúsculas, sin signos raros, espacios colapsados."""
    if not t or not isinstance(t, str):
        return ""
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9áéíóúüñçàèìòù ]+", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# Palabras genéricas que no aportan señal de identidad al comparar OCR con nombre de vino
_PALABRAS_GENERICAS_VINO = {
    "vino", "crianza", "reserva", "gran", "tinto", "blanco", "rosado", "espumoso",
    "seleccion", "especial", "edicion", "limitada", "premium", "classic", "clasico",
    "aged", "barrel", "oak", "roble", "barrica", "cosecha", "vendimia",
}


def _coincidencia_fiable(texto_busqueda: str, nombre_vino: str, bodega_vino: str | None = None) -> bool:
    """
    True si estamos seguros de que el texto de búsqueda se refiere a ESE vino.
    Estrategia en 4 niveles (del más al menos restrictivo):
      1. Un token muy distintivo (≥6 letras, no genérico) aparece en ambos lados.
      2. Contención directa (uno contiene al otro).
      3. La bodega en el texto confirma la bodega del vino.
      4. Al menos 2 tokens no genéricos coinciden en nombre+bodega.
    """
    if not nombre_vino or not isinstance(nombre_vino, str):
        return False
    busq = _normalizar_para_coincidencia(texto_busqueda)
    nombre = _normalizar_para_coincidencia(nombre_vino)
    bodega = _normalizar_para_coincidencia(bodega_vino or "") if bodega_vino else ""
    if not busq:
        return False

    # Nivel 1: token muy distintivo (largo y no genérico) en ambos lados
    tokens_busq = [
        t for t in busq.split()
        if len(t) >= 5 and not t.isdigit() and t not in _PALABRAS_GENERICAS_VINO
    ]
    tokens_objetivo = set((nombre + " " + bodega).split())
    for t in tokens_busq:
        if t in tokens_objetivo:
            return True
        # Fuzzy para tokens largos: "sassicaia" vs "sassicaia" (typos leves)
        for to in tokens_objetivo:
            if len(to) >= 5 and difflib.SequenceMatcher(None, t, to).ratio() >= 0.88:
                return True

    # Nivel 2: contención directa (nombre completo dentro del texto o al revés)
    if nombre and (busq in nombre or nombre in busq):
        return True

    # Nivel 3: la bodega en el texto confirma el vino (ej. "Pérez Pascuas" → Viña Pedrosa)
    if bodega:
        tokens_bodega = [t for t in bodega.split() if len(t) >= 4 and t not in _PALABRAS_GENERICAS_VINO]
        coinciden_bodega = sum(1 for t in tokens_bodega if t in busq)
        if coinciden_bodega >= 2 or (len(tokens_bodega) == 1 and tokens_bodega and tokens_bodega[0] in busq):
            return True

    # Nivel 4: al menos 2 tokens no genéricos (≥3 letras) coinciden en nombre+bodega
    tokens_busq_general = [
        t for t in busq.split()
        if len(t) > 2 and not t.isdigit() and t not in _PALABRAS_GENERICAS_VINO
    ]
    coinciden = sum(1 for t in tokens_busq_general if t in tokens_objetivo)
    return coinciden >= 2


def _guardar_vino_consulta(request: Request, vino: dict) -> str | None:
    """
    Guarda en registrados.json un vino obtenido por consulta (OFF o código barras)
    para que futuras búsquedas lo encuentren. Devuelve la key asignada o None si no se guardó.
    No guarda vinos genéricos (_origen == 'generico').
    """
    if not vino or vino.get("_origen") == "generico":
        return None
    nombre = (vino.get("nombre") or "").strip()
    if not nombre or len(nombre) < 2:
        return None
    key = _slug(nombre)
    vino_limpio = {
        "nombre": nombre[:200],
        "bodega": (vino.get("bodega") or "No especificada").strip()[:200],
        "region": (vino.get("region") or "Por determinar").strip()[:150],
        "pais": (vino.get("pais") or "Desconocido").strip()[:100],
        "tipo": (vino.get("tipo") or "tinto").strip().lower()[:50] or "tinto",
        "puntuacion": vino.get("puntuacion"),
        "precio_estimado": (vino.get("precio_estimado") or "").strip() or None,
        "descripcion": (vino.get("descripcion") or "").strip()[:2000] or "Vino añadido desde consulta.",
        "notas_cata": (vino.get("notas_cata") or "").strip()[:2000] or "No disponibles.",
        "maridaje": (vino.get("maridaje") or "").strip()[:1000] or "Información no disponible.",
    }
    registrados = {}
    if os.path.exists(REGISTRADOS_PATH):
        try:
            with open(REGISTRADOS_PATH, "r", encoding="utf-8") as f:
                registrados = json.load(f)
        except Exception:
            registrados = {}
    base_key = key
    contador = 1
    while key in registrados:
        key = f"{base_key}_{contador}"
        contador += 1
    registrados[key] = vino_limpio
    try:
        os.makedirs(DATA_FOLDER, exist_ok=True)
        with open(REGISTRADOS_PATH, "w", encoding="utf-8") as f:
            json.dump(registrados, f, ensure_ascii=False, indent=2)
    except Exception:
        return None
    vinos = _get_vinos(request)
    vinos[key] = vino_limpio
    return key


def _push_historial(request: Request, session_id: str | None, consulta_id: str, vino_nombre: str, encontrado_en_bd: bool) -> None:
    if not session_id or not session_id.strip():
        return
    hist = getattr(request.app.state, "historial_escaneos", None)
    if hist is None:
        request.app.state.historial_escaneos = {}
        hist = request.app.state.historial_escaneos
    if session_id not in hist:
        hist[session_id] = []
    hist[session_id].append({
        "consulta_id": consulta_id,
        "vino_nombre": (vino_nombre or "")[:200],
        "encontrado_en_bd": encontrado_en_bd,
    })
    hist[session_id] = hist[session_id][-50:]


def _obtener_entidades_extraidas(texto: str | None, vino: dict | None = None, entidades_override: dict | None = None) -> dict:
    """
    Extrae entidades (bodega, añada, denominacion_origen, variedad) del texto OCR,
    del vino, o usa las ya extraídas (doble capa / visión).
    Siempre devuelve un dict para incluir en entidades_extraidas.
    """
    if entidades_override:
        from services.data_refinement import entidades_para_json
        return entidades_para_json(entidades_override)
    if texto and len(texto.strip()) >= 2:
        ent = extraer_entidades(texto)
        return formatear_entidades_para_json(ent)
    if vino:
        out = {}
        if vino.get("nombre") and vino.get("nombre") not in ("vino escaneado", "No especificada"):
            out["nombre"] = str(vino["nombre"]).strip()[:120]
        if vino.get("bodega") and vino.get("bodega") != "No especificada":
            out["bodega"] = str(vino["bodega"]).strip()[:200]
        if vino.get("region") and vino.get("region") != "Por determinar":
            out["denominacion_origen"] = str(vino["region"]).strip()[:150]
        if vino.get("uva_principal"):
            out["variedad"] = str(vino["uva_principal"]).strip()[:80]
        # Añada: intentar extraer de descripcion o nombre si hay año
        m = re.search(r"\b(19[5-9]\d|20[0-3]\d)\b", (vino.get("descripcion") or "") + " " + (vino.get("nombre") or ""))
        if m:
            out["añada"] = int(m.group(1))
        return out
    return {}


def _detail_escanear(falta: str) -> str:
    """Mensaje de error claro cuando faltan datos en POST /escanear."""
    return (
        "Debe enviar al menos uno de estos datos para escanear: "
        '"texto", "imagen" (archivo) o "codigo_barras". '
        "Formato aceptado: multipart/form-data (formulario) con campos texto, imagen y/o codigo_barras; "
        "o JSON con { \"texto\": \"...\" } y/o { \"codigo_barras\": \"...\" }. "
        "Falta: " + falta
    )


def _respuesta_servicio_ocupado(session_id: str | None) -> dict:
    return {
        "reconocido": False,
        "error_imagen": False,
        "es_pro": _es_pro(session_id),
        "mensaje": "Estamos procesando muchos escaneos a la vez. Prueba de nuevo en unos segundos o escribe el nombre del vino manualmente.",
        "entidades_extraidas": {},
    }


@router.post("/escanear")
async def escanear_etiqueta(
    request: Request,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Escanea una etiqueta de vino por imagen y/o texto. Identifica vinos en local o en línea.

    Flujo (los ojos del experto en vinos — una foto, varias señales):
    1. Imagen: se intenta leer código de barras y QR en la misma foto (pyzbar). Si hay EAN y OFF devuelve vino, se responde al momento.
    2. Código de barras en formulario: si el cliente envía codigo_barras, búsqueda en OFF.
    3. OCR + normalizador sobre la imagen (texto de la etiqueta).
    4. BD local (899 vinos): score >= 5 y coincidencia fiable (o marca Protos/Pedrosa) -> vino local.
    5. Fuente externa (OFF) por texto; reintento con query corta si hace falta.
    6. Si nada cuadra: mensaje genérico + "recomendar similar".
    El endpoint siempre responde 200 con una estructura válida; los fallos de red o externos no se trasladan al usuario.

    Acepta: multipart/form-data (texto, imagen, codigo_barras) o JSON (texto, codigo_barras).
    """
    try:
        try:
            await asyncio.wait_for(ESCANEO_SEMAPHORE.acquire(), timeout=0.25)
        except asyncio.TimeoutError:
            logger.warning("[ESCANEAR] Saturación: sin slot libre de escaneo.")
            return _respuesta_servicio_ocupado(x_session_id)
        try:
            return await _escanear_etiqueta_impl(request, x_session_id)
        finally:
            ESCANEO_SEMAPHORE.release()
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("[ESCANEAR] Error inesperado (respuesta genérica): %s", e)
        vinos = _get_vinos(request)
        consultas = _get_consultas(request)
        sid = (x_session_id or "").strip()
        es_pro = _es_pro(sid)
        consulta_id = str(uuid.uuid4())
        nombre_busqueda = "vino escaneado"
        vino_gen = {
            "nombre": nombre_busqueda,
            "bodega": "No especificada",
            "region": "Por determinar",
            "pais": "Información no especificada",
            "tipo": "tinto",
            "puntuacion": None,
            "precio_estimado": None,
            "descripcion": "No pudimos identificar la etiqueta con seguridad. Puedes preguntar al experto en vinos por un vino similar o añadirlo manualmente.",
            "notas_cata": "No disponibles.",
            "maridaje": "Información no disponible.",
            "_origen": "generico",
        }
        consultas[consulta_id] = {"vino": vino_gen, "key": None}
        _push_historial(request, sid, consulta_id, nombre_busqueda, False)
        return {
            "encontrado_en_bd": False,
            "consulta_id": consulta_id,
            "vino": vino_gen,
            "vino_key": _slug(nombre_busqueda),
            "mostrar_boton_comprar": False,
            "recomendar_similar": True,
            "mensaje": "No pudimos identificar este vino. ¿Quieres que te recomiende algo similar?",
            "es_pro": es_pro,
            "entidades_extraidas": {},
        }


async def _escanear_etiqueta_impl(request: Request, x_session_id: str | None):
    """Implementación del flujo de escaneo (separada para capturar errores y devolver siempre 200)."""
    vinos = _get_vinos(request)
    consultas = _get_consultas(request)
    entidades_imagen = None  # Del flujo doble capa (OCR + visión) cuando hay imagen
    error_vision_imagen = None  # Error específico si falla la IA de visión
    calidad_imagen = None

    contenido_tipo = (request.headers.get("content-type") or "").lower()
    texto = None
    codigo_barras = None
    imagen = None

    if "application/json" in contenido_tipo:
        try:
            body = await request.json()
            if isinstance(body, dict):
                texto = (body.get("texto") or "").strip() or None
                codigo_barras = (body.get("codigo_barras") or "").strip() or None
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Cuerpo JSON inválido. Use { \"texto\": \"...\" } y/o { \"codigo_barras\": \"...\" }.",
            )
    else:
        form = await request.form()
        texto = (form.get("texto") or "").strip() or None
        codigo_barras = (form.get("codigo_barras") or "").strip() or None
        imagen = form.get("imagen")
        if imagen and getattr(imagen, "filename", None) and not imagen.filename:
            imagen = None

    texto_busqueda = (texto or "").strip()

    imagen_enviada = False
    contenido_imagen = None
    if imagen and getattr(imagen, "read", None):
        try:
            contenido_imagen = await imagen.read()
            if contenido_imagen:
                imagen_enviada = True
                calidad_imagen = evaluar_calidad_imagen(contenido_imagen)
                mensaje_calidad = mensaje_calidad_imagen(calidad_imagen)
                if calidad_imagen and "imagen_invalida" in (calidad_imagen.get("motivos") or []):
                    return {
                        "reconocido": False,
                        "error_imagen": True,
                        "es_pro": _es_pro((x_session_id or "").strip()),
                        "mensaje": mensaje_calidad or "La imagen no se pudo procesar. Prueba con otra foto.",
                        "entidades_extraidas": {},
                        "diagnostico_imagen": calidad_imagen,
                    }
                # Imagen borrosa: NO abortamos, dejamos que API4AI + Gemini Vision lo intenten.
                # Solo guardamos el aviso para añadirlo al mensaje final si tampoco identifican el vino.
                _imagen_borrosa_sin_texto = (
                    calidad_imagen and "borrosa" in (calidad_imagen.get("motivos") or [])
                    and not texto_busqueda and not codigo_barras
                )
                # 1) Códigos de barras / QR en la imagen (prioridad: identificación inequívoca)
                ean_imagen = extraer_primer_ean_de_imagen(contenido_imagen)
                if ean_imagen:
                    logger.info("[ESCANEAR] Código de barras/QR detectado en imagen: %s", ean_imagen[:20])
                    vino_por_codigo = buscar_por_codigo_barras(ean_imagen)
                    if vino_por_codigo:
                        consulta_id = str(uuid.uuid4())
                        key_guardada = _guardar_vino_consulta(request, vino_por_codigo)
                        consultas[consulta_id] = {"vino": vino_por_codigo, "key": key_guardada}
                        try:
                            from services import analytics_service
                            analytics_service.registrar_escaneo(False, vino_por_codigo.get("nombre"), vino_por_codigo.get("pais"))
                        except Exception:
                            pass
                        _push_historial(request, (x_session_id or "").strip(), consulta_id, vino_por_codigo.get("nombre"), False)
                        nombre_slug = key_guardada or _slug(vino_por_codigo.get("nombre") or "")
                        return {
                            "encontrado_en_bd": False,
                            "consulta_id": consulta_id,
                            "vino": vino_por_codigo,
                            "vino_key": nombre_slug or None,
                            "mostrar_boton_comprar": True,
                            "mensaje": "Identificado por código de barras. Este vino no está en nuestra base; te mostramos la ficha externa. ¿Quieres una recomendación similar de nuestra carta?",
                            "es_pro": _es_pro((x_session_id or "").strip()),
                            "entidades_extraidas": _obtener_entidades_extraidas(None, vino_por_codigo),
                        }
                # 1b) Doble capa: OCR local + fallback IA visión (Gemini 2.0 Flash)
                resultado_doble = extraer_datos_etiqueta_doble_capa(
                    contenido_imagen,
                    session_key=(x_session_id or "").strip() or None,
                )
                texto_ocr = (resultado_doble.get("texto") or "").strip()
                entidades_imagen = resultado_doble.get("entidades")
                error_vision_imagen = resultado_doble.get("error_vision")
                calidad_imagen = resultado_doble.get("calidad_imagen") or calidad_imagen
                if texto_ocr:
                    texto_busqueda = f"{texto_busqueda} {texto_ocr}".strip()
                if texto_busqueda:
                    texto_limpio_early = normalizar_ocr(texto_busqueda)
                    texto_para_early = (texto_limpio_early or texto_busqueda).strip()
                    if len(texto_para_early) >= 2:
                        coincidencias_early = buscar_vinos_avanzado(vinos, texto_para_early, limite=5)
                        if coincidencias_early and coincidencias_early[0]["score"] >= 5.0:
                            mejor_early = coincidencias_early[0]
                            vino_early = mejor_early.get("vino")
                            if isinstance(vino_early, dict):
                                nombre_early = (vino_early.get("nombre") or "").strip()
                                bodega_early = (vino_early.get("bodega") or "").strip()
                                if _coincidencia_fiable(texto_para_early, nombre_early, bodega_early):
                                    logger.info("[ESCANEAR] Encontrado en BD por OCR de etiqueta (antes que IA): %s", nombre_early[:60])
                                    consulta_id = str(uuid.uuid4())
                                    consultas[consulta_id] = {"vino": vino_early, "key": mejor_early["key"]}
                                    try:
                                        from services import analytics_service
                                        analytics_service.registrar_escaneo(True, vino_early.get("nombre"), vino_early.get("pais"))
                                    except Exception:
                                        pass
                                    _push_historial(request, (x_session_id or "").strip(), consulta_id, vino_early.get("nombre"), True)
                                    return {
                                        "encontrado_en_bd": True,
                                        "consulta_id": consulta_id,
                                        "key": mejor_early["key"],
                                        "vino_key": mejor_early["key"],
                                        "mostrar_boton_comprar": True,
                                        "vino": vino_early,
                                        "mensaje": "Encontrado en nuestra base de datos (etiqueta leída correctamente).",
                                        "es_pro": _es_pro((x_session_id or "").strip()),
                                        "entidades_extraidas": _obtener_entidades_extraidas(texto_para_early, entidades_override=entidades_imagen),
                                    }
                # 2) API4AI Wine Recognition: usa el nombre identificado en la búsqueda real
                sugerencias_ia = recognize_wine_from_image(contenido_imagen)
                if sugerencias_ia and sugerencias_ia[0].get("confidence", 0) >= 0.5:
                    nombre_ia = (sugerencias_ia[0].get("name") or "").strip()
                    confianza_ia = float(sugerencias_ia[0].get("confidence") or 0)
                    if nombre_ia:
                        logger.info("[ESCANEAR] API4AI identificó '%s' con confianza %.2f", nombre_ia[:50], confianza_ia)
                        # Buscar directamente en BD con el nombre que dio API4AI
                        texto_api4ai_norm = normalizar_ocr(nombre_ia)
                        if len(texto_api4ai_norm) >= 3:
                            coincidencias_api4ai = buscar_vinos_avanzado(vinos, texto_api4ai_norm, limite=3)
                            if coincidencias_api4ai and coincidencias_api4ai[0]["score"] >= 4.0:
                                mejor_api4ai = coincidencias_api4ai[0]
                                vino_api4ai = mejor_api4ai.get("vino")
                                if isinstance(vino_api4ai, dict):
                                    nombre_found = (vino_api4ai.get("nombre") or "").strip()
                                    bodega_found = (vino_api4ai.get("bodega") or "").strip()
                                    if _coincidencia_fiable(texto_api4ai_norm, nombre_found, bodega_found):
                                        logger.info("[ESCANEAR] API4AI encontró en BD: %s", nombre_found[:60])
                                        consulta_id = str(uuid.uuid4())
                                        consultas[consulta_id] = {"vino": vino_api4ai, "key": mejor_api4ai["key"]}
                                        try:
                                            from services import analytics_service
                                            analytics_service.registrar_escaneo(True, vino_api4ai.get("nombre"), vino_api4ai.get("pais"))
                                        except Exception:
                                            pass
                                        _push_historial(request, (x_session_id or "").strip(), consulta_id, vino_api4ai.get("nombre"), True)
                                        return {
                                            "encontrado_en_bd": True,
                                            "consulta_id": consulta_id,
                                            "key": mejor_api4ai["key"],
                                            "vino_key": mejor_api4ai["key"],
                                            "mostrar_boton_comprar": True,
                                            "vino": vino_api4ai,
                                            "mensaje": "Identificado por reconocimiento visual de etiqueta.",
                                            "es_pro": _es_pro((x_session_id or "").strip()),
                                            "entidades_extraidas": _obtener_entidades_extraidas(texto_api4ai_norm, entidades_override=entidades_imagen),
                                        }
                        # Si no encontró en BD, añadir el nombre al texto de búsqueda para el resto del pipeline
                        if confianza_ia >= 0.7:
                            # Alta confianza: nombre API4AI va primero (más fiable que OCR ruidoso)
                            texto_busqueda = f"{nombre_ia} {texto_busqueda}".strip()
                        else:
                            # Confianza media: añadir como pista adicional al final
                            texto_busqueda = f"{texto_busqueda} {nombre_ia}".strip()
                # OCR ya hecho arriba (1b) para priorizar nuestra BD (Viña Pedrosa, etc.)
        except Exception:
            imagen_enviada = True

    sid = (x_session_id or "").strip()
    es_pro = _es_pro(sid)

    if codigo_barras and not texto_busqueda:
        vino_externo = buscar_por_codigo_barras(codigo_barras)
        if vino_externo:
            consulta_id = str(uuid.uuid4())
            key_guardada = _guardar_vino_consulta(request, vino_externo)
            consultas[consulta_id] = {"vino": vino_externo, "key": key_guardada}
            try:
                from services import analytics_service
                analytics_service.registrar_escaneo(False, vino_externo.get("nombre"), vino_externo.get("pais"))
            except Exception:
                pass
            _push_historial(request, sid, consulta_id, vino_externo.get("nombre"), False)
            nombre_slug = key_guardada or _slug(vino_externo.get("nombre") or "")
            return {
                "encontrado_en_bd": False,
                "consulta_id": consulta_id,
                "vino": vino_externo,
                "vino_key": nombre_slug or None,
                "mostrar_boton_comprar": True,
                "mensaje": "Este vino no está en nuestra base de datos. Te mostramos información externa; ya lo hemos guardado. ¿Quieres que te recomiende algo similar de nuestra base?",
                "es_pro": es_pro,
                "entidades_extraidas": _obtener_entidades_extraidas(None, vino_externo),
            }
        texto_busqueda = codigo_barras

    if not texto_busqueda:
        if imagen_enviada:
            logger.info("[ESCANEAR] No se extrajo texto de la imagen.")
            _borrosa = locals().get("_imagen_borrosa_sin_texto", False)
            mensaje_error = (
                error_vision_imagen
                if error_vision_imagen
                else (
                    "La foto está borrosa y no pudimos identificar el vino. Prueba acercándote más a la etiqueta o escribe el nombre del vino abajo."
                    if _borrosa
                    else "No pudimos leer la etiqueta. ¿Es una botella de vino? Prueba con otra foto más nítida o escribe el nombre del vino abajo."
                )
            )
            return {
                "reconocido": False,
                "error_imagen": True,
                "es_pro": es_pro,
                "mensaje": mensaje_error,
                "entidades_extraidas": {},
                "diagnostico_imagen": calidad_imagen or {},
            }
        raise HTTPException(
            status_code=400,
            detail=_detail_escanear("texto, imagen o codigo_barras"),
        )

    logger.info("[ESCANEAR] Texto búsqueda (OCR/input): %s", texto_busqueda[:200] if texto_busqueda else "(vacío)")

    # Si el input es solo un código de barras (ej. 8420523332655), buscar PRIMERO en nuestra BD, luego en OFF
    if _es_solo_codigo_barras(texto_busqueda):
        ean = _normalizar_ean_texto(texto_busqueda)
        # 1) Nuestra BD: si el vino tiene campo 'ean' o 'codigo_barras', lo encontramos aquí
        resultado_bd = buscar_por_codigo_barras_bd(vinos, ean)
        if resultado_bd:
            vino = resultado_bd["vino"]
            key = resultado_bd["key"]
            logger.info("[ESCANEAR] Código %s encontrado en BD local: %s", ean[:16], (vino.get("nombre") or "")[:60])
            consulta_id = str(uuid.uuid4())
            consultas[consulta_id] = {"vino": vino, "key": key}
            try:
                from services import analytics_service
                analytics_service.registrar_escaneo(True, vino.get("nombre"), vino.get("pais"))
            except Exception:
                pass
            _push_historial(request, sid, consulta_id, vino.get("nombre"), True)
            info_ext = get_informacion_extendida_por_barcode(ean)
            return {
                "encontrado_en_bd": True,
                "consulta_id": consulta_id,
                "key": key,
                "vino_key": key,
                "mostrar_boton_comprar": True,
                "vino": vino,
                "mensaje": "Encontrado en nuestra base de datos por código de barras.",
                "es_pro": es_pro,
                "entidades_extraidas": _obtener_entidades_extraidas(None, vino),
                "informacion_extendida": info_ext if info_ext else None,
                "informacion_extendida_no_disponible": info_ext is None,
            }
        logger.info("[ESCANEAR] Input detectado como código de barras (%s), buscando en Open Food Facts...", ean[:16])
        vino_por_ean = buscar_por_codigo_barras(ean)
        if vino_por_ean:
            consulta_id = str(uuid.uuid4())
            key_guardada = _guardar_vino_consulta(request, vino_por_ean)
            consultas[consulta_id] = {"vino": vino_por_ean, "key": key_guardada}
            try:
                from services import analytics_service
                analytics_service.registrar_escaneo(False, vino_por_ean.get("nombre"), vino_por_ean.get("pais"))
            except Exception:
                pass
            _push_historial(request, sid, consulta_id, vino_por_ean.get("nombre"), False)
            nombre_slug = key_guardada or _slug(vino_por_ean.get("nombre") or "")
            return {
                "encontrado_en_bd": False,
                "consulta_id": consulta_id,
                "vino": vino_por_ean,
                "vino_key": nombre_slug or None,
                "mostrar_boton_comprar": True,
                "mensaje": "Identificado por código de barras. ¿Quieres una recomendación similar de nuestra carta?",
                "es_pro": es_pro,
                "entidades_extraidas": _obtener_entidades_extraidas(None, vino_por_ean),
            }
        logger.info("[ESCANEAR] Open Food Facts sin resultado para código %s (no está en la base externa o timeout).", ean[:16])

    # Si el texto es una URL (ej. QR AECOC) o contiene un código de barras, extraerlo y buscar en BD y OFF
    ean_extraido = _extraer_ean_de_url_o_texto(texto_busqueda)
    if ean_extraido and not _es_solo_codigo_barras(texto_busqueda):
        # 1) Nuestra BD por código
        resultado_bd = buscar_por_codigo_barras_bd(vinos, ean_extraido)
        if resultado_bd:
            vino = resultado_bd["vino"]
            key = resultado_bd["key"]
            logger.info("[ESCANEAR] Código extraído %s encontrado en BD local: %s", ean_extraido[:16], (vino.get("nombre") or "")[:60])
            consulta_id = str(uuid.uuid4())
            consultas[consulta_id] = {"vino": vino, "key": key}
            try:
                from services import analytics_service
                analytics_service.registrar_escaneo(True, vino.get("nombre"), vino.get("pais"))
            except Exception:
                pass
            _push_historial(request, sid, consulta_id, vino.get("nombre"), True)
            info_ext = get_informacion_extendida_por_barcode(ean_extraido)
            return {
                "encontrado_en_bd": True,
                "consulta_id": consulta_id,
                "key": key,
                "vino_key": key,
                "mostrar_boton_comprar": True,
                "vino": vino,
                "mensaje": "Encontrado en nuestra base por código del QR.",
                "es_pro": es_pro,
                "entidades_extraidas": _obtener_entidades_extraidas(texto_busqueda, vino),
                "informacion_extendida": info_ext if info_ext else None,
                "informacion_extendida_no_disponible": info_ext is None,
            }
        logger.info("[ESCANEAR] Código extraído de URL/texto: %s, buscando en Open Food Facts...", ean_extraido[:16])
        vino_por_ean = buscar_por_codigo_barras(ean_extraido)
        if vino_por_ean:
            consulta_id = str(uuid.uuid4())
            key_guardada = _guardar_vino_consulta(request, vino_por_ean)
            consultas[consulta_id] = {"vino": vino_por_ean, "key": key_guardada}
            try:
                from services import analytics_service
                analytics_service.registrar_escaneo(False, vino_por_ean.get("nombre"), vino_por_ean.get("pais"))
            except Exception:
                pass
            _push_historial(request, sid, consulta_id, vino_por_ean.get("nombre"), False)
            nombre_slug = key_guardada or _slug(vino_por_ean.get("nombre") or "")
            return {
                "encontrado_en_bd": False,
                "consulta_id": consulta_id,
                "vino": vino_por_ean,
                "vino_key": nombre_slug or None,
                "mostrar_boton_comprar": True,
                "mensaje": "Identificado por código en el QR. ¿Quieres una recomendación similar?",
                "es_pro": es_pro,
                "entidades_extraidas": _obtener_entidades_extraidas(texto_busqueda, vino_por_ean),
            }
        logger.info("[ESCANEAR] Open Food Facts sin resultado para código extraído %s.", ean_extraido[:16])

    # Normalizar texto OCR (Sados -> Viña Pedrosa, Bobgcas -> Bodegas, pet DUERO -> del Duero, etc.)
    texto_limpio = normalizar_ocr(texto_busqueda)
    if texto_limpio != texto_busqueda:
        logger.info("[ESCANEAR] Texto normalizado: %s", texto_limpio[:200] if texto_limpio else "(vacío)")

    # Si la imagen solo dio texto poco claro (muy corto o sin letras), no inventar resultado
    if imagen_enviada and _es_texto_poco_claro(texto_limpio or texto_busqueda):
        logger.info("[ESCANEAR] Texto poco claro, no se inventa resultado.")
        return {
            "reconocido": False,
            "error_imagen": True,
            "es_pro": es_pro,
            "mensaje": (
                error_vision_imagen
                if error_vision_imagen
                else "No se pudo identificar la etiqueta con claridad. Prueba con otra foto más nítida o escribe el nombre del vino abajo."
            ),
            "entidades_extraidas": _obtener_entidades_extraidas(texto_limpio or texto_busqueda, entidades_override=entidades_imagen),
            "diagnostico_imagen": calidad_imagen or {},
        }

    # Buscar en BD con texto normalizado para mejorar match (Viña Pedrosa, Protos, etc.)
    texto_para_buscar = texto_limpio if texto_limpio else texto_busqueda
    coincidencias = buscar_vinos_avanzado(vinos, texto_para_buscar, limite=5)

    # Mejora: si hay entidades extraídas (nombre, bodega, DO), usar búsqueda multi-campo
    # que es mucho más precisa que el texto plano cuando Gemini Vision identifica el vino
    if entidades_imagen and isinstance(entidades_imagen, dict) and any(
        entidades_imagen.get(k) for k in ("nombre", "bodega", "denominacion", "variedad")
    ):
        coincidencias_entidades = buscar_por_entidades(vinos, entidades_imagen, limite=5)
        if coincidencias_entidades:
            # Fusionar: el mejor de entidades toma preferencia si su score es competitivo
            top_entidades = coincidencias_entidades[0]
            top_texto = coincidencias[0] if coincidencias else None
            if not top_texto or top_entidades["score"] >= top_texto["score"] * 0.8:
                logger.info("[ESCANEAR] Búsqueda por entidades separadas activada. Mejor: %s (score=%.2f)",
                    (top_entidades.get("vino") or {}).get("nombre", "")[:60], top_entidades["score"])
                coincidencias = coincidencias_entidades

    mejor_score = coincidencias[0]["score"] if coincidencias else 0
    mejor_nombre = (coincidencias[0]["vino"].get("nombre") or "") if coincidencias else ""
    logger.info("[ESCANEAR] BD: %d coincidencias, mejor score=%.2f, nombre=%s", len(coincidencias), mejor_score, mejor_nombre[:80] if mejor_nombre else "")
    # Diagnóstico: si el texto parece Viña Pedrosa pero no hay match fiable, mostrar top 3 para depurar
    if coincidencias and (mejor_score < 5.0 or "pedrosa" in (texto_para_buscar or "").lower()):
        for i, c in enumerate(coincidencias[:3]):
            n = (c.get("vino") or {}).get("nombre") or ""
            logger.info("[ESCANEAR]   top%d: score=%.2f nombre=%s", i + 1, c.get("score", 0), n[:60])

    # Solo devolvemos un vino de nuestra BD si la coincidencia es FUERTE (score >= 5) y el nombre cuadra.
    # Así nunca devolvemos "Pingus" cuando el usuario escaneó "Viña Pedrosa".
    if coincidencias and coincidencias[0]["score"] >= 5.0:
        mejor = coincidencias[0]
        vino = mejor["vino"]
        nombre_vino = (vino.get("nombre") or "").strip()
        bodega_vino = (vino.get("bodega") or "").strip()
        if _coincidencia_fiable(texto_para_buscar, nombre_vino, bodega_vino):
            logger.info("[ESCANEAR] Encontrado en BD: %s (key=%s)", nombre_vino[:80], mejor["key"])
            consulta_id = str(uuid.uuid4())
            consultas[consulta_id] = {"vino": vino, "key": mejor["key"]}
            try:
                from services import analytics_service
                analytics_service.registrar_escaneo(True, vino.get("nombre"), vino.get("pais"))
            except Exception:
                pass
            _push_historial(request, x_session_id, consulta_id, vino.get("nombre"), True)
            return {
                "encontrado_en_bd": True,
                "consulta_id": consulta_id,
                "key": mejor["key"],
                "vino_key": mejor["key"],
                "mostrar_boton_comprar": True,
                "vino": vino,
                "otros_resultados": [
                    {"key": c["key"], "nombre": c["vino"].get("nombre"), "score": round(c["score"], 2)}
                    for c in coincidencias[1:4]
                ],
                "es_pro": es_pro,
                "entidades_extraidas": _obtener_entidades_extraidas(texto_para_buscar, entidades_override=entidades_imagen),
            }

    logger.info("[ESCANEAR] Vino no encontrado en BD local. Buscando en fuente externa (Open Food Facts)...")
    resultados_externos = []
    nombre_externo = ""
    try:
        resultados_externos = buscar_por_texto(texto_para_buscar, limite=1)
        if not resultados_externos and len((texto_para_buscar or "").split()) > 3:
            query_corta = _extraer_query_corta(texto_para_buscar, max_palabras=4)
            if query_corta and query_corta != texto_para_buscar[:50].strip():
                logger.info("[ESCANEAR] Reintento externo con query corta: %s", query_corta[:60])
                resultados_externos = buscar_por_texto(query_corta, limite=1)
        nombre_externo = (resultados_externos[0].get("nombre") or "").strip() if resultados_externos else ""
    except Exception as e:
        logger.warning("[ESCANEAR] Error en búsqueda externa (se devuelve genérico): %s", e)

    if resultados_externos and _coincidencia_fiable(texto_para_buscar, nombre_externo, (resultados_externos[0].get("bodega") or "").strip()):
        logger.info("[ESCANEAR] Resultado externo usado: %s", nombre_externo[:80])
        try:
            vino_externo = resultados_externos[0]
            consulta_id = str(uuid.uuid4())
            key_guardada = _guardar_vino_consulta(request, vino_externo)
            consultas[consulta_id] = {"vino": vino_externo, "key": key_guardada}
            try:
                from services import analytics_service
                analytics_service.registrar_escaneo(False, vino_externo.get("nombre"), vino_externo.get("pais"))
            except Exception:
                pass
            _push_historial(request, sid, consulta_id, vino_externo.get("nombre"), False)
            nombre_slug = key_guardada or _slug(vino_externo.get("nombre") or "")
            return {
                "encontrado_en_bd": False,
                "consulta_id": consulta_id,
                "vino": vino_externo,
                "vino_key": nombre_slug or None,
                "mostrar_boton_comprar": True,
                "mensaje": "Este vino no está en nuestra base de datos. Te mostramos la información que encontramos fuera; ya la hemos guardado. ¿Quieres una recomendación similar de nuestra base?",
                "es_pro": es_pro,
                "entidades_extraidas": _obtener_entidades_extraidas(texto_para_buscar, entidades_override=entidades_imagen),
            }
        except Exception as e:
            logger.warning("[ESCANEAR] Error al guardar vino externo: %s", e)

    logger.info("[ESCANEAR] Sin coincidencia externa fiable. Intentando fallback con experto (Gemini)...")
    consulta_id = str(uuid.uuid4())
    # Usar texto normalizado o raw para el mensaje (si normalizó a vacío, queda el código de barras)
    nombre_busqueda = (texto_para_buscar or texto_busqueda or "vino")[:200].strip()

    # Fallback: si tenemos texto que parece nombre (no solo EAN), intentar Gemini para dar resultado en vez de error
    if not _es_solo_codigo_barras(nombre_busqueda) and len(nombre_busqueda.strip()) >= 3:
        try:
            from services import sumiller_gemini_service as gemini_svc
            from services import vinos_aprendidos_service as aprendidos_svc
            _, vino_nuevo = gemini_svc.buscar_vino_en_nube(nombre_busqueda, perfil="aficionado")
            if vino_nuevo and isinstance(vino_nuevo, dict) and (vino_nuevo.get("nombre") or vino_nuevo.get("bodega")):
                key_aprendida = aprendidos_svc.guardar_vino_aprendido(vino_nuevo)
                if key_aprendida:
                    vinos = _get_vinos(request)
                    vinos[key_aprendida] = vino_nuevo
                    request.app.state.vinos_mundiales = vinos
                consulta_id = str(uuid.uuid4())
                consultas[consulta_id] = {"vino": vino_nuevo, "key": key_aprendida}
                try:
                    from services import analytics_service
                    analytics_service.registrar_escaneo(False, vino_nuevo.get("nombre"), vino_nuevo.get("pais"))
                except Exception:
                    pass
                _push_historial(request, sid, consulta_id, vino_nuevo.get("nombre"), False)
                nombre_slug = key_aprendida or _slug(vino_nuevo.get("nombre") or "")
                logger.info("[ESCANEAR] Fallback Gemini OK: %s", (vino_nuevo.get("nombre") or "")[:60])
                return {
                    "encontrado_en_bd": False,
                    "consulta_id": consulta_id,
                    "vino": vino_nuevo,
                    "vino_key": nombre_slug or None,
                    "mostrar_boton_comprar": True,
                    "recomendar_similar": True,
                    "mensaje": "Lo hemos identificado con nuestro experto. Ya está guardado para la próxima. ¿Quieres una recomendación similar?",
                    "es_pro": es_pro,
                    "entidades_extraidas": _obtener_entidades_extraidas(texto_para_buscar, entidades_override=entidades_imagen),
                    "vino_anadido_a_base": True,
                }
        except Exception as e:
            logger.warning("[ESCANEAR] Fallback Gemini no disponible o falló: %s", e)

    logger.info("[ESCANEAR] Sin resultado en experto. Devolviendo mensaje genérico.")
    vino_gen = {
        "nombre": nombre_busqueda,
        "bodega": "No especificada",
        "region": "Por determinar",
        "pais": "Información no especificada",
        "tipo": "tinto",
        "puntuacion": None,
        "precio_estimado": None,
        "descripcion": f"No tenemos información de «{nombre_busqueda}» en nuestra base de datos. Pregunta al experto en vinos: «¿Qué vino me recomiendas similar a {nombre_busqueda}?».",
        "notas_cata": "No disponibles.",
        "maridaje": "Información no disponible.",
        "_origen": "generico",
    }
    consultas[consulta_id] = {"vino": vino_gen, "key": None}
    try:
        from services import analytics_service
        analytics_service.registrar_escaneo(False, vino_gen.get("nombre"), vino_gen.get("pais"))
    except Exception:
        pass
    _push_historial(request, sid, consulta_id, vino_gen.get("nombre"), False)
    nombre_slug = _slug(vino_gen.get("nombre") or "")
    # Enlace genérico a búsqueda web (sin promocionar competencia)
    termino_web = (texto_busqueda or texto_para_buscar or nombre_busqueda or "vino").strip()[:200]
    busqueda_web_url = "https://www.google.com/search?q=" + quote(termino_web + " vino")
    return {
        "encontrado_en_bd": False,
        "consulta_id": consulta_id,
        "vino": vino_gen,
        "vino_key": nombre_slug or None,
        "mostrar_boton_comprar": False,
        "recomendar_similar": True,
        "mensaje": "No tengo este vino en mi base (la fuente externa no lo tiene o la conexión falló). Pídeme una recomendación similar o prueba de nuevo más tarde.",
        "termino_buscado": termino_web,
        "busqueda_web_url": busqueda_web_url,
        "busqueda_web_label": "Buscar en la web",
        "es_pro": es_pro,
        "entidades_extraidas": _obtener_entidades_extraidas(texto_para_buscar, entidades_override=entidades_imagen),
        "diagnostico_imagen": calidad_imagen or {},
    }


class VinoRegistro(BaseModel):
    """Cuerpo JSON para registrar un vino (mismo formato que la BD)."""
    nombre: str = Field(..., min_length=1, max_length=200)
    bodega: str = Field(default="No especificada", max_length=200)
    region: str = Field(default="Por determinar", max_length=150)
    pais: str = Field(default="Desconocido", max_length=100)
    tipo: str = Field(default="tinto", max_length=50)
    puntuacion: int | None = Field(default=None, ge=0, le=100)
    precio_estimado: str | None = None
    descripcion: str = Field(default="", max_length=2000)
    notas_cata: str = Field(default="", max_length=2000)
    maridaje: str = Field(default="", max_length=1000)
    key: str | None = Field(default=None, description="Clave opcional; si no se envía se genera del nombre")


@router.post("/registrar-vino")
async def registrar_vino(
    request: Request,
    body: VinoRegistro,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Registra un nuevo vino en data/registrados.json.
    Validación anti-tonterías y límite diario por sesión (X-Session-ID opcional).
    """
    nombre = (body.nombre or "").strip()[:200]
    bodega = (body.bodega or "No especificada").strip()[:200]
    try:
        from services import validacion_service as validacion_svc
        from services import limite_diario_service as limite_diario_svc
        ok_val, msg_key = validacion_svc.validar_vino_completo(nombre, bodega, anio=None, alcohol=None)
        if not ok_val:
            raise HTTPException(status_code=400, detail={"error": "validation", "message_key": msg_key})
        sid = (x_session_id or "").strip()
        if sid:
            puede, _ = limite_diario_svc.puede_registrar_hoy(sid)
            if not puede:
                raise HTTPException(status_code=429, detail={"error": "limite_diario", "message_key": "limite_diario"})
    except HTTPException:
        raise
    except Exception:
        pass

    key = (body.key or "").strip() or _slug(nombre)
    if not key:
        key = f"vino_registrado_{uuid.uuid4().hex[:8]}"

    vino = {
        "nombre": nombre,
        "bodega": (body.bodega or "No especificada").strip()[:200],
        "region": (body.region or "Por determinar").strip()[:150],
        "pais": (body.pais or "Desconocido").strip()[:100],
        "tipo": (body.tipo or "tinto").strip().lower() or "tinto",
        "puntuacion": body.puntuacion,
        "precio_estimado": (body.precio_estimado or "").strip() or None,
        "descripcion": (body.descripcion or "").strip() or "Vino registrado por el usuario.",
        "notas_cata": (body.notas_cata or "").strip() or "No disponibles.",
        "maridaje": (body.maridaje or "").strip() or "Información no disponible.",
    }

    os.makedirs(DATA_FOLDER, exist_ok=True)
    registrados = {}
    if os.path.exists(REGISTRADOS_PATH):
        try:
            with open(REGISTRADOS_PATH, "r", encoding="utf-8") as f:
                registrados = json.load(f)
        except Exception:
            registrados = {}

    base_key = key
    contador = 1
    while key in registrados:
        key = f"{base_key}_{contador}"
        contador += 1

    registrados[key] = vino
    with open(REGISTRADOS_PATH, "w", encoding="utf-8") as f:
        json.dump(registrados, f, ensure_ascii=False, indent=2)

    vinos = _get_vinos(request)
    vinos[key] = vino

    sid = (x_session_id or "").strip()
    if sid:
        try:
            from services import limite_diario_service as limite_diario_svc
            limite_diario_svc.incrementar_registro(sid)
        except Exception:
            pass

    return {
        "success": True,
        "key": key,
        "vino": vino,
        "mensaje": "Vino registrado correctamente. A partir de ahora aparecerá en las búsquedas.",
    }


@router.get("/historial-escaneos")
def get_historial_escaneos(request: Request, x_session_id: str | None = Header(None, alias="X-Session-ID"), limite: int = 20):
    """Historial de escaneos del usuario (requiere X-Session-ID)."""
    hist = getattr(request.app.state, "historial_escaneos", {})
    if not x_session_id or not x_session_id.strip():
        return {"historial": []}
    lista = hist.get(x_session_id.strip(), [])[-limite:]
    return {"historial": list(reversed(lista))}
