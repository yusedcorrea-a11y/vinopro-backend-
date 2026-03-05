"""
Servicio de recomendaciones personalizadas por sesión.
Almacena historial de búsquedas, vinos vistos y votos (me gusta / no me gusta)
y genera sugerencias basadas en ello.
"""
import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORIAL_PATH = DATA_DIR / "historial_usuario.json"

# En memoria: session_id -> { "busquedas": [{"q": str, "keys": [str]}], "vistos": [str], "likes": set(str), "dislikes": set(str) }
_store: dict[str, dict] = {}
_MAX_BUSQUEDAS = 20
_MAX_VISTOS = 50
_MAX_LIKES_DISLIKES = 200


def _get_session(session_id: str) -> dict:
    if not session_id:
        return {}
    if session_id not in _store:
        _store[session_id] = {
            "busquedas": [],
            "vistos": [],
            "likes": set(),
            "dislikes": set(),
        }
    return _store[session_id]


def _persist():
    """Guarda en data/historial_usuario.json (sets como listas)."""
    try:
        to_save = {}
        for sid, data in _store.items():
            to_save[sid] = {
                "busquedas": data.get("busquedas", [])[-_MAX_BUSQUEDAS:],
                "vistos": list(data.get("vistos", []))[-_MAX_VISTOS:],
                "likes": list(data.get("likes", set())),
                "dislikes": list(data.get("dislikes", set())),
            }
        HISTORIAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORIAL_PATH, "w", encoding="utf-8") as f:
            json.dump(to_save, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _load():
    """Carga desde data/historial_usuario.json si existe."""
    if not HISTORIAL_PATH.is_file():
        return
    try:
        with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for sid, raw in data.items():
            _store[sid] = {
                "busquedas": raw.get("busquedas", [])[-_MAX_BUSQUEDAS:],
                "vistos": list(raw.get("vistos", []))[-_MAX_VISTOS:],
                "likes": set(raw.get("likes", [])),
                "dislikes": set(raw.get("dislikes", [])),
            }
    except Exception:
        pass


def registrar_busqueda(session_id: str, query: str, wine_keys: list[str] | None = None) -> None:
    """Registra una búsqueda del usuario y los vinos devueltos. Solo se guardan keys que sean strings."""
    s = _get_session(session_id)
    if not session_id:
        return
    keys_safe = [k for k in (list(wine_keys or [])[:10]) if isinstance(k, str) and (k or "").strip()]
    s["busquedas"] = (s.get("busquedas") or []) + [{"q": (query or "").strip(), "keys": keys_safe}]
    s["busquedas"] = s["busquedas"][-_MAX_BUSQUEDAS:]
    _persist()


def registrar_visto(session_id: str, wine_key: str) -> None:
    """Registra que el usuario vio un vino (ej. clic en más info o comprar)."""
    if not session_id or not wine_key:
        return
    s = _get_session(session_id)
    vistos = s.get("vistos") or []
    if wine_key in vistos:
        vistos.remove(wine_key)
    vistos.append(wine_key)
    s["vistos"] = vistos[-_MAX_VISTOS:]
    _persist()


def registrar_voto(session_id: str, wine_key: str, like: bool) -> None:
    """Registra me gusta (like=True) o no me gusta (like=False)."""
    if not session_id or not wine_key:
        return
    s = _get_session(session_id)
    likes = s.get("likes") or set()
    dislikes = s.get("dislikes") or set()
    if like:
        dislikes.discard(wine_key)
        likes.add(wine_key)
    else:
        likes.discard(wine_key)
        dislikes.add(wine_key)
    if len(likes) > _MAX_LIKES_DISLIKES:
        s["likes"] = set(list(likes)[-_MAX_LIKES_DISLIKES:])
    else:
        s["likes"] = likes
    if len(dislikes) > _MAX_LIKES_DISLIKES:
        s["dislikes"] = set(list(dislikes)[-_MAX_LIKES_DISLIKES:])
    else:
        s["dislikes"] = dislikes
    _persist()


def get_recomendaciones_personalizadas(
    session_id: str,
    vinos_dict: dict[str, Any],
    exclude_keys: list[str] | None = None,
    limite: int = 5,
) -> list[dict]:
    """
    Devuelve vinos recomendados para la sesión:
    - Prioriza por gustos (likes, búsquedas recientes: mismo tipo/región)
    - Excluye los ya mostrados (exclude_keys) y los dislikes.
    Return: [ {"key": str, "vino": dict}, ... ]
    """
    exclude = set(exclude_keys or [])
    s = _get_session(session_id)
    dislikes = s.get("dislikes") or set()
    exclude |= dislikes
    likes = s.get("likes") or set()
    busquedas = s.get("busquedas") or []
    vistos = s.get("vistos") or []

    # Construir candidatos: todos los vinos no excluidos
    candidatos: list[tuple[float, str, dict]] = []
    for key, vino in vinos_dict.items():
        if key in exclude or not isinstance(vino, dict):
            continue
        score = 0.0
        tipo = (vino.get("tipo") or "").strip().lower()
        region = (vino.get("region") or "").strip()
        uva = (vino.get("uva_principal") or "").strip()
        pais = (vino.get("pais") or "").strip()
        puntuacion = float(vino.get("puntuacion") or 0)

        if key in likes:
            score += 50
        if key in vistos:
            score += 5
        for b in busquedas[-5:]:
            keys_b = set(k for k in (b.get("keys") or []) if isinstance(k, str))
            if key in keys_b:
                score += 3
            for k in keys_b:
                v = vinos_dict.get(k) if isinstance(vinos_dict, dict) else None
                if isinstance(v, dict):
                    if (v.get("tipo") or "").strip().lower() == tipo:
                        score += 2
                    if (v.get("region") or "").strip() == region:
                        score += 2
                    if (v.get("uva_principal") or "").strip() and (v.get("uva_principal") or "").strip() == uva:
                        score += 1.5
                    if (v.get("pais") or "").strip() == pais:
                        score += 1
        candidatos.append((score, key, vino))
    candidatos.sort(key=lambda x: (-x[0], -float(x[2].get("puntuacion") or 0)))
    return [{"key": k, "vino": v} for _, k, v in candidatos[:limite]]


def get_vinos_similares(vinos_dict: dict[str, Any], wine_key: str, limite: int = 5) -> list[dict]:
    """
    Vinos similares al dado: misma región, misma uva o mismo tipo.
    Return: [ {"key": str, "vino": dict}, ... ]
    """
    ref = vinos_dict.get(wine_key) if isinstance(vinos_dict, dict) else None
    if not isinstance(ref, dict):
        return []
    tipo = (ref.get("tipo") or "").strip().lower()
    region = (ref.get("region") or "").strip()
    uva = (ref.get("uva_principal") or "").strip()
    resultados = []
    for key, vino in vinos_dict.items():
        if key == wine_key or not isinstance(vino, dict):
            continue
        t = (vino.get("tipo") or "").strip().lower()
        r = (vino.get("region") or "").strip()
        u = (vino.get("uva_principal") or "").strip()
        score = 0
        if region and r == region:
            score += 3
        if tipo and t == tipo:
            score += 2
        if uva and u == uva:
            score += 2
        if score > 0:
            resultados.append((score, key, vino))
    resultados.sort(key=lambda x: (-x[0], -float(x[2].get("puntuacion") or 0)))
    return [{"key": k, "vino": v} for _, k, v in resultados[:limite]]


# Cargar historial al importar (opcional)
_load()
