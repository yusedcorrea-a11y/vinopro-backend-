"""
Servicio para el adaptador de restaurantes: tokens API, configuración y webhooks.
Permite conectar Mi Bodega con programas externos (CoverManager, TheFork, etc.).
Incluye rotación de token, debounce de webhooks y estado de sincronización.
"""
import json
import os
import secrets
import threading
import uuid
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from services import bodega_service as bodega_svc

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
RESTAURANTES_PATH = os.path.join(DATA_FOLDER, "restaurantes.json")

PROGRAMAS_DISPONIBLES = ["CoverManager", "TheFork", "Otro"]
WEBHOOK_TIMEOUT_SECONDS = 5
WEBHOOK_RETRY_DELAY_SECONDS = 5
WEBHOOK_DEBOUNCE_SECONDS = 10

_DEBOUNCE_TIMERS: dict[str, threading.Timer] = {}
_RETRY_TIMERS: dict[str, threading.Timer] = {}
_TIMER_LOCK = threading.Lock()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_restaurantes() -> dict:
    if os.path.exists(RESTAURANTES_PATH):
        try:
            with open(RESTAURANTES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("restaurantes", {})
                return data
        except Exception:
            pass
    return {"restaurantes": {}}


def _save_restaurantes(data: dict) -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(RESTAURANTES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _ensure_defaults(rest: dict) -> dict:
    rest.setdefault("session_id", str(uuid.uuid4()))
    rest.setdefault("nombre", "Mi Restaurante")
    rest.setdefault("programas", [])
    rest.setdefault("webhook_url", "")
    rest.setdefault("last_sync_at", None)
    rest.setdefault("last_sync_status", "never")
    rest.setdefault("last_sync_error", None)
    rest.setdefault("token_rotated_at", None)
    return rest


def _find_token_by_session(data: dict, session_id: str) -> str | None:
    for token, rest in data.get("restaurantes", {}).items():
        if rest.get("session_id") == session_id:
            return token
    return None


def _response_payload(token: str, rest: dict) -> dict:
    rest = _ensure_defaults(dict(rest))
    return {"token": token, **rest}


def get_or_create_restaurante(session_id: str | None = None) -> dict:
    """
    Crea un restaurante con token y session_id únicos o devuelve el asociado a la sesión.
    Si no se indica sesión y ya existe alguno, devuelve el primero (modo demo).
    """
    data = _load_restaurantes()
    rest = data.get("restaurantes", {})
    sid = (session_id or "").strip()

    if sid:
        token = _find_token_by_session(data, sid)
        if token:
            rest[token] = _ensure_defaults(rest[token])
            _save_restaurantes(data)
            return _response_payload(token, rest[token])

    if rest:
        first_key = next(iter(rest))
        rest[first_key] = _ensure_defaults(rest[first_key])
        _save_restaurantes(data)
        return _response_payload(first_key, rest[first_key])

    token = secrets.token_urlsafe(32)
    session_id = sid or str(uuid.uuid4())
    rest[token] = _ensure_defaults(
        {
            "session_id": session_id,
            "nombre": "Mi Restaurante",
            "programas": [],
            "webhook_url": "",
        }
    )
    data["restaurantes"] = rest
    _save_restaurantes(data)
    return _response_payload(token, rest[token])


def regenerate_token(session_id: str | None = None) -> dict | None:
    data = _load_restaurantes()
    rest = data.get("restaurantes", {})
    sid = (session_id or "").strip()
    if sid:
        old_token = _find_token_by_session(data, sid)
    else:
        old_token = next(iter(rest), None)
    if not old_token or old_token not in rest:
        return None

    new_token = secrets.token_urlsafe(32)
    payload = _ensure_defaults(rest.pop(old_token))
    payload["token_rotated_at"] = _utc_now_iso()
    rest[new_token] = payload
    data["restaurantes"] = rest
    _save_restaurantes(data)
    return _response_payload(new_token, payload)


def get_restaurante_by_token(token: str) -> dict | None:
    data = _load_restaurantes()
    rest = data.get("restaurantes", {}).get(token.strip())
    return _ensure_defaults(rest) if rest else None


def get_restaurante_by_session(session_id: str) -> dict | None:
    data = _load_restaurantes()
    for r in data.get("restaurantes", {}).values():
        if r.get("session_id") == session_id:
            return _ensure_defaults(r)
    return None


def get_session_id_for_token(token: str) -> str | None:
    r = get_restaurante_by_token(token)
    return r.get("session_id") if r else None


def update_config(token: str, nombre: str | None = None, programas: list | None = None, webhook_url: str | None = None) -> dict | None:
    data = _load_restaurantes()
    rest = data.get("restaurantes", {})
    if token not in rest:
        return None
    rest[token] = _ensure_defaults(rest[token])
    if nombre is not None:
        rest[token]["nombre"] = nombre
    if programas is not None:
        rest[token]["programas"] = [p for p in programas if p in PROGRAMAS_DISPONIBLES]
    if webhook_url is not None:
        rest[token]["webhook_url"] = (webhook_url or "").strip()
    _save_restaurantes(data)
    return _response_payload(token, rest[token])


def get_stock_export(session_id: str) -> list[dict]:
    """Lista de vinos con cantidad actual, formato apto para consumo externo."""
    botellas = bodega_svc.get_bodega(session_id)
    return [
        {
            "id": b.get("id"),
            "vino_nombre": b.get("vino_nombre"),
            "cantidad": int(b.get("cantidad", 1)),
            "anada": b.get("anada"),
            "ubicacion": b.get("ubicacion") or "",
            "tipo": b.get("tipo") or "tinto",
        }
        for b in botellas
    ]


def _set_sync_status(session_id: str, status: str, error: str | None = None) -> None:
    data = _load_restaurantes()
    token = _find_token_by_session(data, session_id)
    if not token:
        return
    rest = _ensure_defaults(data["restaurantes"][token])
    rest["last_sync_status"] = status
    rest["last_sync_error"] = error[:300] if error else None
    if status == "success":
        rest["last_sync_at"] = _utc_now_iso()
    data["restaurantes"][token] = rest
    _save_restaurantes(data)


def _cancel_timer(timer_map: dict[str, threading.Timer], session_id: str) -> None:
    timer = timer_map.pop(session_id, None)
    if timer:
        timer.cancel()


def _send_webhook_now(session_id: str, attempt: int = 1) -> None:
    rest = get_restaurante_by_session(session_id)
    if not rest or not rest.get("webhook_url"):
        return
    url = rest["webhook_url"].strip()
    if not url:
        return
    stock = get_stock_export(session_id)
    payload = json.dumps({"event": "bodega.updated", "stock": stock}).encode("utf-8")
    req = Request(url, data=payload, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=WEBHOOK_TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", 200)
            if status >= 500:
                raise HTTPError(url, status, f"HTTP {status}", hdrs=None, fp=None)
        _set_sync_status(session_id, "success")
    except (URLError, HTTPError, OSError) as exc:
        is_retryable = isinstance(exc, URLError) or isinstance(exc, OSError) or (
            isinstance(exc, HTTPError) and getattr(exc, "code", 0) >= 500
        )
        if is_retryable and attempt == 1:
            with _TIMER_LOCK:
                _cancel_timer(_RETRY_TIMERS, session_id)
                timer = threading.Timer(WEBHOOK_RETRY_DELAY_SECONDS, _send_webhook_now, args=(session_id, 2))
                timer.daemon = True
                _RETRY_TIMERS[session_id] = timer
                timer.start()
            return
        _set_sync_status(session_id, "error", str(exc))


def test_webhook(token: str) -> dict:
    """
    Envía un evento de prueba al webhook configurado sin tocar el stock real.
    Devuelve estado HTTP y un fragmento de la respuesta remota para depuración.
    """
    rest = get_restaurante_by_token(token)
    if not rest:
        return {"success": False, "status_code": None, "message": "Token no válido."}
    url = (rest.get("webhook_url") or "").strip()
    if not url:
        return {"success": False, "status_code": None, "message": "No hay webhook configurado."}

    payload = json.dumps(
        {
            "event": "bodega.test",
            "timestamp": _utc_now_iso(),
            "restaurant_name": rest.get("nombre") or "Mi Restaurante",
            "message": "Evento de prueba desde VINO. No afecta al stock real.",
            "sample_stock": [
                {
                    "id": "sample-botella",
                    "vino_nombre": "Vino de prueba",
                    "cantidad": 2,
                    "anada": 2021,
                    "ubicacion": "Bodega principal",
                    "tipo": "tinto",
                }
            ],
        }
    ).encode("utf-8")
    req = Request(url, data=payload, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=WEBHOOK_TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", 200)
            body = response.read().decode("utf-8", errors="replace")[:300]
        ok = 200 <= status < 300
        return {
            "success": ok,
            "status_code": status,
            "message": "Webhook de prueba recibido correctamente." if ok else f"Respuesta inesperada del servidor: HTTP {status}",
            "response_preview": body,
        }
    except HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            body = str(exc)[:300]
        return {
            "success": False,
            "status_code": getattr(exc, "code", None),
            "message": f"El servidor respondió con HTTP {getattr(exc, 'code', 'error')}.",
            "response_preview": body,
        }
    except (URLError, OSError) as exc:
        return {
            "success": False,
            "status_code": None,
            "message": f"No se pudo contactar con el webhook: {str(exc)[:200]}",
            "response_preview": "",
        }


def notify_webhook(session_id: str) -> None:
    """
    Programa una actualización consolidada del stock.
    Si hay varios cambios rápidos, solo se envía un webhook tras 10s de inactividad.
    """
    rest = get_restaurante_by_session(session_id)
    if not rest or not rest.get("webhook_url"):
        return
    with _TIMER_LOCK:
        _cancel_timer(_RETRY_TIMERS, session_id)
        _cancel_timer(_DEBOUNCE_TIMERS, session_id)
        timer = threading.Timer(WEBHOOK_DEBOUNCE_SECONDS, _send_webhook_now, args=(session_id, 1))
        timer.daemon = True
        _DEBOUNCE_TIMERS[session_id] = timer
        timer.start()
