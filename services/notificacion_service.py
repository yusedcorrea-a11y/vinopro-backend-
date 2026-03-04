"""
Servicio de notificaciones (comunidad Fase 6B).
Persistencia en data/notificaciones.json.
"""
import json
import time
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
NOTIF_PATH = DATA_DIR / "notificaciones.json"

# { "username": [ { "id", "tipo", "from_username", "ref_id", "leida", "created_at" } ] }
_data: dict = {}


def _load() -> dict:
    global _data
    if _data:
        return _data
    if NOTIF_PATH.is_file():
        try:
            with open(NOTIF_PATH, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = {}
    return _data


def _save() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(NOTIF_PATH, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def add(username: str, tipo: str, from_username: str = "", ref_id: str = "") -> str:
    """Añade notificación para username. Devuelve id."""
    if not username:
        return ""
    username = username.strip().lower()
    from_username = (from_username or "").strip().lower()
    _load()
    id_ = str(uuid.uuid4())[:8]
    _data.setdefault(username, []).append({
        "id": id_,
        "tipo": tipo,
        "from_username": from_username,
        "ref_id": ref_id,
        "leida": False,
        "created_at": int(time.time()),
    })
    _save()
    return id_


def get_no_leidas(username: str) -> list[dict]:
    """Notificaciones no leídas del usuario."""
    if not username:
        return []
    _load()
    lista = _data.get(username.strip().lower(), [])
    return [n for n in lista if not n.get("leida")]


def get_todas(username: str, limit: int = 50) -> list[dict]:
    """Todas las notificaciones, más recientes primero."""
    if not username:
        return []
    _load()
    lista = _data.get(username.strip().lower(), [])
    lista = sorted(lista, key=lambda x: -(x.get("created_at") or 0))
    return lista[:limit]


def marcar_leidas(username: str, ids: list[str] | None = None) -> None:
    """Marca como leídas. Si ids es None, marca todas."""
    if not username:
        return
    username = username.strip().lower()
    _load()
    lista = _data.get(username, [])
    for n in lista:
        if ids is None or n.get("id") in (ids or []):
            n["leida"] = True
    _save()
