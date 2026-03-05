"""
Chat entre vineros. Cada usuario escribe en su idioma; la app traduce al idioma del lector.
Persistencia: data/chat_mensajes.json
"""
import json
import time
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHAT_PATH = DATA_DIR / "chat_mensajes.json"

_data: dict = {}  # { "conversations": { "user1|user2": [ { id, from_username, texto, created_at }, ... ] } }


def _load() -> dict:
    global _data
    if _data:
        return _data
    if CHAT_PATH.is_file():
        try:
            with open(CHAT_PATH, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = {}
    if "conversations" not in _data:
        _data["conversations"] = {}
    return _data


def _save() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CHAT_PATH, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _conv_key(u1: str, u2: str) -> str:
    """Clave única de conversación (orden alfabético)."""
    a, b = (u1 or "").strip().lower(), (u2 or "").strip().lower()
    if a > b:
        a, b = b, a
    return f"{a}|{b}" if a and b else ""


def enviar_mensaje(from_username: str, to_username: str, texto: str) -> dict | None:
    """
    Envía un mensaje de from_username a to_username.
    texto se guarda en el idioma original del remitente.
    Devuelve el mensaje creado o None si falla.
    """
    from_username = (from_username or "").strip().lower()
    to_username = (to_username or "").strip().lower()
    texto = (texto or "").strip()[:2000]
    if not from_username or not to_username or from_username == to_username or not texto:
        return None
    key = _conv_key(from_username, to_username)
    if not key:
        return None
    _load()
    if key not in _data["conversations"]:
        _data["conversations"][key] = []
    msg = {
        "id": str(uuid.uuid4())[:12],
        "from_username": from_username,
        "texto": texto,
        "created_at": int(time.time()),
    }
    _data["conversations"][key].append(msg)
    _save()
    return msg


def get_mensajes(username: str, with_username: str, limit: int = 100) -> list[dict]:
    """
    Devuelve los mensajes de la conversación entre username y with_username (orden cronológico).
    Cada mensaje: { id, from_username, texto, created_at }. texto en idioma original del remitente.
    """
    username = (username or "").strip().lower()
    with_username = (with_username or "").strip().lower()
    key = _conv_key(username, with_username)
    if not key:
        return []
    _load()
    msgs = _data["conversations"].get(key, [])
    msgs = sorted(msgs, key=lambda m: m.get("created_at", 0))
    return msgs[-limit:] if limit else msgs


def get_conversaciones(username: str, limit: int = 50) -> list[dict]:
    """
    Lista de conversaciones del usuario: cada una con other_username, last_message (texto), last_at.
    Ordenado por last_at descendente.
    """
    username = (username or "").strip().lower()
    if not username:
        return []
    _load()
    out = []
    for key, msgs in _data["conversations"].items():
        if not msgs:
            continue
        parts = key.split("|")
        if len(parts) != 2:
            continue
        other = parts[1] if parts[0] == username else parts[0]
        last = msgs[-1]
        out.append({
            "other_username": other,
            "last_message": (last.get("texto") or "")[:80],
            "last_at": last.get("created_at", 0),
            "from_username": last.get("from_username", ""),
        })
    out.sort(key=lambda x: x["last_at"], reverse=True)
    return out[:limit]
