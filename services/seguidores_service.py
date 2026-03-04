"""
Servicio de seguir / seguidores (comunidad Fase 6B).
Persistencia en data/seguidores.json.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SEGUIDORES_PATH = DATA_DIR / "seguidores.json"

# { "seguidores": { "username": ["follower1", "follower2"] }, "seguidos": { "username": ["user1", "user2"] } }
_data: dict = {}


def _load() -> dict:
    global _data
    if _data:
        return _data
    if SEGUIDORES_PATH.is_file():
        try:
            with open(SEGUIDORES_PATH, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = {}
    if "seguidores" not in _data:
        _data["seguidores"] = {}
    if "seguidos" not in _data:
        _data["seguidos"] = {}
    return _data


def _save() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(SEGUIDORES_PATH, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def seguir(quien_sigue: str, a_quien: str) -> bool:
    """quien_sigue empieza a seguir a a_quien. Devuelve True si se hizo (False si ya seguía o es el mismo)."""
    if not quien_sigue or not a_quien or quien_sigue.strip().lower() == a_quien.strip().lower():
        return False
    quien_sigue = quien_sigue.strip().lower()
    a_quien = a_quien.strip().lower()
    _load()
    seg = _data["seguidores"].setdefault(a_quien, [])
    if quien_sigue in seg:
        return False
    seg.append(quien_sigue)
    sig = _data["seguidos"].setdefault(quien_sigue, [])
    if a_quien not in sig:
        sig.append(a_quien)
    _save()
    return True


def dejar_de_seguir(quien: str, a_quien: str) -> bool:
    """Deja de seguir. Devuelve True si estaba siguiendo y se quitó."""
    if not quien or not a_quien:
        return False
    quien = quien.strip().lower()
    a_quien = a_quien.strip().lower()
    _load()
    seg = _data["seguidores"].get(a_quien, [])
    if quien in seg:
        seg.remove(quien)
        _data["seguidores"][a_quien] = seg
    sig = _data["seguidos"].get(quien, [])
    if a_quien in sig:
        sig.remove(a_quien)
        _data["seguidos"][quien] = sig
    _save()
    return True


def get_seguidores(username: str) -> list[str]:
    """Lista de usernames que siguen a este usuario."""
    _load()
    return list(_data["seguidores"].get(username.strip().lower(), []))


def get_seguidos(username: str) -> list[str]:
    """Lista de usernames que este usuario sigue."""
    _load()
    return list(_data["seguidos"].get(username.strip().lower(), []))


def sigue_a(quien: str, a_quien: str) -> bool:
    """True si quien sigue a a_quien."""
    if not quien or not a_quien:
        return False
    return a_quien.strip().lower() in get_seguidos(quien.strip().lower())
