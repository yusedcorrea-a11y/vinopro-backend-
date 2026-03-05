"""
API de geolocalización: lugares cercanos por coordenadas o por ciudad.
Incluye lugares destacados (partners) para mostrar en el mapa.
"""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from services import geolocalizacion_service as geo_svc

router = APIRouter(prefix="/api", tags=["Geolocalización"])
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LUGARES_DESTACADOS_PATH = DATA_DIR / "lugares_destacados.json"


@router.get("/lugares-cerca")
def lugares_cerca(
    lat: float | None = None,
    lon: float | None = None,
    ciudad: str | None = None,
    radio: float = 5.0,
    tipo: str | None = None,
):
    """
    Devuelve lugares (restaurantes, bares, vinotecas) cercanos.
    - Si se pasan lat y lon: busca alrededor de ese punto (radio en km, 1-10).
    - Si se pasa ciudad (y no lat/lon): geocodifica la ciudad y busca alrededor.
    """
    radio_km = max(1.0, min(10.0, float(radio)))
    if lat is not None and lon is not None:
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="lat y lon deben ser números")
        lugares = geo_svc.buscar_lugares_cerca(lat_f, lon_f, radio_km=radio_km, tipo=tipo)
        return {"lat": lat_f, "lon": lon_f, "radio_km": radio_km, "lugares": lugares}
    if ciudad:
        coords = geo_svc.geocode_ciudad(ciudad)
        if not coords:
            raise HTTPException(
                status_code=404,
                detail="No se pudo encontrar la ubicación para esa ciudad o dirección.",
            )
        lat_f, lon_f = coords
        lugares = geo_svc.buscar_lugares_cerca(lat_f, lon_f, radio_km=radio_km, tipo=tipo)
        return {"lat": lat_f, "lon": lon_f, "radio_km": radio_km, "ciudad": ciudad, "lugares": lugares}
    raise HTTPException(
        status_code=400,
        detail="Indica coordenadas (lat, lon) o una ciudad (ciudad=...).",
    )


def _cargar_lugares_destacados() -> list:
    """
    Lugares recomendados / partners. Orden: patrocinadores primero (patrocinador=true),
    luego por prioridad (mayor primero). Campos opcionales: patrocinador (bool), prioridad (int).
    """
    if not LUGARES_DESTACADOS_PATH.is_file():
        return []
    try:
        with open(LUGARES_DESTACADOS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        lugares = data if isinstance(data, list) else []
        # Fase 4: ordenar por patrocinador (true primero) y prioridad (mayor primero)
        def orden(l):
            es_patrocinador = 1 if (isinstance(l, dict) and l.get("patrocinador")) else 0
            prioridad = int(l.get("prioridad", 0)) if isinstance(l, dict) else 0
            return (-es_patrocinador, -prioridad)
        lugares.sort(key=orden)
        return lugares
    except Exception:
        return []


@router.get("/lugares-destacados")
def lugares_destacados():
    """
    Devuelve establecimientos destacados (partners) donde los usuarios pueden
    disfrutar del vino. Los que tengan patrocinador=true aparecen primero;
    opcionalmente se ordenan por prioridad. Incluye información de contacto.
    """
    lugares = _cargar_lugares_destacados()
    return {"lugares": lugares}


@router.get("/geocode")
def geocode(ciudad: str):
    """Geocodifica una ciudad o dirección y devuelve lat, lon."""
    coords = geo_svc.geocode_ciudad(ciudad)
    if not coords:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada.")
    return {"lat": coords[0], "lon": coords[1], "ciudad": ciudad}
