"""
Endpoints de escaneo de etiquetas y registro de vinos.
"""
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

from services.busqueda_service import buscar_vinos_avanzado, buscar_por_codigo_barras_bd
from services.ocr_service import extraer_texto_de_imagen, TesseractNoDisponibleError
from services.api_externa_service import buscar_por_texto, buscar_por_codigo_barras
from services.ocr_normalizer import limpiar as normalizar_ocr
from services.codigos_service import extraer_primer_ean_de_imagen
from services.wine_label_api4ai_service import recognize_wine_from_image
from services.entity_extractor import extraer_entidades, formatear_entidades_para_json

router = APIRouter(prefix="", tags=["Escaneo"])

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
REGISTRADOS_PATH = os.path.join(DATA_FOLDER, "registrados.json")


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


# Marcas clave: si están en texto Y en nombre/bodega del vino, consideramos la coincidencia fiable
# (evita rechazar "Protos Reserva" cuando el OCR pone "Protos propucto"; o Viña Pedrosa cuando solo lee "Pérez Pascuas")
_MARCAS_CLAVE_BD = ("protos", "pedrosa")
# Bodega clave: si el texto contiene esto y el vino tiene esta bodega, es fiable (ej. OCR solo leyó "Pérez Pascuas")
_BODEGA_CLAVE_PEDROSA = "pérez pascuas"


def _coincidencia_fiable(texto_busqueda: str, nombre_vino: str, bodega_vino: str | None = None) -> bool:
    """
    True solo si estamos seguros de que el texto de búsqueda se refiere a ESE vino.
    Evita devolver "Pingus" cuando el usuario escaneó "Viña Pedrosa" (honestidad máxima).
    Si la marca (Protos, Pedrosa) está en ambos lados, confiamos aunque el OCR haya puesto "propucto" etc.
    Si el texto tiene "Pérez Pascuas" y el vino tiene esa bodega (Viña Pedrosa), también es fiable.
    """
    if not nombre_vino or not isinstance(nombre_vino, str):
        return False
    busq = _normalizar_para_coincidencia(texto_busqueda)
    nombre = _normalizar_para_coincidencia(nombre_vino)
    bodega = _normalizar_para_coincidencia(bodega_vino or "") if bodega_vino else ""
    if not busq and not bodega:
        return False
    # Marca clave en texto y en nombre: Protos/Protos Reserva o Pedrosa/Viña Pedrosa -> fiable
    for marca in _MARCAS_CLAVE_BD:
        if marca in busq and marca in nombre:
            return True
    # Si el OCR solo leyó la bodega: "Pérez Pascuas" en texto y el vino es de esa bodega (Viña Pedrosa, etc.)
    if _BODEGA_CLAVE_PEDROSA in busq and "pascuas" in bodega:
        return True
    # Contención: "Viña Pedrosa" en "Viña Pedrosa Crianza" o al revés
    if nombre and (busq in nombre or nombre in busq):
        return True
    # Al menos 2 tokens significativos del texto de búsqueda deben aparecer en el nombre
    tokens_busq = [x for x in busq.split() if len(x) > 2]
    tokens_nom = set(nombre.split())
    coinciden = sum(1 for t in tokens_busq if t in tokens_nom)
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


def _obtener_entidades_extraidas(texto: str | None, vino: dict | None = None) -> dict:
    """
    Extrae entidades (bodega, añada, denominacion_origen, variedad) del texto OCR
    o las deriva del vino cuando no hay texto (ej. match por EAN).
    Siempre devuelve un dict para incluir en entidades_extraidas.
    """
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


