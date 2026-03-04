"""
Límite diario de registros (añadir botella / registrar vino) por sesión.
Niveles: nuevo (<20 total) 10/día, normal (20-99) 50/día, verificado (100+) 200/día, PRO sin límite.
"""
import json
import os
from datetime import date

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
REGISTROS_DIARIOS_PATH = os.path.join(DATA_FOLDER, "registros_diarios.json")
USUARIOS_REPUTACION_PATH = os.path.join(DATA_FOLDER, "usuarios_reputacion.json")

LIMITE_NUEVO = 10
LIMITE_NORMAL = 50
LIMITE_VERIFICADO = 200


def _load_registros_diarios() -> dict:
    if os.path.exists(REGISTROS_DIARIOS_PATH):
        try:
            with open(REGISTROS_DIARIOS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_registros_diarios(data: dict) -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(REGISTROS_DIARIOS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_reputacion() -> dict:
    if os.path.exists(USUARIOS_REPUTACION_PATH):
        try:
            with open(USUARIOS_REPUTACION_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_reputacion(data: dict) -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(USUARIOS_REPUTACION_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _hoy() -> str:
    return date.today().isoformat()


def _get_nivel(registros_totales: int, es_pro: bool) -> str:
    if es_pro:
        return "pro"
    if registros_totales < 20:
        return "nuevo"
    if registros_totales < 100:
        return "normal"
    return "verificado"


def _limite_para_nivel(nivel: str) -> int:
    if nivel == "pro":
        return 999999
    if nivel == "nuevo":
        return LIMITE_NUEVO
    if nivel == "verificado":
        return LIMITE_VERIFICADO
    return LIMITE_NORMAL


def get_registros_hoy(session_id: str) -> int:
    """Cuenta de registros (añadir botella / registrar vino) hoy para esta sesión."""
    if not (session_id or "").strip():
        return 0
    data = _load_registros_diarios()
    hoy = _hoy()
    if hoy not in data:
        return 0
    return int(data[hoy].get(session_id.strip(), 0))


def get_estado_reputacion(session_id: str) -> tuple[int, str]:
    """Devuelve (registros_totales, nivel) para la sesión."""
    if not (session_id or "").strip():
        return 0, "nuevo"
    try:
        from services import freemium_service as freemium_svc
        es_pro = freemium_svc.is_pro(session_id.strip())
    except Exception:
        es_pro = False
    data = _load_reputacion()
    rec = data.get(session_id.strip(), {})
    total = int(rec.get("registros_totales", 0))
    nivel = _get_nivel(total, es_pro)
    return total, nivel


def puede_registrar_hoy(session_id: str) -> tuple[bool, str]:
    """
    True si puede hacer un registro más hoy.
    Devuelve (True, "") o (False, "limite_diario").
    """
    if not (session_id or "").strip():
        return False, "limite_diario"
    sid = session_id.strip()
    _, nivel = get_estado_reputacion(sid)
    limite = _limite_para_nivel(nivel)
    usados = get_registros_hoy(sid)
    if usados >= limite:
        return False, "limite_diario"
    return True, ""


def get_estado_hoy(session_id: str) -> dict:
    """Para el frontend: registros_hoy, limite, nivel."""
    if not (session_id or "").strip():
        return {"registros_hoy": 0, "limite": LIMITE_NUEVO, "nivel": "nuevo"}
    sid = session_id.strip()
    total, nivel = get_estado_reputacion(sid)
    limite = _limite_para_nivel(nivel)
    usados = get_registros_hoy(sid)
    return {
        "registros_hoy": usados,
        "limite": limite if nivel != "pro" else None,
        "nivel": nivel,
    }


def incrementar_registro(session_id: str) -> None:
    """Suma uno al contador de hoy y actualiza reputación (registros_totales)."""
    if not (session_id or "").strip():
        return
    sid = session_id.strip()
    hoy = _hoy()
    data = _load_registros_diarios()
    if hoy not in data:
        data[hoy] = {}
    data[hoy][sid] = data[hoy].get(sid, 0) + 1
    _save_registros_diarios(data)

    rep = _load_reputacion()
    if sid not in rep:
        rep[sid] = {"nivel": "nuevo", "registros_totales": 0}
    rep[sid]["registros_totales"] = rep[sid].get("registros_totales", 0) + 1
    rep[sid]["nivel"] = _get_nivel(rep[sid]["registros_totales"], False)  # pro se resuelve en get
    _save_reputacion(rep)
