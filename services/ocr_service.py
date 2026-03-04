"""
Servicio de OCR para extraer texto de imágenes de etiquetas de vino.
Usa pytesseract (Tesseract) para reconocimiento de caracteres.

Flujo real (solo información veraz):
- El texto extraído aquí se envía a routes/escaneo.py.
- Ahí se busca en la BASE DE DATOS de vinos (buscar_vinos_avanzado) y en fuentes
  externas (Open Food Facts, etc.). No se usa un LLM para "identificar" el vino:
  la identificación es por coincidencia real con el catálogo.
- Si no hay coincidencia, el backend devuelve un mensaje honesto y la opción
  "Recomiéndame algo similar" (sumiller sí usa reglas/IA para recomendar).
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
    # En Windows, winget/instalador suele dejar Tesseract aquí; así no dependemos del PATH
    if sys.platform == "win32":
        _tesseract_exe = os.environ.get("TESSERACT_CMD") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.isfile(_tesseract_exe):
            pytesseract.pytesseract.tesseract_cmd = _tesseract_exe
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None
    _TesseractNotFoundError = Exception


# Tamaño máximo del lado largo para no saturar OCR (fotos de móvil suelen ser 3000+ px)
MAX_SIDE_OCR = 1200


def extraer_texto_de_imagen(contenido: bytes, idioma: str = "spa+eng") -> str:
    """
    Extrae texto de una imagen (etiqueta de vino) usando OCR.
    Redimensiona imágenes muy grandes para acelerar y evitar fallos.
    :param contenido: bytes de la imagen (JPEG, PNG, etc.)
    :param idioma: idiomas para Tesseract (spa+eng por defecto)
    :return: texto extraído o cadena vacía si falla
    :raises TesseractNoDisponibleError: si Tesseract no está instalado o no está en el PATH
    """
    if not OCR_AVAILABLE:
        logger.warning("OCR no disponible: instalar Pillow y pytesseract (y Tesseract en el sistema)")
        return ""

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
        texto = pytesseract.image_to_string(image, lang=idioma)
        return (texto or "").strip()
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
