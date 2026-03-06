"""
Servicio de OCR para extraer texto de imágenes de etiquetas de vino.
Usa pytesseract (Tesseract) con preprocesamiento OpenCV (CLAHE, bilateral, sharpen)
para mejorar lectura con reflejos, curvatura y ruido.

Flujo:
- Preprocesamiento multi-paso (si OpenCV disponible): CLAHE, bilateral+sharpen, adaptativo.
- OCR sobre cada versión; se elige el resultado con mejor puntuación.
- El texto se envía a routes/escaneo.py para búsqueda en BD y fuentes externas.
"""
import io
import logging
import os
import shutil
import sys

logger = logging.getLogger(__name__)


class TesseractNoDisponibleError(Exception):
    """Se lanza cuando Tesseract OCR no está instalado o no está en el PATH."""
    pass


def _obtener_ruta_tesseract() -> str | None:
    """Devuelve la ruta del ejecutable de Tesseract si existe, None si no."""
    if sys.platform == "win32":
        ruta = os.environ.get("TESSERACT_CMD") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        return ruta if os.path.isfile(ruta) else None
    # Linux/macOS: tesseract en PATH o /usr/bin/tesseract
    ruta_env = os.environ.get("TESSERACT_CMD")
    if ruta_env and os.path.isfile(ruta_env):
        return ruta_env
    tesseract_path = shutil.which("tesseract")
    return tesseract_path if tesseract_path else None


def _verificar_tesseract_disponible() -> tuple[bool, str]:
    """
    Verifica si Tesseract está instalado y accesible.
    :return: (disponible: bool, mensaje: str para log/error)
    """
    ruta = _obtener_ruta_tesseract()
    if not ruta:
        if sys.platform == "win32":
            msg = (
                "Tesseract OCR no encontrado. Instale desde "
                "https://github.com/UB-Mannheim/tesseract/wiki o ejecute: "
                "winget install UB-Mannheim.TesseractOCR. "
                "Ruta esperada: C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
            )
        else:
            msg = (
                "Tesseract OCR no encontrado. Instale con: "
                "apt-get install tesseract-ocr tesseract-ocr-spa (Debian/Ubuntu) o "
                "brew install tesseract (macOS). "
                "O use el Dockerfile incluido en el proyecto."
            )
        return False, msg
    return True, f"Tesseract encontrado: {ruta}"


try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
    _TesseractNotFoundError = getattr(pytesseract, "TesseractNotFoundError", Exception)

    _tesseract_ruta = _obtener_ruta_tesseract()
    if _tesseract_ruta:
        pytesseract.pytesseract.tesseract_cmd = _tesseract_ruta
        logger.info("[OCR] %s", _verificar_tesseract_disponible()[1])
    else:
        ok, msg = _verificar_tesseract_disponible()
        if not ok:
            logger.error("[OCR] %s", msg)
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None
    _TesseractNotFoundError = Exception

try:
    from services.image_preprocessor import preprocesar_para_ocr, PREPROCESSOR_AVAILABLE
except ImportError:
    PREPROCESSOR_AVAILABLE = False
    preprocesar_para_ocr = lambda c: []

MAX_SIDE_OCR = 1200

# Palabras clave que indican texto útil de etiqueta de vino
_PALABRAS_CLAVE = frozenset({
    "bodega", "bodegas", "crianza", "reserva", "gran", "ribera", "rioja", "duero",
    "denominacion", "origen", "producto", "espana", "españa", "vino", "tinto", "blanco",
    "tempranillo", "garnacha", "pedrosa", "protos", "pascuas", "hnos",
})


def _score_texto_ocr(texto: str) -> float:
    """Puntuación heurística: más palabras clave y longitud = mejor resultado."""
    if not texto or len(texto.strip()) < 3:
        return 0.0
    t_lower = texto.lower()
    score = len(texto) * 0.1
    for kw in _PALABRAS_CLAVE:
        if kw in t_lower:
            score += 2.0
    return score


def _ocr_desde_pil(image: "Image.Image", idioma: str) -> str:
    """Ejecuta Tesseract sobre una imagen PIL."""
    return (pytesseract.image_to_string(image, lang=idioma) or "").strip()


def _ocr_desde_numpy(arr, idioma: str) -> str:
    """Ejecuta Tesseract sobre un array numpy (OpenCV)."""
    try:
        from PIL import Image
        pil_img = Image.fromarray(arr)
        return _ocr_desde_pil(pil_img, idioma)
    except Exception:
        return ""


