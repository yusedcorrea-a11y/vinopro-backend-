"""
Servicio para Mi Bodega Virtual: botellas, alertas de temperatura/humedad,
potencial de guarda y valoración de inventario.
"""
import json
import os
import uuid
from datetime import datetime
from typing import Any

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
BODEGAS_PATH = os.path.join(DATA_FOLDER, "bodegas.json")

# Temperatura y humedad ideales por tipo (para alertas)
TEMP_HUMEDAD_IDEAL = {
    "tinto": {"temp_min": 12, "temp_max": 18, "humedad_min": 50, "humedad_max": 70},
    "blanco": {"temp_min": 8, "temp_max": 14, "humedad_min": 50, "humedad_max": 70},
    "rosado": {"temp_min": 8, "temp_max": 14, "humedad_min": 50, "humedad_max": 70},
    "espumoso": {"temp_min": 6, "temp_max": 12, "humedad_min": 50, "humedad_max": 70},
    "dulce": {"temp_min": 8, "temp_max": 14, "humedad_min": 50, "humedad_max": 70},
}
DEFAULT_TEMP = {"temp_min": 10, "temp_max": 16, "humedad_min": 50, "humedad_max": 70}

# Años de potencial de guarda típico por tipo (desde añada)
ANOS_GUARDA_TIPO = {"tinto": 15, "blanco": 8, "rosado": 3, "espumoso": 5, "dulce": 20}


def _load_bodegas() -> dict:
    if os.path.exists(BODEGAS_PATH):
        try:
            with open(BODEGAS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_bodegas(data: dict) -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(BODEGAS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_o_create_bodega(session_id: str) -> list:
    data = _load_bodegas()
    if session_id not in data:
        data[session_id] = {"botellas": [], "updated_at": datetime.utcnow().isoformat()}
        _save_bodegas(data)
    return data[session_id]["botellas"]


def add_botella(
    session_id: str,
    vino_key: str | None,
    vino_nombre: str,
    cantidad: int = 1,
    anada: int | None = None,
    ubicacion: str = "",
    temp_ideal: str = "",
    humedad_ideal: str = "",
    valor_unitario_estimado: float | None = None,
    tipo: str = "tinto",
) -> dict:
    botellas = _get_o_create_bodega(session_id)
    rango = TEMP_HUMEDAD_IDEAL.get(tipo.lower(), DEFAULT_TEMP)
    botella = {
        "id": str(uuid.uuid4()),
        "vino_key": vino_key or "",
        "vino_nombre": (vino_nombre or "").strip()[:200],
        "cantidad": max(1, int(cantidad)),
        "anada": anada,
        "ubicacion": (ubicacion or "").strip()[:100],
        "temp_ideal": temp_ideal or f"{rango['temp_min']}-{rango['temp_max']}°C",
        "humedad_ideal": humedad_ideal or f"{rango['humedad_min']}-{rango['humedad_max']}%",
        "valor_unitario_estimado": valor_unitario_estimado,
        "tipo": (tipo or "tinto").strip().lower()[:20],
        "fecha_guardado": datetime.utcnow().isoformat(),
    }
    botellas.append(botella)
    data = _load_bodegas()
    data[session_id]["botellas"] = botellas
    data[session_id]["updated_at"] = datetime.utcnow().isoformat()
    _save_bodegas(data)
    return botella


def get_bodega(session_id: str) -> list:
    return _get_o_create_bodega(session_id)


def update_botella(session_id: str, botella_id: str, **kwargs) -> dict | None:
    data = _load_bodegas()
    if session_id not in data:
        return None
    for i, b in enumerate(data[session_id]["botellas"]):
        if b.get("id") == botella_id:
            for k, v in kwargs.items():
                if k in b and v is not None:
                    b[k] = v
            data[session_id]["updated_at"] = datetime.utcnow().isoformat()
            _save_bodegas(data)
            return b
    return None


def delete_botella(session_id: str, botella_id: str) -> bool:
    data = _load_bodegas()
    if session_id not in data:
        return False
    botellas = [b for b in data[session_id]["botellas"] if b.get("id") != botella_id]
    if len(botellas) == len(data[session_id]["botellas"]):
        return False
    data[session_id]["botellas"] = botellas
    data[session_id]["updated_at"] = datetime.utcnow().isoformat()
    _save_bodegas(data)
    return True


def get_alertas(session_id: str, temp_actual: float | None, humedad_actual: float | None) -> list:
    if temp_actual is None and humedad_actual is None:
        return []
    botellas = _get_o_create_bodega(session_id)
    alertas = []
    for b in botellas:
        msg = []
        tipo = b.get("tipo", "tinto").lower()
        rango = TEMP_HUMEDAD_IDEAL.get(tipo, DEFAULT_TEMP)
        if temp_actual is not None:
            if temp_actual < rango["temp_min"]:
                msg.append(f"Temperatura baja (ideal {rango['temp_min']}-{rango['temp_max']}°C)")
            elif temp_actual > rango["temp_max"]:
                msg.append(f"Temperatura alta (ideal {rango['temp_min']}-{rango['temp_max']}°C)")
        if humedad_actual is not None:
            if humedad_actual < rango["humedad_min"]:
                msg.append(f"Humedad baja (ideal {rango['humedad_min']}-{rango['humedad_max']}%)")
            elif humedad_actual > rango["humedad_max"]:
                msg.append(f"Humedad alta (ideal {rango['humedad_min']}-{rango['humedad_max']}%)")
        if msg:
            alertas.append({"botella_id": b["id"], "vino_nombre": b["vino_nombre"], "alertas": msg})
    return alertas


def get_valoracion(session_id: str) -> dict:
    botellas = _get_o_create_bodega(session_id)
    total = 0.0
    for b in botellas:
        v = b.get("valor_unitario_estimado")
        if v is not None and v > 0:
            total += float(v) * int(b.get("cantidad", 1))
    return {"total_botellas": sum(int(b.get("cantidad", 1)) for b in botellas), "valoracion_estimada": round(total, 2), "entradas": len(botellas)}


def get_potencial_guarda(botella: dict, anio_actual: int | None = None) -> dict:
    from datetime import date
    anio = anio_actual or date.today().year
    anada = botella.get("anada")
    tipo = botella.get("tipo", "tinto").lower()
    anos_guarda = ANOS_GUARDA_TIPO.get(tipo, 10)
    if anada is None:
        return {"anios_restantes_estimados": None, "mensaje": "Indica la añada para estimar el potencial de guarda."}
    anada = int(anada)
    anos_transcurridos = anio - anada
    anos_restantes = max(0, anos_guarda - anos_transcurridos)
    return {
        "anada": anada,
        "anios_restantes_estimados": anos_restantes,
        "mensaje": f"Añada {anada}. Potencial de guarda estimado: {anos_restantes} años restantes (tipo {tipo})." if anos_restantes > 0 else f"Añada {anada}. En su momento óptimo de consumo.",
    }
