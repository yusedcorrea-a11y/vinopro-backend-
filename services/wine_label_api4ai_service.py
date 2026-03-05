"""
Reconocimiento de etiquetas de vino por imagen (API4AI Wine Recognition).
Opcional: si API4AI_API_URL está definida y la llamada tiene éxito, usamos el resultado
para identificar el vino antes de caer a OCR + búsqueda por texto.
Demo: https://demo.api4ai.cloud (gratis, con límites; no producción).
Producción: https://api4ai.cloud o RapidAPI (API key en API4AI_API_KEY).
"""
import logging
import os

logger = logging.getLogger(__name__)

# Demo gratuito (sin key); producción: definir API4AI_API_URL y opcionalmente API4AI_API_KEY
API4AI_BASE_URL = os.environ.get("API4AI_API_URL", "https://demo.api4ai.cloud")
WINE_REC_PATH = "/wine-rec/v1/results"
TIMEOUT = 15.0
MIN_CONFIDENCE = 0.5  # Umbral mínimo para aceptar una sugerencia


def recognize_wine_from_image(image_bytes: bytes) -> list[dict] | None:
    """
    Envía la imagen a API4AI Wine Recognition y devuelve la lista de sugerencias
    (cada una con 'name' o 'label' y 'confidence').
    Si falla o la API no está configurada, devuelve None.
    """
    if not image_bytes or len(image_bytes) < 100:
        return None

    try:
        import httpx
    except ImportError:
        logger.warning("[API4AI] httpx no disponible; omitiendo reconocimiento por imagen.")
        return None

    url = API4AI_BASE_URL.rstrip("/") + WINE_REC_PATH
    headers = {}
    api_key = os.environ.get("API4AI_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"ApiKey {api_key}"

    files = {"image": ("wine_label.jpg", image_bytes, "image/jpeg")}

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.post(url, files=files, headers=headers or None)
        r.raise_for_status()
        data = r.json()
    except httpx.TimeoutException:
        logger.warning("[API4AI] Timeout al reconocer imagen.")
        return None
    except httpx.HTTPStatusError as e:
        logger.warning("[API4AI] HTTP %s: %s", e.response.status_code, e.response.text[:200])
        return None
    except Exception as e:
        logger.warning("[API4AI] Error: %s", e)
        return None

    # Respuesta API4AI: varias formas posibles (results[].entities[].wine, result.wines, etc.)
    suggestions = []
    try:
        results = data.get("results") or data.get("result") or []
        if isinstance(results, dict):
            results = results.get("wines") or results.get("items") or []
        # Recoger todas las entradas tipo "wine" (results[].entities[] o results[].wine o results[].label)
        items_to_check = []
        for r in results:
            if isinstance(r, dict):
                entities = r.get("entities") or r.get("wines")
                if entities:
                    for e in entities:
                        if isinstance(e, dict):
                            items_to_check.append(e.get("wine") or e)
                        elif isinstance(e, str):
                            items_to_check.append({"name": e, "confidence": 0.6})
                else:
                    items_to_check.append(r.get("wine") or r)
            elif isinstance(r, str):
                items_to_check.append({"name": r, "confidence": 0.6})
        for wine in items_to_check:
            if not isinstance(wine, dict):
                continue
            label = (wine.get("label") or wine.get("name") or wine.get("wine_name") or "").strip()
            conf = wine.get("confidence")
            if conf is None:
                conf = wine.get("score")
            if isinstance(conf, (int, float)):
                if conf > 1:
                    conf = conf / 100.0
                conf = max(0, min(1, float(conf)))
            if label:
                suggestions.append({"name": label, "confidence": conf if isinstance(conf, (int, float)) else 0.6})
    except (TypeError, AttributeError, KeyError) as e:
        logger.info("[API4AI] Formato inesperado: %s. Keys: %s", e, list(data.keys()) if isinstance(data, dict) else None)

    if suggestions:
        suggestions.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        logger.info("[API4AI] Sugerencias: %s", suggestions[:3])
    return suggestions if suggestions else None
