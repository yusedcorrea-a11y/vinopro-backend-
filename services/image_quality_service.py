"""
Evaluación ligera de calidad de imagen para el flujo de escaneo.
Permite detectar fotos borrosas, oscuras o con reflejos antes de gastar OCR/IA.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np

    IMAGE_QUALITY_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin OpenCV
    cv2 = None
    np = None
    IMAGE_QUALITY_AVAILABLE = False


_BRILLO_BAJO = 55.0
_BLUR_BAJO = 80.0
_HIGHLIGHT_RATIO_ALTO = 0.08


def evaluar_calidad_imagen(imagen_bytes: bytes) -> dict:
    """
    Evalúa calidad básica de la imagen para OCR/visión.
    Devuelve siempre un dict estable para que el frontend pueda reaccionar.
    """
    resultado = {
        "disponible": IMAGE_QUALITY_AVAILABLE,
        "ok": True,
        "motivos": [],
        "metricas": {},
    }
    if not IMAGE_QUALITY_AVAILABLE or not imagen_bytes:
        return resultado

    try:
        arr = np.frombuffer(imagen_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return {
                "disponible": True,
                "ok": False,
                "motivos": ["imagen_invalida"],
                "metricas": {},
            }

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brillo_medio = float(gray.mean())
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        highlights_ratio = float((gray >= 245).sum()) / float(gray.size or 1)

        motivos = []
        if brillo_medio < _BRILLO_BAJO:
            motivos.append("baja_luz")
        if blur_score < _BLUR_BAJO:
            motivos.append("borrosa")
        if highlights_ratio > _HIGHLIGHT_RATIO_ALTO:
            motivos.append("reflejos")

        resultado["ok"] = not motivos
        resultado["motivos"] = motivos
        resultado["metricas"] = {
            "brillo_medio": round(brillo_medio, 2),
            "blur_score": round(blur_score, 2),
            "highlights_ratio": round(highlights_ratio, 4),
        }
        return resultado
    except Exception as exc:  # pragma: no cover - defensivo
        logger.debug("[IMG_QUALITY] No se pudo evaluar la imagen: %s", exc)
        return resultado


def mensaje_calidad_imagen(calidad: dict | None) -> str | None:
    if not calidad or calidad.get("ok", True):
        return None
    motivos = calidad.get("motivos") or []
    if "imagen_invalida" in motivos:
        return "La imagen no se pudo procesar. Prueba con otra foto en JPG o PNG."
    if "borrosa" in motivos:
        return "La foto está borrosa. Acerca más la etiqueta, apoya el móvil un segundo y vuelve a capturar."
    if "baja_luz" in motivos and "reflejos" in motivos:
        return "La imagen tiene poca luz y reflejos. Busca una luz frontal suave y evita el brillo directo del cristal."
    if "baja_luz" in motivos:
        return "La foto tiene poca luz. Intenta una zona más iluminada o acerca la etiqueta a una luz frontal."
    if "reflejos" in motivos:
        return "Hay demasiado reflejo en la botella. Inclínala ligeramente y evita un punto de luz directo."
    return "No pudimos leer bien la foto. Intenta otra captura más nítida."
