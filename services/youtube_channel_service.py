"""
Último vídeo para embed en VINEROS (sin API key de YouTube):
1) ID fijo en JSON (youtube_embed_video_id)
2) Primera entrada del RSS de una lista (youtube_playlist_id)
3) Primera entrada del RSS de un canal (youtube_channel_uc)

Caché en memoria para no saturar a YouTube.
"""
from __future__ import annotations

import re
import time
from typing import Optional

import httpx

_UA = "Mozilla/5.0 (compatible; VinoProIA/1.0; +https://vinoproia.com) AppleWebKit/537.36"
_NS_FAIL_SHORT = 90.0
_NS_FAIL_LONG = 400.0
_CACHE_VID: dict[str, tuple[float, Optional[str]]] = {}
_TTL = 600.0

_RE_VIDEO_XML = re.compile(r"<yt:videoId>([a-zA-Z0-9_-]{11})</yt:videoId>")
_RE_STATIC_VIDEO = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def _now() -> float:
    return time.time()


def _cache_get(key: str) -> tuple[bool, Optional[str]]:
    """(hit, value_or_None_if_cached_miss)."""
    t = _now()
    if key in _CACHE_VID and _CACHE_VID[key][0] > t:
        return True, _CACHE_VID[key][1]
    return False, None


def _cache_set(key: str, value: Optional[str], ttl: float = _TTL) -> None:
    _CACHE_VID[key] = (_now() + ttl, value)


async def _fetch_first_video_id_from_feed(url: str, cache_key: str) -> Optional[str]:
    hit, val = _cache_get(cache_key)
    if hit:
        return val
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": _UA})
        if r.status_code != 200:
            _cache_set(cache_key, None, _NS_FAIL_SHORT)
            return None
        m = _RE_VIDEO_XML.search(r.text)
        if not m:
            _cache_set(cache_key, None, _NS_FAIL_LONG)
            return None
        vid = m.group(1)
        _cache_set(cache_key, vid, _TTL)
        return vid
    except Exception:
        _cache_set(cache_key, None, _NS_FAIL_SHORT)
        return None


async def get_latest_video_id_from_playlist(playlist_id: str) -> Optional[str]:
    pid = (playlist_id or "").strip()
    if not pid or len(pid) < 6:
        return None
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={pid}"
    return await _fetch_first_video_id_from_feed(url, "pl:" + pid)


async def get_latest_upload_video_id(channel_uc: str) -> Optional[str]:
    uc = (channel_uc or "").strip()
    if not uc.startswith("UC") or len(uc) < 15:
        return None
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={uc}"
    return await _fetch_first_video_id_from_feed(url, "ch:" + uc)


async def resolve_embed_video_id(
    static_video_id: str = "",
    playlist_id: str = "",
    channel_uc: str = "",
) -> Optional[str]:
    """Orden: vídeo fijo → lista RSS → canal RSS."""
    sid = (static_video_id or "").strip()
    if sid and _RE_STATIC_VIDEO.match(sid):
        return sid
    pl = (playlist_id or "").strip()
    if pl:
        v = await get_latest_video_id_from_playlist(pl)
        if v:
            return v
    uc = (channel_uc or "").strip()
    if uc:
        v = await get_latest_upload_video_id(uc)
        if v:
            return v
    return None