@router.post("/escanear")
async def escanear_etiqueta(
    request: Request,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """
    Escanea una etiqueta de vino por imagen y/o texto. Identifica vinos en local o en línea.

    Flujo (los ojos del sumiller — una foto, varias señales):
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
        return await _escanear_etiqueta_impl(request, x_session_id)
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
            "descripcion": "No pudimos identificar la etiqueta con seguridad. Puedes preguntar al sumiller por un vino similar o añadirlo manualmente.",
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
    error_tesseract = False
    contenido_imagen = None
    if imagen and getattr(imagen, "read", None):
        try:
            contenido_imagen = await imagen.read()
            if contenido_imagen:
                imagen_enviada = True
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
                # 1b) OCR de la etiqueta ANTES que la API de imagen: si el texto (Viña Pedrosa, Pérez Pascuas, etc.)
                #     coincide con un vino de nuestra BD, lo devolvemos y no usamos el resultado de la API (que a veces falla).
                texto_ocr = None
                try:
                    texto_ocr = extraer_texto_de_imagen(contenido_imagen)
                    if texto_ocr:
                        texto_busqueda = f"{texto_busqueda} {texto_ocr}".strip()
                except TesseractNoDisponibleError:
                    error_tesseract = True
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
                                        "entidades_extraidas": _obtener_entidades_extraidas(texto_para_early),
                                    }
                # 2) Reconocimiento por imagen (API4AI): NO usamos el resultado para devolver vino.
                # La API suele devolver siempre el mismo vino (ej. Changyu Icewine) para fotos distintas;
                # como Changyu está en nuestra BD, antes devolvíamos ese vino para cualquier escaneo.
                # Solo confiamos en OCR + nuestra BD o en texto/código que escriba el usuario.
                sugerencias_ia = recognize_wine_from_image(contenido_imagen)
                if sugerencias_ia and sugerencias_ia[0].get("confidence", 0) >= 0.5:
                    nombre_ia = (sugerencias_ia[0].get("name") or "").strip()
                    if nombre_ia:
                        logger.info("[ESCANEAR] API4AI sugirió %s; no usamos para devolver (evitar mismo vino para todas las fotos).", nombre_ia[:50])
                # OCR ya hecho arriba (1b) para priorizar nuestra BD (Viña Pedrosa, etc.)
        except Exception:
            imagen_enviada = True

    if error_tesseract:
        return {
            "reconocido": False,
            "error_imagen": True,
            "es_pro": _es_pro(x_session_id or ""),
            "mensaje": "El escaneo requiere un componente adicional. Por favor, contacta al administrador.",
            "entidades_extraidas": {},
        }

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
            return {
                "reconocido": False,
                "error_imagen": True,
                "es_pro": es_pro,
                "mensaje": "No pudimos leer la etiqueta. ¿Es una botella de vino? Prueba con otra foto más nítida o escribe el nombre del vino abajo.",
                "entidades_extraidas": {},
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
            "mensaje": "No se pudo identificar la etiqueta con claridad. Prueba con otra foto más nítida o escribe el nombre del vino abajo.",
            "entidades_extraidas": _obtener_entidades_extraidas(texto_limpio or texto_busqueda),
        }

    # Buscar en BD con texto normalizado para mejorar match (Viña Pedrosa, Protos, etc.)
    texto_para_buscar = texto_limpio if texto_limpio else texto_busqueda
    coincidencias = buscar_vinos_avanzado(vinos, texto_para_buscar, limite=5)
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
                "entidades_extraidas": _obtener_entidades_extraidas(texto_para_buscar),
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
                "entidades_extraidas": _obtener_entidades_extraidas(texto_para_buscar),
            }
        except Exception as e:
            logger.warning("[ESCANEAR] Error al guardar vino externo: %s", e)

    logger.info("[ESCANEAR] Sin coincidencia externa fiable. Devolviendo mensaje genérico y enlace a búsqueda web.")
    consulta_id = str(uuid.uuid4())
    # Usar texto normalizado o raw para el mensaje (si normalizó a vacío, queda el código de barras)
    nombre_busqueda = (texto_para_buscar or texto_busqueda or "vino")[:200].strip()
    vino_gen = {
        "nombre": nombre_busqueda,
        "bodega": "No especificada",
        "region": "Por determinar",
        "pais": "Información no especificada",
        "tipo": "tinto",
        "puntuacion": None,
        "precio_estimado": None,
        "descripcion": f"No tenemos información de «{nombre_busqueda}» en nuestra base de datos. Puedes buscar en Vivino (como un buscador de vinos) o preguntar al sumiller: «¿Qué vino me recomiendas similar a {nombre_busqueda}?».",
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
    # Enlace para buscar en Vivino (buscador de vinos, como Amazon pero de vinos) — información real
    termino_web = (texto_busqueda or texto_para_buscar or nombre_busqueda or "vino").strip()[:200]
    busqueda_web_url = "https://www.vivino.com/search/wine?q=" + quote(termino_web)
    return {
        "encontrado_en_bd": False,
        "consulta_id": consulta_id,
        "vino": vino_gen,
        "vino_key": nombre_slug or None,
        "mostrar_boton_comprar": False,
        "recomendar_similar": True,
        "mensaje": "No tengo este vino en mi base (Open Food Facts no lo tiene o la conexión falló). Usa «Buscar en Vivino» para ver información real o pídeme una recomendación similar.",
        "termino_buscado": termino_web,
        "busqueda_web_url": busqueda_web_url,
        "busqueda_web_label": "Buscar en Vivino",
        "es_pro": es_pro,
        "entidades_extraidas": _obtener_entidades_extraidas(texto_para_buscar),
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
