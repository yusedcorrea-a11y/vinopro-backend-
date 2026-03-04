"""
Valoraciones de usuarios: puntuación 1-5 y nota de cata por vino.
Persistencia en data/valoraciones.json. Una valoración por (session_id, wine_key); se actualiza si repite.
Fase 6B: opcional username, id, foto_path para comunidad.
"""
import json
import time
import uuid
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
VALORACIONES_PATH = DATA_DIR / "valoraciones.json"

# En memoria: lista de { "wine_key", "session_id", "score", "note", "created_at", "username?", "id?", "foto_path?" }
_lista: list[dict[str, Any]] = []


def _load() -> list[dict]:
    global _lista
    if _lista:
        return _lista
    if VALORACIONES_PATH.is_file():
        try:
            with open(VALORACIONES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            _lista = data if isinstance(data, list) else []
        except Exception:
            _lista = []
    else:
        _lista = []
    return _lista


def _save() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(VALORACIONES_PATH, "w", encoding="utf-8") as f:
            json.dump(_lista, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def add_or_update(
    session_id: str,
    wine_key: str,
    score: int,
    note: str = "",
    username: str | None = None,
    foto_path: str | None = None,
) -> str | None:
    """
    Añade o actualiza la valoración de un usuario (session_id) para un vino.
    score: 1-5. note: opcional. username/foto_path para comunidad (Fase 6B).
    Devuelve el id de la valoración (para editar/borrar).
    """
    if not session_id or not wine_key:
        return None
    score = max(1, min(5, int(score)))
    note = (note or "").strip()[:2000]
    _load()
    for i, r in enumerate(_lista):
        if r.get("session_id") == session_id and r.get("wine_key") == wine_key:
            _lista[i] = {
                "wine_key": wine_key,
                "session_id": session_id,
                "score": score,
                "note": note,
                "created_at": r.get("created_at"),
                "id": r.get("id") or str(uuid.uuid4())[:8],
                "username": (username or "").strip() or r.get("username", ""),
                "foto_path": (foto_path or "").strip() or r.get("foto_path", ""),
            }
            _save()
            return _lista[i].get("id")
    now = int(time.time())
    id_ = str(uuid.uuid4())[:8]
    _lista.append({
        "wine_key": wine_key,
        "session_id": session_id,
        "score": score,
        "note": note,
        "created_at": now,
        "id": id_,
        "username": (username or "").strip(),
        "foto_path": (foto_path or "").strip(),
    })
    _save()
    return id_


def get_summary(wine_key: str, session_id: str | None = None) -> dict[str, Any]:
    """
    Devuelve para un vino: average (float 1-5), count (int), y si session_id viene, user_rating (score, note).
    """
    _load()
    ratings = [r for r in _lista if r.get("wine_key") == wine_key]
    count = len(ratings)
    if not count:
        out = {"average": 0.0, "count": 0}
        if session_id:
            out["user_rating"] = None
        return out
    total = sum(r.get("score", 0) for r in ratings)
    average = round(total / count, 1)
    out = {"average": average, "count": count}
    if session_id:
        user_r = next((r for r in ratings if r.get("session_id") == session_id), None)
        if user_r:
            out["user_rating"] = {
                "score": user_r["score"],
                "note": user_r.get("note") or "",
                "id": user_r.get("id") or "",
                "username": user_r.get("username") or "",
            }
        else:
            out["user_rating"] = None
    return out


def get_recent_notes(wine_key: str, limit: int = 5) -> list[dict[str, Any]]:
    """Últimas valoraciones con nota (para mostrar en ficha de vino). Incluye username si existe (comunidad)."""
    _load()
    with_notes = [r for r in _lista if r.get("wine_key") == wine_key and (r.get("note") or "").strip()]
    with_notes.sort(key=lambda x: -(x.get("created_at") or 0))
    return [
        {
            "score": r.get("score"),
            "note": (r.get("note") or "").strip(),
            "created_at": r.get("created_at"),
            "username": r.get("username") or None,
        }
        for r in with_notes[:limit]
    ]


def get_valoracion_por_id(session_id: str, id_val: str) -> dict[str, Any] | None:
    """Obtiene una valoración por id; solo si pertenece a session_id."""
    _load()
    for r in _lista:
        if r.get("id") == id_val and r.get("session_id") == session_id:
            return r
    return None


def delete_valoracion(session_id: str, id_val: str) -> bool:
    """Elimina una valoración por id si pertenece a session_id. Devuelve True si se eliminó."""
    _load()
    for i, r in enumerate(_lista):
        if r.get("id") == id_val and r.get("session_id") == session_id:
            _lista.pop(i)
            _save()
            return True
    return False


def get_valoraciones_por_session(session_id: str) -> list[dict[str, Any]]:
    """Todas las valoraciones del usuario (para mi perfil)."""
    _load()
    out = [r for r in _lista if r.get("session_id") == session_id]
    out.sort(key=lambda x: -(x.get("created_at") or 0))
    return out


def get_valoraciones_por_username(username: str, limit: int = 50) -> list[dict[str, Any]]:
    """Valoraciones públicas de un usuario (para perfil público)."""
    if not username:
        return []
    _load()
    out = [r for r in _lista if (r.get("username") or "").strip().lower() == username.strip().lower()]
    out.sort(key=lambda x: -(x.get("created_at") or 0))
    return out[:limit]


# Cargar al importar
_load()
