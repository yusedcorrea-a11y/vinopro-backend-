"""
Servicio freemium: límite 30 botellas en Mi Bodega para usuarios gratis.
Usuarios PRO (listados en data/usuarios_pro.json por session_id) bodega ilimitada.
"""
import json
import os

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
BODEGAS_PATH = os.path.join(DATA_FOLDER, "bodegas.json")
USUARIOS_PRO_PATH = os.path.join(DATA_FOLDER, "usuarios_pro.json")

LIMITE_GRATIS = 30


def _load_bodegas() -> dict:
    if os.path.exists(BODEGAS_PATH):
        try:
            with open(BODEGAS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _load_pro_users() -> set:
    data = _load_pro_data()
    return set((s or "").strip() for s in data.get("pro_users", []) if s)


def _load_pro_data() -> dict:
    """Carga el JSON completo de usuarios_pro (para leer y escribir)."""
    if os.path.exists(USUARIOS_PRO_PATH):
        try:
            with open(USUARIOS_PRO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"pro_users": []}


def _save_pro_data(data: dict) -> None:
    os.makedirs(os.path.dirname(USUARIOS_PRO_PATH) or ".", exist_ok=True)
    with open(USUARIOS_PRO_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_pro_user(session_id: str) -> bool:
    """Añade session_id a pro_users si no está. Devuelve True si se añadió."""
    if not (session_id or session_id.strip()):
        return False
    sid = session_id.strip()
    data = _load_pro_data()
    lst = data.get("pro_users", [])
    if sid in lst:
        return False
    lst.append(sid)
    data["pro_users"] = lst
    _save_pro_data(data)
    return True


def is_pro(session_id: str) -> bool:
    """True si el session_id está en la lista de usuarios PRO."""
    if session_id is None or not isinstance(session_id, str):
        return False
    if not session_id.strip():
        return False
    return session_id.strip() in _load_pro_users()


def count_botellas(session_id: str) -> int:
    """Total de botellas (suma de cantidades) en la bodega del usuario."""
    data = _load_bodegas()
    if session_id not in data or "botellas" not in data[session_id]:
        return 0
    return sum(int(b.get("cantidad", 1)) for b in data[session_id]["botellas"])


def puede_anadir_botella(session_id: str, cantidad: int = 1) -> tuple[bool, str]:
    """
    Devuelve (True, "") si puede añadir; (False, mensaje) si supera el límite.
    Usuarios PRO no tienen límite.
    """
    if session_id is None or not isinstance(session_id, str) or not session_id.strip():
        return False, "Sesión no válida."
    session_id = session_id.strip()
    if is_pro(session_id):
        return True, ""
    usado = count_botellas(session_id)
    nuevo_total = usado + max(1, int(cantidad))
    if nuevo_total > LIMITE_GRATIS:
        return False, (
            f"Límite del plan Gratis alcanzado ({usado}/{LIMITE_GRATIS} botellas). "
            "Pasa a PRO para bodega ilimitada."
        )
    return True, ""
