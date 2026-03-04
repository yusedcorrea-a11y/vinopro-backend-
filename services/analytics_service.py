"""
Big Data vinícola: registro de búsquedas, escaneos y preguntas al sumiller.
"""
import json
import os
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
ANALYTICS_PATH = os.path.join(DATA_FOLDER, "analytics.json")
MAX_EVENTOS = 5000  # límite por tipo para no crecer indefinidamente


def _load() -> dict:
    if os.path.exists(ANALYTICS_PATH):
        try:
            with open(ANALYTICS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"busquedas": [], "escaneos": [], "preguntas": []}


def _save(data: dict) -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(ANALYTICS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _trim(lista: list, max_n: int = MAX_EVENTOS) -> None:
    if len(lista) > max_n:
        del lista[: len(lista) - max_n]


def registrar_busqueda(query: str, pais: str | None = None, encontrados: int = 0) -> None:
    data = _load()
    data["busquedas"].append({
        "query": (query or "").strip()[:200],
        "pais": (pais or "").strip()[:100],
        "encontrados": int(encontrados),
        "ts": datetime.utcnow().isoformat(),
    })
    _trim(data["busquedas"])
    _save(data)


def registrar_escaneo(encontrado_en_bd: bool, vino_nombre: str = "", pais: str | None = None) -> None:
    data = _load()
    data["escaneos"].append({
        "encontrado_en_bd": bool(encontrado_en_bd),
        "vino_nombre": (vino_nombre or "").strip()[:200],
        "pais": (pais or "").strip()[:100],
        "ts": datetime.utcnow().isoformat(),
    })
    _trim(data["escaneos"])
    _save(data)


def registrar_pregunta(pregunta: str, vino_nombre: str = "") -> None:
    data = _load()
    data["preguntas"].append({
        "pregunta": (pregunta or "").strip()[:300],
        "vino_nombre": (vino_nombre or "").strip()[:200],
        "ts": datetime.utcnow().isoformat(),
    })
    _trim(data["preguntas"])
    _save(data)


def tendencias_busquedas(limite: int = 20, dias: int | None = 30) -> list[dict]:
    data = _load()
    busquedas = data.get("busquedas", [])
    if dias:
        cutoff = (datetime.utcnow() - timedelta(days=dias)).isoformat()
        busquedas = [b for b in busquedas if (b.get("ts") or "") >= cutoff]
    queries = [b.get("query", "").strip().lower() for b in busquedas if b.get("query")]
    cnt = Counter(queries)
    return [{"query": q, "veces": c} for q, c in cnt.most_common(limite)]


def estadisticas_por_pais(dias: int | None = 30) -> list[dict]:
    data = _load()
    escaneos = data.get("escaneos", [])
    busquedas = data.get("busquedas", [])
    if dias:
        cutoff = (datetime.utcnow() - timedelta(days=dias)).isoformat()
        escaneos = [e for e in escaneos if (e.get("ts") or "") >= cutoff]
        busquedas = [b for b in busquedas if (b.get("ts") or "") >= cutoff]
    paises_escaneo = Counter(e.get("pais") or "Sin especificar" for e in escaneos if e.get("pais"))
    paises_busqueda = Counter(b.get("pais") or "N/A" for b in busquedas if b.get("pais"))
    todos = set(paises_escaneo) | set(paises_busqueda)
    return [{"pais": p, "escaneos": paises_escaneo.get(p, 0), "busquedas": paises_busqueda.get(p, 0)} for p in sorted(todos) if p and p != "N/A"]


def preguntas_frecuentes(limite: int = 15, dias: int | None = 30) -> list[dict]:
    data = _load()
    preguntas = data.get("preguntas", [])
    if dias:
        cutoff = (datetime.utcnow() - timedelta(days=dias)).isoformat()
        preguntas = [p for p in preguntas if (p.get("ts") or "") >= cutoff]
    textos = [p.get("pregunta", "").strip().lower() for p in preguntas if p.get("pregunta")]
    cnt = Counter(textos)
    return [{"pregunta": q, "veces": c} for q, c in cnt.most_common(limite)]


def resumen_dashboard(dias: int = 30) -> dict:
    return {
        "total_busquedas": len([b for b in _load().get("busquedas", []) if (b.get("ts") or "") >= (datetime.utcnow() - timedelta(days=dias)).isoformat()]),
        "total_escaneos": len([e for e in _load().get("escaneos", []) if (e.get("ts") or "") >= (datetime.utcnow() - timedelta(days=dias)).isoformat()]),
        "total_preguntas": len([p for p in _load().get("preguntas", []) if (p.get("ts") or "") >= (datetime.utcnow() - timedelta(days=dias)).isoformat()]),
        "tendencias": tendencias_busquedas(10, dias),
        "por_pais": estadisticas_por_pais(dias),
        "preguntas_frecuentes": preguntas_frecuentes(10, dias),
    }
