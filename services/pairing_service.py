"""
Maridaje con Spoonacular: vino → platos, plato → vinos, descripción de vino.
Lee SPOONACULAR_API_KEY; maneja 429 (cuota) y fallos con mensajes amigables.
"""
import os
from urllib.parse import quote

import httpx

_BASE = "https://api.spoonacular.com/food/wine"
_TIMEOUT = 12.0


def _get_api_key() -> str:
    return (os.environ.get("SPOONACULAR_API_KEY") or os.getenv("SPOONACULAR_API_KEY") or "").strip()


def _request(path: str, params: dict) -> dict | None:
    """GET a Spoonacular; devuelve JSON dict o None si falla/429/sin key."""
    api_key = _get_api_key()
    if not api_key:
        return None
    params = dict(params)
    params["apiKey"] = api_key
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    url = f"{_BASE}{path}?{query}"
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            r = client.get(url)
            if r.status_code == 429:
                print("[Spoonacular] Cuota excedida (429); intente más tarde.")
                return None
            if r.status_code != 200:
                print(f"[Spoonacular] HTTP {r.status_code}: {r.text[:200]}")
                return None
            return r.json()
    except httpx.HTTPError as e:
        print(f"[Spoonacular] Error de red: {e}")
        return None
    except Exception as e:
        print(f"[Spoonacular] Error: {e}")
        return None


def get_dish_pairing_for_wine(wine: str) -> dict:
    """
    Dado un vino (ej. "merlot", "malbec"), devuelve platos recomendados.
    Respuesta: { "ok": true, "pairings": [...], "text": "..." } o { "ok": false, "message": "..." }.
    """
    wine_clean = (wine or "").strip()
    if not wine_clean:
        return {"ok": False, "message": "Indica el nombre del vino para obtener maridajes."}
    data = _request("/dishes", {"wine": wine_clean})
    if data is None:
        if not _get_api_key():
            return {"ok": False, "message": "Servicio de maridaje no configurado. Contacta al administrador."}
        return {"ok": False, "message": "No se pudo obtener el maridaje ahora. Prueba más tarde o verifica la cuota de la API."}
    pairings = data.get("pairings") if isinstance(data, dict) else []
    text = (data.get("text") or "").strip()
    return {
        "ok": True,
        "pairings": pairings if isinstance(pairings, list) else [],
        "text": text or None,
    }


def get_wine_pairing_for_food(food: str) -> dict:
    """
    Dado un plato/ingrediente/cocina (ej. "steak", "salmon"), devuelve vinos recomendados.
    Respuesta: { "ok": true, "pairedWines": [...], "pairingText": "...", "productMatches": [...] } o error.
    """
    food_clean = (food or "").strip()
    if not food_clean:
        return {"ok": False, "message": "Indica un plato, ingrediente o tipo de cocina para recomendar vinos."}
    data = _request("/pairing", {"food": food_clean})
    if data is None:
        if not _get_api_key():
            return {"ok": False, "message": "Servicio de maridaje no configurado. Contacta al administrador."}
        return {"ok": False, "message": "No se pudo obtener la recomendación ahora. Prueba más tarde."}
    return {
        "ok": True,
        "pairedWines": data.get("pairedWines") or [],
        "pairingText": data.get("pairingText") or "",
        "productMatches": data.get("productMatches") or [],
    }


def get_wine_description(wine: str) -> dict:
    """
    Descripción breve del vino (ej. "merlot" → "Merlot is a dry red wine...").
    Útil para fichas de vino o tooltips.
    """
    wine_clean = (wine or "").strip()
    if not wine_clean:
        return {"ok": False, "message": "Indica el nombre del vino."}
    data = _request("/description", {"wine": wine_clean})
    if data is None:
        if not _get_api_key():
            return {"ok": False, "message": "Servicio no configurado."}
        return {"ok": False, "message": "No se pudo obtener la descripción."}
    desc = (data.get("wineDescription") or "").strip()
    return {"ok": True, "wineDescription": desc or None}
