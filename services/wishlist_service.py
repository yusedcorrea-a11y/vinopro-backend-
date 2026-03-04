"""
Wishlist: lista "Quiero probar" por sesión. Persistencia en data/wishlist.json.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WISHLIST_PATH = DATA_DIR / "wishlist.json"

# session_id -> [ wine_key, ... ]
_store: dict[str, list[str]] = {}
_MAX_PER_SESSION = 200


def _load() -> None:
    global _store
    if _store and not (len(_store) == 0 and WISHLIST_PATH.is_file()):
        return
    if WISHLIST_PATH.is_file():
        try:
            with open(WISHLIST_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            _store = {k: list(v)[:_MAX_PER_SESSION] for k, v in (raw or {}).items() if isinstance(v, list)}
        except Exception:
            _store = {}
    else:
        _store = {}


def _save() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(WISHLIST_PATH, "w", encoding="utf-8") as f:
            json.dump(_store, f, ensure_ascii=False)
    except Exception:
        pass


def add(session_id: str, wine_key: str) -> bool:
    """Añade un vino a la wishlist. Devuelve True si se añadió."""
    if not session_id or not wine_key:
        return False
    _load()
    wine_key = wine_key.strip()
    lst = _store.setdefault(session_id, [])
    if wine_key in lst:
        return False
    lst.append(wine_key)
    _store[session_id] = lst[-_MAX_PER_SESSION:]
    _save()
    return True


def remove(session_id: str, wine_key: str) -> bool:
    """Quita un vino de la wishlist. Devuelve True si estaba y se quitó."""
    if not session_id:
        return False
    _load()
    wine_key = wine_key.strip()
    lst = _store.get(session_id, [])
    if wine_key not in lst:
        return False
    lst.remove(wine_key)
    _store[session_id] = lst
    _save()
    return True


def has(session_id: str, wine_key: str) -> bool:
    """Indica si el vino está en la wishlist del usuario."""
    if not session_id or not wine_key:
        return False
    _load()
    return wine_key.strip() in _store.get(session_id, [])


def get_list(session_id: str) -> list[str]:
    """Devuelve la lista de wine_key de la wishlist del usuario."""
    if not session_id:
        return []
    _load()
    return list(_store.get(session_id, []))


_load()
