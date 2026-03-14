"""
Servicio de feed de actividad (comunidad Fase 6B).
Persistencia en data/actividad.json.
"""
import json
import time
import uuid
from pathlib import Path

from models.comunidad import Actividad

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ACTIVIDAD_PATH = DATA_DIR / "actividad.json"
CANALES_FEED_PATH = DATA_DIR / "canales_feed.json"

LISTA_CANALES = ["para_ti", "noticias", "eventos", "enoturismo", "equipamiento", "vineros"]

_lista: list[dict] = []
_canales_data: dict = {}


def _load() -> list[dict]:
    global _lista
    if _lista:
        return _lista
    if ACTIVIDAD_PATH.is_file():
        try:
            with open(ACTIVIDAD_PATH, "r", encoding="utf-8") as f:
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
        with open(ACTIVIDAD_PATH, "w", encoding="utf-8") as f:
            json.dump(_lista, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def add_actividad(
    username: str,
    tipo: str,
    vino_key: str,
    vino_nombre: str = "",
    score: int | None = None,
    titulo: str = "",
    texto: str = "",
    link: str = "",
) -> str:
    """
    Añade una actividad al feed.
    tipo: "valoracion" | "probado" | "deseado" | "evento".
    Para tipo "evento", se usan titulo, texto y link (vino_key puede ser vacío o "_evento").
    Devuelve el id de la actividad.
    """
    if not username or not tipo:
        return ""
    if tipo != "evento" and not vino_key:
        return ""
    username = username.strip().lower()
    now = int(time.time())
    id_act = str(uuid.uuid4())[:8]
    _load()
    entry = {
        "id": id_act,
        "username": username,
        "tipo": tipo,
        "vino_key": (vino_key or "").strip()[:200],
        "vino_nombre": (vino_nombre or "").strip()[:200],
        "score": score,
        "created_at": now,
    }
    if tipo == "evento":
        entry["titulo"] = (titulo or "").strip()[:200]
        entry["texto"] = (texto or "").strip()[:1000]
        entry["link"] = (link or "").strip()[:500]
    _lista.append(entry)
    _save()
    return id_act


def get_eventos_destacados(limit: int = 10) -> list[dict]:
    """Actividades de tipo 'evento' (publicaciones de partners/organizadores), más recientes primero."""
    _load()
    eventos = [a for a in _lista if (a.get("tipo") or "") == "evento"]
    eventos.sort(key=lambda x: -(x.get("created_at") or 0))
    return eventos[:limit]


def get_feed_para_usuario(usernames_seguidos: list[str], limit: int = 50) -> list[dict]:
    """
    Devuelve actividades de los usuarios que sigue, ordenadas por fecha (más reciente primero).
    usernames_seguidos: lista de usernames a los que sigue el usuario actual.
    """
    if not usernames_seguidos:
        return []
    seguidos_set = set(u.strip().lower() for u in usernames_seguidos)
    _load()
    filtradas = [a for a in _lista if (a.get("username") or "").strip().lower() in seguidos_set]
    filtradas.sort(key=lambda x: -(x.get("created_at") or 0))
    return filtradas[:limit]


def get_actividad_de_usuario(username: str, limit: int = 30) -> list[dict]:
    """Actividad reciente de un usuario (para su perfil)."""
    if not username:
        return []
    username = username.strip().lower()
    _load()
    filtradas = [a for a in _lista if (a.get("username") or "").strip().lower() == username]
    filtradas.sort(key=lambda x: -(x.get("created_at") or 0))
    return filtradas[:limit]


def _load_canales() -> dict:
    global _canales_data
    if _canales_data:
        return _canales_data
    if CANALES_FEED_PATH.is_file():
        try:
            with open(CANALES_FEED_PATH, "r", encoding="utf-8") as f:
                _canales_data = json.load(f)
            if not isinstance(_canales_data, dict):
                _canales_data = {}
        except Exception:
            _canales_data = {}
    else:
        _canales_data = {}
    return _canales_data


def get_contenido_canal(canal: str, limit: int = 20) -> list[dict]:
    """
    Contenido estático de un canal (noticias, eventos, enoturismo, equipamiento).
    Cada item: id, created_at, titulo, descripcion, link, fuente, badge.
    Para "eventos" solo devuelve los del JSON; la API mezclará con get_eventos_destacados.
    """
    if canal not in ("noticias", "eventos", "enoturismo", "equipamiento"):
        return []
    data = _load_canales()
    raw = data.get(canal)
    if not isinstance(raw, list):
        return []
    items = [x for x in raw if isinstance(x, dict)]
    items.sort(key=lambda x: -(x.get("created_at") or 0))
    return items[:limit]