def extraer_texto_de_imagen(contenido: bytes, idioma: str = "spa+eng") -> str:
    """
    Extrae texto de una imagen (etiqueta de vino) usando OCR con preprocesamiento.
    Multi-paso: CLAHE, bilateral+sharpen, adaptativo + original. Elige el mejor resultado.
    :param contenido: bytes de la imagen (JPEG, PNG, etc.)
    :param idioma: idiomas para Tesseract (spa+eng por defecto)
    :return: texto extraído o cadena vacía si falla
    :raises TesseractNoDisponibleError: si Tesseract no está instalado
    """
    if not OCR_AVAILABLE:
        logger.warning("OCR no disponible: instalar Pillow y pytesseract (y Tesseract en el sistema)")
        raise TesseractNoDisponibleError("OCR no disponible: faltan dependencias Python (Pillow, pytesseract).")

    # Validación explícita antes de usar Tesseract
    disponible, msg = _verificar_tesseract_disponible()
    if not disponible:
        logger.error("[OCR] %s", msg)
        raise TesseractNoDisponibleError(msg)

    resultados: list[tuple[str, float]] = []

    # Pipeline 1: Preprocesamiento OpenCV + OCR multi-paso
    if PREPROCESSOR_AVAILABLE and preprocesar_para_ocr:
        pipelines = preprocesar_para_ocr(contenido)
        for nombre, img_arr in pipelines:
            try:
                texto = _ocr_desde_numpy(img_arr, idioma)
                if texto:
                    score = _score_texto_ocr(texto)
                    resultados.append((texto, score))
            except Exception as e:
                logger.debug("[OCR] Pipeline %s falló: %s", nombre, e)

    # Pipeline 2: Original con PIL (fallback o adicional)
    try:
        image = Image.open(io.BytesIO(contenido))
        image = image.convert("RGB")
        w, h = image.size
        if max(w, h) > MAX_SIDE_OCR:
            ratio = MAX_SIDE_OCR / max(w, h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            resample = getattr(Image, "LANCZOS", Image.BILINEAR)
            if getattr(Image, "Resampling", None) and hasattr(Image.Resampling, "LANCZOS"):
                resample = Image.Resampling.LANCZOS
            image = image.resize((new_w, new_h), resample)
        texto = _ocr_desde_pil(image, idioma)
        if texto:
            score = _score_texto_ocr(texto)
            resultados.append((texto, score))
    except Exception as e:
        msg = str(e).lower()
        is_tesseract_missing = (
            type(e).__name__ == "TesseractNotFoundError"
            or (e.__class__ is not Exception and e.__class__ is _TesseractNotFoundError)
            or ("tesseract" in msg and ("not installed" in msg or "not in your path" in msg or "not in path" in msg))
        )
        if is_tesseract_missing:
            logger.error(
                "Tesseract no instalado o no está en el PATH. Instale Tesseract OCR (ver docs/INSTALAR_TESSERACT_WINDOWS.md): %s",
                e,
            )
            raise TesseractNoDisponibleError(
                "Tesseract OCR no está instalado o no está en el PATH."
            ) from e
        logger.exception("Error en OCR: %s", e)
        return ""

    if not resultados:
        return ""

    # Elegir el resultado con mayor puntuación; si empatan, el más largo
    mejor = max(resultados, key=lambda x: (x[1], len(x[0])))
    return mejor[0]


# Umbrales para activar fallback con IA de visión
_MIN_LONGITUD_OCR_CONFIABLE = 15
_MIN_SCORE_OCR_CONFIABLE = 3.0


def extraer_datos_etiqueta_doble_capa(contenido: bytes, idioma: str = "spa+eng", session_key: str | None = None) -> dict:
    """
    Flujo de doble capa: OCR local optimizado + fallback con IA de visión.
    - Paso 1: OCR con preprocesamiento OpenCV (CLAHE, bilateral, sharpen).
    - Paso 2: Si OCR vacío, corto o baja confianza -> envía a GPT-4o o Claude 3.5.
    - Paso 3: Refinamiento (2O22->2022, etc.) y estructura JSON consistente.

    :param contenido: bytes de la imagen
    :param idioma: idiomas Tesseract (spa+eng)
    :return: {"texto": str, "entidades": dict, "origen": "ocr"|"vision", "error_vision": str|None}
    """
    from services.data_refinement import normalizar_entidades, refinar_texto_ocr
    from services.entity_extractor import extraer_entidades
    from services.vision_wine_service import analizar_etiqueta_vision

    resultado_base = {"texto": "", "entidades": {"bodega": None, "nombre": None, "añada": None, "denominacion_origen": None, "variedad": None}, "origen": "ocr", "error_vision": None}

    # Paso 1: OCR local
    texto_ocr = ""
    try:
        texto_ocr = extraer_texto_de_imagen(contenido, idioma)
    except TesseractNoDisponibleError:
        logger.info("[OCR] Tesseract no disponible, intentando fallback con IA de visión...")
        vision_result = analizar_etiqueta_vision(contenido, session_key=session_key)
        if vision_result and "error" in vision_result:
            resultado_base["error_vision"] = vision_result["error"]
            return resultado_base
        if vision_result:
            ent = normalizar_entidades(vision_result.get("entidades") or {})
            return {"texto": vision_result.get("texto") or "", "entidades": ent, "origen": "vision", "error_vision": None}
        return resultado_base

    texto_refinado = refinar_texto_ocr(texto_ocr)
    score = _score_texto_ocr(texto_refinado) if texto_refinado else 0.0

    # ¿OCR suficientemente bueno?
    if texto_refinado and len(texto_refinado) >= _MIN_LONGITUD_OCR_CONFIABLE and score >= _MIN_SCORE_OCR_CONFIABLE:
        ent = extraer_entidades(texto_refinado)
        ent_norm = normalizar_entidades(ent)
        return {"texto": texto_refinado, "entidades": ent_norm, "origen": "ocr", "error_vision": None}

    # Paso 2: Fallback con IA de visión
    logger.info("[OCR] Texto insuficiente (len=%d, score=%.1f), usando IA de visión...", len(texto_refinado or ""), score)
    vision_result = analizar_etiqueta_vision(contenido, session_key=session_key)
    if vision_result and "error" in vision_result:
        resultado_base["error_vision"] = vision_result["error"]
    elif vision_result:
        ent = normalizar_entidades(vision_result.get("entidades") or {})
        texto_vision = vision_result.get("texto") or ""
        return {"texto": texto_vision, "entidades": ent, "origen": "vision", "error_vision": None}

    # Sin visión: devolver lo que tengamos del OCR (aunque sea poco)
    if texto_refinado:
        ent = extraer_entidades(texto_refinado)
        ent_norm = normalizar_entidades(ent)
        return {"texto": texto_refinado, "entidades": ent_norm, "origen": "ocr", "error_vision": resultado_base["error_vision"]}
    return resultado_base
