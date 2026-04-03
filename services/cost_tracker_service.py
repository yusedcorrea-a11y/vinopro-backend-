"""
Cost Tracker — VINO PRO IA
Registra tokens consumidos y coste estimado de cada llamada a Gemini.
Persiste en data/cost_tracker.json. Ligero, sin dependencias extras.

Precios Gemini 2.0 Flash (por 1M tokens):
  Entrada:  $0.075
  Salida:   $0.30
"""
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Precios por 1M tokens (USD) — Gemini 2.0 Flash
_PRECIO_ENTRADA_POR_M = 0.075
_PRECIO_SALIDA_POR_M  = 0.30

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "cost_tracker.json"
_lock = threading.Lock()

_FUNCIONES_VALIDAS = {
    "responder_sobre_vino",
    "buscar_con_file_search",
    "buscar_vino_en_nube",
    "reescribir_respuesta",
}


def _leer() -> dict:
    """Lee el JSON de costos. Si no existe o está corrupto, devuelve estructura vacía."""
    if not _DATA_FILE.is_file():
        return _estructura_vacia()
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return _estructura_vacia()
        return data
    except Exception:
        return _estructura_vacia()


def _guardar(data: dict) -> None:
    _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _estructura_vacia() -> dict:
    return {
        "tokens_entrada_total": 0,
        "tokens_salida_total": 0,
        "coste_usd_total": 0.0,
        "num_llamadas": 0,
        "por_funcion": {},
        "iniciado_en": datetime.now(timezone.utc).isoformat(),
        "ultima_llamada": None,
        "modelo": "gemini-2.0-flash",
    }


def _calcular_coste(tokens_entrada: int, tokens_salida: int) -> float:
    coste = (tokens_entrada / 1_000_000) * _PRECIO_ENTRADA_POR_M
    coste += (tokens_salida / 1_000_000) * _PRECIO_SALIDA_POR_M
    return round(coste, 8)


def registrar_uso(
    tokens_entrada: int,
    tokens_salida: int,
    funcion: str = "desconocida",
) -> None:
    """
    Registra una llamada a Gemini con sus tokens de entrada y salida.
    Llamar después de cada generate_content() exitoso.
    """
    if tokens_entrada < 0 or tokens_salida < 0:
        return
    coste = _calcular_coste(tokens_entrada, tokens_salida)
    ahora = datetime.now(timezone.utc).isoformat()

    with _lock:
        data = _leer()
        data["tokens_entrada_total"] += tokens_entrada
        data["tokens_salida_total"]  += tokens_salida
        data["coste_usd_total"]       = round(data["coste_usd_total"] + coste, 8)
        data["num_llamadas"]         += 1
        data["ultima_llamada"]        = ahora

        fn = funcion if funcion in _FUNCIONES_VALIDAS else "otra"
        if fn not in data["por_funcion"]:
            data["por_funcion"][fn] = {
                "llamadas": 0,
                "tokens_entrada": 0,
                "tokens_salida": 0,
                "coste_usd": 0.0,
            }
        data["por_funcion"][fn]["llamadas"]      += 1
        data["por_funcion"][fn]["tokens_entrada"] += tokens_entrada
        data["por_funcion"][fn]["tokens_salida"]  += tokens_salida
        data["por_funcion"][fn]["coste_usd"]       = round(
            data["por_funcion"][fn]["coste_usd"] + coste, 8
        )
        try:
            _guardar(data)
        except Exception as e:
            logger.warning("[CostTracker] No se pudo guardar: %s", e)


def obtener_resumen() -> dict:
    """
    Devuelve el resumen de consumo y coste estimado.
    Incluye el % del presupuesto de $10 consumido.
    """
    with _lock:
        data = _leer()

    presupuesto_usd = 10.0
    coste = data.get("coste_usd_total", 0.0)
    pct = round((coste / presupuesto_usd) * 100, 2) if presupuesto_usd > 0 else 0.0
    restante = round(presupuesto_usd - coste, 6)

    return {
        "resumen": {
            "tokens_entrada_total": data.get("tokens_entrada_total", 0),
            "tokens_salida_total": data.get("tokens_salida_total", 0),
            "num_llamadas": data.get("num_llamadas", 0),
            "coste_usd_total": coste,
            "presupuesto_usd": presupuesto_usd,
            "restante_usd": max(restante, 0.0),
            "porcentaje_usado": pct,
        },
        "por_funcion": data.get("por_funcion", {}),
        "modelo": data.get("modelo", "gemini-2.0-flash"),
        "iniciado_en": data.get("iniciado_en"),
        "ultima_llamada": data.get("ultima_llamada"),
    }


def resetear() -> None:
    """Resetea los contadores (útil al inicio de cada mes / ciclo de facturación)."""
    with _lock:
        _guardar(_estructura_vacia())
    logger.info("[CostTracker] Contadores reseteados.")
