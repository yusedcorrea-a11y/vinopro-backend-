"""
Servicio para el adaptador de restaurantes: tokens API, configuración y webhooks.
Permite conectar Mi Bodega con programas externos (CoverManager, TheFork, etc.).
"""
import json
import os
import secrets
import uuid
from typing import Any
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from services import bodega_service as bodega_svc

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
RESTAURANTES_PATH = os.path.join(DATA_FOLDER, "restaurantes.json")

PROGRAMAS_DISPONIBLES = ["CoverManager", "TheFork", "Otro"]


def _load_restaurantes() -> dict:
    if os.path.exists(RESTAURANTES_PATH):
        try:
            with open(RESTAURANTES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"restaurantes": {}}


def _save_restaurantes(data: dict) -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(RESTAURANTES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_or_create_restaurante() -> dict:
    """
    Crea un nuevo restaurante con token y session_id únicos, o devuelve el primero existente.
    En producción se podría asociar a usuario/email.
    """
    data = _load_restaurantes()
    rest = data.get("restaurantes", {})
    if rest:
        # Devolver el primero (para demo; en multi-tenant se filtraría por usuario)
        first_key = next(iter(rest))
        return {"token": first_key, **rest[first_key]}
    token = secrets.token_urlsafe(32)
    session_id = str(uuid.uuid4())
    rest[token] = {
        "session_id": session_id,
        "nombre": "Mi Restaurante",
        "programas": [],
        "webhook_url": "",
    }
    data["restaurantes"] = rest
    _save_restaurantes(data)
    return {"token": token, "session_id": session_id, "nombre": "Mi Restaurante", "programas": [], "webhook_url": ""}


def get_restaurante_by_token(token: str) -> dict | None:
    data = _load_restaurantes()
    return data.get("restaurantes", {}).get(token.strip())


def get_restaurante_by_session(session_id: str) -> dict | None:
    data = _load_restaurantes()
    for r in data.get("restaurantes", {}).values():
        if r.get("session_id") == session_id:
            return r
    return None


def get_session_id_for_token(token: str) -> str | None:
    r = get_restaurante_by_token(token)
    return r.get("session_id") if r else None


def update_config(token: str, nombre: str | None = None, programas: list | None = None, webhook_url: str | None = None) -> dict | None:
    data = _load_restaurantes()
    rest = data.get("restaurantes", {})
    if token not in rest:
        return None
    if nombre is not None:
        rest[token]["nombre"] = nombre
    if programas is not None:
        rest[token]["programas"] = [p for p in programas if p in PROGRAMAS_DISPONIBLES]
    if webhook_url is not None:
        rest[token]["webhook_url"] = (webhook_url or "").strip()
    _save_restaurantes(data)
    return rest[token]


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


def notify_webhook(session_id: str) -> None:
    """Envía actualización de stock al webhook del restaurante si está configurado."""
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
        with urlopen(req, timeout=5) as _:
            pass
    except (URLError, HTTPError, OSError):
        pass  # No bloquear la operación si el webhook falla
