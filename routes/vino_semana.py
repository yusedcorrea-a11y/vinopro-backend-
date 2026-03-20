"""
API del destacado «Vino de la semana» (bodegas pequeñas / promoción editorial).
Configuración: data/vino_semana.json (excluido del catálogo de vinos en app.py).
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Request

router = APIRouter(tags=["Vino de la semana"])

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "data" / "vino_semana.json"


def _load_config() -> dict:
    if not CONFIG_PATH.is_file():
        return {"activo": False}
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {"activo": False}
    except Exception:
        return {"activo": False}


@router.get("/api/vino-semana")
def api_vino_semana(request: Request, lang: str = "es"):
    """
    Devuelve la configuración del destacado semanal y, si `vino_key` existe en el catálogo, la ficha del vino.
    Query opcional: lang=es|en (elige titulo/texto si existen claves _es / _en).
    """
    cfg = _load_config()
    vinos = getattr(request.app.state, "vinos_mundiales", {}) or {}

    lang = (lang or "es").strip().lower()[:2]
    titulo = cfg.get(f"titulo_{lang}") or cfg.get("titulo_es") or ""
    texto = cfg.get(f"texto_{lang}") or cfg.get("texto_es") or ""

    out = {
        "activo": bool(cfg.get("activo", False)),
        "desde": cfg.get("desde"),
        "hasta": cfg.get("hasta"),
        "titulo": titulo,
        "texto": texto,
        "pais_destacado": cfg.get("pais_destacado") or "",
        "bodega_pequena": bool(cfg.get("bodega_pequena", False)),
        "contacto_productores": cfg.get("contacto_productores") or "",
        "vino_key": None,
        "vino": None,
    }

    key = (cfg.get("vino_key") or "").strip()
    if key and key in vinos:
        out["vino_key"] = key
        out["vino"] = vinos[key]

    return out
