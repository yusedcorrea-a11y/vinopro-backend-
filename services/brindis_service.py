"""
Servicio de brindis del feed VINEROS.
Persistencia en data/brindis.json: { "post_id": ["username1", "username2", ...] }.
Un usuario solo cuenta una vez por post.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BRINDIS_PATH = DATA_DIR / "brindis.json"

_data: dict = {}


def _load() -> dict:
    global _data
    if _data:
        return _data
    if BRINDIS_PATH.is_file():
        try:
            with open(BRINDIS_PATH, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = {}
    if not _data:
        _data = {}
    return _data


def _save() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(BRINDIS_PATH, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_count(post_id: str) -> int:
    """Número de brindis (usuarios únicos) para un post."""
    if not (post_id or "").strip():
        return 0
    _load()
    users = _data.get((post_id or "").strip(), [])
    return len(users) if isinstance(users, list) else 0


def yo_brindi(post_id: str, username: str) -> bool:
    """True si el usuario ya ha brindado en este post."""
    if not (post_id or "").strip() or not (username or "").strip():
        return False
    _load()
    users = _data.get((post_id or "").strip(), [])
    if not isinstance(users, list):
        return False
    return (username or "").strip().lower() in [u.strip().lower() for u in users if u]


def add_brindis(post_id: str, username: str) -> int:
    """
    Registra un brindis del usuario en el post. Si ya brindó, no duplica.
    Devuelve el nuevo count del post.
    """
    post_id = (post_id or "").strip()
    username = (username or "").strip().lower()
    if not post_id or not username:
        return get_count(post_id)
    _load()
    users = _data.get(post_id, [])
    if not isinstance(users, list):
        users = []
    if username not in users:
        users.append(username)
        _data[post_id] = users
        _save()
    return len(users)
