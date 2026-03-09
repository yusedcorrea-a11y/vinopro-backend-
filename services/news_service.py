"""
Noticias de vino: GNews API con caché. Si no hay API key o falla, se usa contenido estático de canales_feed.
"""
import json
import os
import time
from pathlib import Path
from urllib.parse import quote

import httpx

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_PATH = DATA_DIR / "noticias_cache.json"
CACHE_TTL_SEC = 2 * 3600  # 2 horas

_cached: list[dict] | None = None
_cached_at: float = 0


def _fallback_noticias(limit: int = 20) -> list[dict]:
    """Noticias estáticas desde canales_feed.json (mismo formato que get_contenido_canal)."""
    from services import feed_service as feed_svc
    return feed_svc.get_contenido_canal("noticias", limit=limit)


def _load_cache() -> tuple[list[dict], float]:
    if not CACHE_PATH.is_file():
        return [], 0
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        articles = data.get("articles") if isinstance(data, dict) else []
        cached_at = float(data.get("cached_at", 0))
        if isinstance(articles, list):
            return articles, cached_at
    except Exception:
        pass
    return [], 0


def _save_cache(articles: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"cached_at": time.time(), "articles": articles}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _gnews_to_item(art: dict) -> dict:
    """Convierte un artículo GNews al formato canal (titulo, descripcion, link, fuente, imagen, created_at)."""
    from datetime import datetime
    pub = (art.get("publishedAt") or "").strip()
    ts = 0
    if pub:
        try:
            dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            ts = int(dt.timestamp())
        except Exception:
            pass
    if not ts:
        ts = int(time.time())
    source = (art.get("source") or {})
    name = (source.get("name") or "Noticias").strip() or "Noticias"
    return {
        "id": (art.get("id") or str(ts))[:80],
        "created_at": ts,
        "titulo": (art.get("title") or "Sin título").strip()[:300],
        "descripcion": (art.get("description") or "").strip()[:500],
        "link": (art.get("url") or "").strip()[:500],
        "fuente": name[:100],
        "badge": "Noticias",
        "imagen": (art.get("image") or "").strip()[:500] or None,
    }


def get_wine_news(limit: int = 20) -> list[dict]:
    """
    Devuelve noticias de vino. Si GNEWS_API_KEY está definida, usa GNews con caché 2h.
    Si no hay key o la API falla, devuelve noticias estáticas de canales_feed.
    Cada item: id, created_at, titulo, descripcion, link, fuente, badge, imagen.
    """
    global _cached, _cached_at
    now = time.time()
    if _cached is not None and (now - _cached_at) < CACHE_TTL_SEC:
        return _cached[:limit]
    cached_articles, cached_at = _load_cache()
    if cached_articles and (now - cached_at) < CACHE_TTL_SEC:
        _cached = cached_articles
        _cached_at = cached_at
        return _cached[:limit]

    # GNews exige el parámetro "apikey" (minúsculas) en la URL; el valor debe venir de la variable de entorno
    api_key = (os.environ.get("GNEWS_API_KEY") or os.getenv("GNEWS_API_KEY") or "").strip()
    if not api_key:
        print("[GNews] No se encontró GNEWS_API_KEY en el entorno; se usan noticias de respaldo.")
        return _fallback_noticias(limit)

    print(f"[GNews] Enviando petición con API key (longitud {len(api_key)})")
    # Búsqueda enológica restrictiva: evita "Wine" (Cavaliers/NBA) con NOT; prioriza términos del sector
    query = '(vino OR enología OR bodega OR viticultura OR sommelier) AND NOT NBA AND NOT "Cleveland Cavaliers" AND NOT basketball'
    apikey_encoded = quote(api_key, safe="")
    query_encoded = quote(query, safe="")
    url = f"https://gnews.io/api/v4/search?q={query_encoded}&lang=es&max=20&apikey={apikey_encoded}"
    raw = []
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(url)
            if r.status_code == 400:
                print(f"DEBUG GNews Error: {r.text}")
                return _fallback_noticias(limit)
            if r.status_code != 200:
                print(f"[WARN] GNews API HTTP {r.status_code}: {r.text[:200]}")
                return _fallback_noticias(limit)
            try:
                data = r.json()
            except Exception as e:
                print(f"[WARN] GNews API JSON error: {e}")
                return _fallback_noticias(limit)
            raw = data.get("articles") if isinstance(data, dict) else []
    except httpx.HTTPError as e:
        print(f"[WARN] GNews API error: {e}")
        return _fallback_noticias(limit)
    except Exception as e:
        print(f"[WARN] GNews API error: {e}")
        return _fallback_noticias(limit)

    if not isinstance(raw, list) or len(raw) == 0:
        try:
            # Fallback: búsqueda por frase enológica en español
            query_fallback = quote("cultura del vino", safe="")
            url_es = f"https://gnews.io/api/v4/search?q={query_fallback}&lang=es&max=20&apikey={apikey_encoded}"
            with httpx.Client(timeout=12.0) as client:
                r2 = client.get(url_es)
                if r2.status_code == 400:
                    print(f"DEBUG GNews Error (cultura del vino): {r2.text}")
                elif r2.is_success:
                    data = r2.json()
                    raw = data.get("articles") if isinstance(data, dict) else []
        except Exception:
            pass
    if not isinstance(raw, list) or len(raw) == 0:
        return _fallback_noticias(limit)

    items = []
    for a in raw:
        if not isinstance(a, dict):
            continue
        items.append(_gnews_to_item(a))
    items.sort(key=lambda x: -(x.get("created_at") or 0))
    _cached = items
    _cached_at = now
    _save_cache(items)
    return items[:limit]
