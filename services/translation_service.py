"""
Traducción en tiempo real para la comunidad (Futuros Vineros).
Usa LibreTranslate (gratuito): público o URL en LIBRETRANSLATE_URL.
Así un vinero en Rusia puede escribir en ruso y un usuario en India verlo en hindi.
"""
import os
import asyncio
from typing import Optional

# Códigos soportados por LibreTranslate (normalizar zh -> zh-Hans para la app)
IDIOMAS_COMUNIDAD = [
    "es", "en", "fr", "de", "it", "pt", "ru", "hi", "ar", "zh", "ja", "ko",
    "tr", "pl", "nl", "he", "th", "vi", "id", "uk", "pt-BR", "zh-Hans", "zh-Hant",
]
# Mapeo app -> LibreTranslate
_NORMALIZAR = {"zh": "zh-Hans"}


def _normalize_lang(code: str) -> str:
    c = (code or "en").strip().lower()
    return _NORMALIZAR.get(c, c)


async def traducir(
    texto: str,
    idioma_destino: str,
    idioma_origen: Optional[str] = None,
) -> str:
    """
    Traduce un texto al idioma destino.
    idioma_origen: opcional; si no se pasa, LibreTranslate auto-detecta.
    Devuelve el texto original si falla o está vacío.
    """
    texto = (texto or "").strip()
    if not texto:
        return ""
    target = _normalize_lang(idioma_destino)
    source = _normalize_lang(idioma_origen) if idioma_origen else "auto"
    base_url = (os.environ.get("LIBRETRANSLATE_URL") or "https://libretranslate.com").rstrip("/")
    api_key = (os.environ.get("LIBRETRANSLATE_API_KEY") or "").strip()

    try:
        import httpx
    except ImportError:
        return texto

    payload = {
        "q": texto[:5000],  # límite razonable
        "source": source,
        "target": target,
    }
    if api_key:
        payload["api_key"] = api_key

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{base_url}/translate", json=payload)
            if r.status_code == 200:
                data = r.json()
                out = (data.get("translatedText") or "").strip()
                return out if out else texto
    except Exception:
        pass
    return texto


async def traducir_lote(
    textos: list[str],
    idioma_destino: str,
    idioma_origen: Optional[str] = None,
) -> list[str]:
    """
    Traduce una lista de textos al idioma destino.
    Hace una petición por texto (LibreTranslate no tiene batch nativo) con concurrencia limitada.
    """
    if not textos:
        return []
    target = _normalize_lang(idioma_destino)
    source = _normalize_lang(idioma_origen) if idioma_origen else "auto"
    base_url = (os.environ.get("LIBRETRANSLATE_URL") or "https://libretranslate.com").rstrip("/")
    api_key = (os.environ.get("LIBRETRANSLATE_API_KEY") or "").strip()

    try:
        import httpx
    except ImportError:
        return list(textos)

    async def one(q: str) -> str:
        if not (q or "").strip():
            return q or ""
        payload = {"q": (q or "")[:5000], "source": source, "target": target}
        if api_key:
            payload["api_key"] = api_key
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(f"{base_url}/translate", json=payload)
                if r.status_code == 200:
                    out = (r.json().get("translatedText") or "").strip()
                    return out or q
        except Exception:
            pass
        return q or ""

    # Máximo 5 concurrentes para no saturar la API gratuita
    sem = asyncio.Semaphore(5)

    async def limited(t: str):
        async with sem:
            return await one(t)

    results = await asyncio.gather(*[limited(t) for t in textos])
    return list(results)
