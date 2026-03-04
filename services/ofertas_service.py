"""
Ofertas de vino por usuarios Premium: ofertar un vino (con foto), contactar por email, regla 3 sin respuesta = quitar oferta.
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
OFERTAS_PATH = os.path.join(DATA_FOLDER, "ofertas.json")
UPLOADS_OFERTAS = os.path.join(DATA_FOLDER, "uploads", "ofertas")
MAX_CONTACTOS_SIN_RESPUESTA = 3


def _load_ofertas() -> list:
    if os.path.exists(OFERTAS_PATH):
        try:
            with open(OFERTAS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("ofertas", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        except Exception:
            pass
    return []


def _save_ofertas(ofertas: list) -> None:
    os.makedirs(os.path.dirname(OFERTAS_PATH) or ".", exist_ok=True)
    with open(OFERTAS_PATH, "w", encoding="utf-8") as f:
        json.dump({"ofertas": ofertas}, f, ensure_ascii=False, indent=2)


def _is_active(o: dict) -> bool:
    """Oferta activa: no removida y no supera 3 contactos sin respuesta."""
    if o.get("removed"):
        return False
    requests = o.get("contact_requests") or []
    if len(requests) < MAX_CONTACTOS_SIN_RESPUESTA:
        return True
    if any(r.get("replied") for r in requests):
        return True
    return False


def crear_oferta(vino_key: str, offerer_session_id: str, photo_path: str, offerer_email: str = "") -> dict:
    """
    Crea una oferta. photo_path es ruta relativa (ej. uploads/ofertas/xxx.jpg).
    Devuelve la oferta creada con id.
    """
    ofertas = _load_ofertas()
    offer_id = str(uuid.uuid4())[:12]
    nueva = {
        "id": offer_id,
        "vino_key": vino_key.strip(),
        "offerer_session_id": (offerer_session_id or "").strip(),
        "offerer_email": (offerer_email or "").strip()[:200],
        "photo_path": (photo_path or "").strip(),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "contact_requests": [],
        "removed": False,
    }
    ofertas.append(nueva)
    _save_ofertas(ofertas)
    return nueva


def get_active_offers_for_vino(vino_key: str) -> list:
    """Lista ofertas activas para un vino (para mostrar en Comprar)."""
    if not (vino_key or "").strip():
        return []
    ofertas = _load_ofertas()
    key = vino_key.strip()
    return [o for o in ofertas if o.get("vino_key") == key and _is_active(o)]


def get_offer_by_id(offer_id: str) -> dict | None:
    ofertas = _load_ofertas()
    for o in ofertas:
        if o.get("id") == offer_id:
            return o
    return None


def add_contact_request(offer_id: str, from_email: str, from_session_id: str, message: str) -> tuple[bool, str]:
    """
    Añade una solicitud de contacto. Si ya hay 3 y ninguna respondida, marca oferta como removed.
    Devuelve (True, "") o (False, mensaje_error).
    """
    ofertas = _load_ofertas()
    for o in ofertas:
        if o.get("id") != offer_id:
            continue
        if o.get("removed"):
            return False, "Oferta no disponible."
        requests = o.get("contact_requests") or []
        if len(requests) >= MAX_CONTACTOS_SIN_RESPUESTA and not any(r.get("replied") for r in requests):
            o["removed"] = True
            _save_ofertas(ofertas)
            return False, "Esta oferta ya no acepta más contactos."
        req_id = str(uuid.uuid4())[:8]
        requests.append({
            "id": req_id,
            "from_email": (from_email or "").strip()[:200],
            "from_session_id": (from_session_id or "").strip(),
            "message": (message or "").strip()[:2000],
            "at": datetime.utcnow().isoformat() + "Z",
            "replied": False,
        })
        o["contact_requests"] = requests
        if len(requests) >= MAX_CONTACTOS_SIN_RESPUESTA and not any(r.get("replied") for r in requests):
            o["removed"] = True
        _save_ofertas(ofertas)
        return True, ""
    return False, "Oferta no encontrada."


def mark_request_replied(offer_id: str, request_id: str, session_id: str) -> tuple[bool, str]:
    """Marca una solicitud como respondida. Solo el oferente (mismo session_id) puede."""
    ofertas = _load_ofertas()
    for o in ofertas:
        if o.get("id") != offer_id or (o.get("offerer_session_id") or "") != (session_id or "").strip():
            continue
        for r in o.get("contact_requests") or []:
            if r.get("id") == request_id:
                r["replied"] = True
                _save_ofertas(ofertas)
                return True, ""
        return False, "Solicitud no encontrada."
    return False, "Oferta no encontrada o no eres el oferente."


def get_offers_by_offerer(session_id: str) -> list:
    """Lista ofertas del usuario (para Mis ofertas)."""
    if not (session_id or "").strip():
        return []
    sid = session_id.strip()
    ofertas = _load_ofertas()
    return [o for o in ofertas if (o.get("offerer_session_id") or "") == sid]


def remove_offer(offer_id: str, session_id: str) -> tuple[bool, str]:
    """El oferente puede retirar su oferta."""
    ofertas = _load_ofertas()
    for o in ofertas:
        if o.get("id") == offer_id and (o.get("offerer_session_id") or "") == (session_id or "").strip():
            o["removed"] = True
            _save_ofertas(ofertas)
            return True, ""
    return False, "Oferta no encontrada o no eres el oferente."
