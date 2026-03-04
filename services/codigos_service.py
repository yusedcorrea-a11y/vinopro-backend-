"""
Servicio para extraer códigos de barras y QR de una imagen (etiqueta de botella).
Usa pyzbar; si no está instalado o falla libzbar, devuelve lista vacía sin romper el flujo.

Una sola foto puede contener: código de barras (EAN) + QR. El escáner prioriza estos
para identificar el vino por Open Food Facts antes de usar OCR.
"""
import io
import logging
import re

logger = logging.getLogger(__name__)

CODIGOS_AVAILABLE = False
try:
    from pyzbar import pyzbar
    from PIL import Image
    CODIGOS_AVAILABLE = True
except ImportError as e:
    logger.debug("pyzbar no disponible (instalar pyzbar y libzbar): %s", e)


def _es_ean(data: str) -> bool:
    """True si el dato parece un EAN/GTIN (solo dígitos, 8-14 caracteres)."""
    if not data or not isinstance(data, str):
        return False
    limpio = re.sub(r"\D", "", data)
    return 8 <= len(limpio) <= 14


def _normalizar_ean(data: str) -> str:
    """Extrae solo dígitos para EAN (8-14)."""
    if not data:
        return ""
    limpio = re.sub(r"\D", "", data)
    if 8 <= len(limpio) <= 14:
        return limpio
    return limpio[:14] if len(limpio) > 14 else limpio


def extraer_codigos_de_imagen(contenido: bytes) -> list[dict]:
    """
    Extrae todos los códigos de barras y QR visibles en la imagen.
    :param contenido: bytes de la imagen (JPEG, PNG, etc.)
    :return: lista de {"tipo": "EAN-13"|"QRCODE"|..., "data": str}. Si pyzbar no está o falla, [].
    """
    if not CODIGOS_AVAILABLE or not contenido:
        return []
    try:
        image = Image.open(io.BytesIO(contenido))
        image = image.convert("RGB")
        decoded = pyzbar.decode(image)
        out = []
        for obj in decoded:
            tipo = getattr(obj, "type", "UNKNOWN")
            if isinstance(tipo, bytes):
                tipo = tipo.decode("utf-8", errors="replace")
            data_raw = getattr(obj, "data", b"")
            try:
                data = data_raw.decode("utf-8", errors="replace").strip()
            except Exception:
                data = str(data_raw)
            if data:
                out.append({"tipo": str(tipo), "data": data})
        return out
    except Exception as e:
        logger.warning("Error extrayendo códigos de imagen: %s", e)
        return []


def extraer_primer_ean_de_imagen(contenido: bytes) -> str | None:
    """
    Devuelve el primer código que parezca EAN/GTIN (de barras o de QR) para buscar en Open Food Facts.
    :return: string de dígitos EAN o None si no hay ninguno.
    """
    codigos = extraer_codigos_de_imagen(contenido)
    for c in codigos:
        data = (c.get("data") or "").strip()
        if _es_ean(data):
            return _normalizar_ean(data)
    return None
