"""
Preprocesamiento de imágenes para OCR en etiquetas de vino.
Optimizado para CPU (Lenovo IdeaPad 3): CLAHE, filtrado bilateral y sharpen.
Sin dependencias de GPU.
"""
import io
import logging
logger = logging.getLogger(__name__)

PREPROCESSOR_AVAILABLE = False
try:
    import cv2
    import numpy as np
    PREPROCESSOR_AVAILABLE = True
except ImportError:
    cv2 = None
    np = None

# Tamaño máximo del lado largo (igual que ocr_service)
MAX_SIDE = 1200

# Palabras clave de vino que indican texto útil para elegir mejor resultado OCR
_PALABRAS_CLAVE_VINO = frozenset({
    "bodega", "bodegas", "crianza", "reserva", "gran", "ribera", "rioja", "duero",
    "denominacion", "origen", "producto", "espana", "españa", "vino", "tinto", "blanco",
    "tempranillo", "garnacha", "pedrosa", "protos", "pascuas", "hnos", "hnos.",
})


def _redimensionar_si_necesario(img, max_side: int = MAX_SIDE):
    """Redimensiona si el lado mayor excede max_side."""
    h, w = img.shape[:2]
    if max(h, w) <= max_side:
        return img
    ratio = max_side / max(h, w)
    new_w, new_h = int(w * ratio), int(h * ratio)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)


def _pipeline_grayscale_clahe(img) -> "np.ndarray":
    """Escala de grises + CLAHE para contraste irregular (sombras, reflejos suaves)."""
    if not PREPROCESSOR_AVAILABLE:
        return img
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _pipeline_bilateral_sharpen(img) -> "np.ndarray":
    """Filtrado bilateral (reduce ruido, preserva bordes) + unsharp mask."""
    if not PREPROCESSOR_AVAILABLE:
        return img
    # Bilateral: d=5 para rendimiento en CPU, sigmaColor/sigmaSpace moderados
    filtered = cv2.bilateralFilter(img, d=5, sigmaColor=50, sigmaSpace=50)
    gray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
    # Unsharp mask: realce de bordes para texto
    gaussian = cv2.GaussianBlur(gray, (0, 0), 2.0)
    sharpened = cv2.addWeighted(gray, 1.5, gaussian, -0.5, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def _pipeline_adaptive_binary(img) -> "np.ndarray":
    """Binarización adaptativa para etiquetas muy degradadas o alto contraste."""
    if not PREPROCESSOR_AVAILABLE:
        return img
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )


def preprocesar_para_ocr(contenido: bytes) -> list[tuple[str, "np.ndarray"]]:
    """
    Genera versiones preprocesadas de la imagen para OCR multi-paso.
    :param contenido: bytes de la imagen (JPEG, PNG, etc.)
    :return: lista de (nombre_pipeline, imagen_numpy). Si OpenCV no está, devuelve [].
    """
    if not PREPROCESSOR_AVAILABLE or not contenido:
        return []

    try:
        arr = np.frombuffer(contenido, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return []
        img = _redimensionar_si_necesario(img)
        pipelines = [
            ("clahe", _pipeline_grayscale_clahe(img)),
            ("bilateral_sharpen", _pipeline_bilateral_sharpen(img)),
            ("adaptive", _pipeline_adaptive_binary(img)),
        ]
        return pipelines
    except Exception as e:
        logger.warning("[Preprocesador] Error: %s", e)
        return []


def _score_texto_ocr(texto: str) -> float:
    """Puntuación heurística: más palabras clave de vino = mejor resultado."""
    if not texto or len(texto.strip()) < 3:
        return 0.0
    t_lower = texto.lower()
    palabras = set(t_lower.split())
    score = len(texto) * 0.1  # base por longitud
    for kw in _PALABRAS_CLAVE_VINO:
        if kw in t_lower or kw in palabras:
            score += 2.0
    return score


def obtener_mejor_imagen_para_ocr(contenido: bytes) -> "np.ndarray | None":
    """
    Devuelve la imagen original redimensionada (PIL/numpy compatible).
    Usado cuando no hay OpenCV: ocr_service hace resize con PIL.
    Con OpenCV: el preprocesador se usa desde ocr_service para multi-paso.
    """
    if not PREPROCESSOR_AVAILABLE or not contenido:
        return None
    try:
        arr = np.frombuffer(contenido, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        return _redimensionar_si_necesario(img)
    except Exception:
        return None
