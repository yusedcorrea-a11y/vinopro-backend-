"""
Servicio de perfiles de usuario (comunidad Fase 6B).
Persistencia en data/usuarios_perfiles.json.
"""
import json
import re
import time
from pathlib import Path

from models.comunidad import PerfilUsuario

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PERFILES_PATH = DATA_DIR / "usuarios_perfiles.json"

# { "profiles": [ {...} ], "session_to_username": { "session_id": "username" } }
_data: dict = {}
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


def _load() -> dict:
    global _data
    if _data:
        return _data
    if PERFILES_PATH.is_file():
        try:
            with open(PERFILES_PATH, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = {}
    if "profiles" not in _data:
        _data["profiles"] = []
    if "session_to_username" not in _data:
        _data["session_to_username"] = {}
    return _data


def _save() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(PERFILES_PATH, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def username_valido(username: str) -> bool:
    """Usuario 3-30 caracteres alfanuméricos o _."""
    return bool(username and _USERNAME_RE.match(username.strip()))


def crear_perfil(session_id: str, username: str, bio: str = "", ubicacion: str = "") -> tuple[bool, str]:
    """
    Crea perfil para esta sesión. username debe ser único.
    Devuelve (True, "") o (False, "mensaje_error").
    """
    if not session_id:
        return False, "Sesión requerida"
    username = (username or "").strip().lower()
    if not username_valido(username):
        return False, "Usuario inválido (3-30 caracteres, letras, números y _)"
    _load()
    for p in _data["profiles"]:
        if (p.get("username") or "").lower() == username:
            return False, "Usuario ya existe"
        if p.get("session_id") == session_id:
            return False, "Esta sesión ya tiene un perfil"
    now = int(time.time())
    _data["profiles"].append({
        "username": username,
        "session_id": session_id,
        "bio": (bio or "").strip()[:500],
        "ubicacion": (ubicacion or "").strip()[:200],
        "avatar_path": "",
        "privado": False,
        "created_at": now,
    })
    _data["session_to_username"][session_id] = username
    _save()
    return True, ""


def get_perfil_por_username(username: str) -> PerfilUsuario | None:
    """Devuelve el perfil público por username o None."""
    _load()
    username = (username or "").strip().lower()
    for p in _data["profiles"]:
        if (p.get("username") or "").lower() == username:
            return PerfilUsuario.from_dict(p)
    return None


def get_username_por_session(session_id: str) -> str | None:
    """Devuelve el username asociado a esta sesión o None."""
    _load()
    return _data["session_to_username"].get(session_id)


def get_perfil_por_session(session_id: str) -> PerfilUsuario | None:
    """Devuelve el perfil del usuario actual (por sesión) o None."""
    username = get_username_por_session(session_id)
    if not username:
        return None
    return get_perfil_por_username(username)


def actualizar_perfil(session_id: str, bio: str | None = None, ubicacion: str | None = None, privado: bool | None = None) -> bool:
    """Actualiza bio, ubicación o privado del perfil de esta sesión."""
    perfil = get_perfil_por_session(session_id)
    if not perfil:
        return False
    _load()
    for p in _data["profiles"]:
        if p.get("username") == perfil.username:
            if bio is not None:
                p["bio"] = (bio or "").strip()[:500]
            if ubicacion is not None:
                p["ubicacion"] = (ubicacion or "").strip()[:200]
            if privado is not None:
                p["privado"] = bool(privado)
            _save()
            return True
    return False


def existe_username(username: str) -> bool:
    """True si el username ya está registrado."""
    return get_perfil_por_username(username) is not None
