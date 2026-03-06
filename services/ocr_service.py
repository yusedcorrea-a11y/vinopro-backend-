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
import sys

logger = logging.getLogger(__name__)


class TesseractNoDisponibleError(Exception):
    """Se lanza cuando Tesseract OCR no está instalado o no está en el PATH."""
    pass


try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
    _TesseractNotFoundError = getattr(pytesseract, "TesseractNotFoundError", Exception)
    if sys.platform == "win32":
        _tesseract_exe = os.environ.get("TESSERACT_CMD") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.isfile(_tesseract_exe):
            pytesseract.pytesseract.tesseract_cmd = _tesseract_exe
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
        return ""

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
