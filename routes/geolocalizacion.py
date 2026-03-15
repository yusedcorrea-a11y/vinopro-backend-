"""
API de geolocalización: lugares cercanos por coordenadas o por ciudad.
Incluye lugares destacados (partners) y ubicación aproximada por IP (geolocalización inteligente).
"""
import json
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from services import geolocalizacion_service as geo_svc

router = APIRouter(prefix="/api", tags=["Geolocalización"])
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LUGARES_DESTACADOS_PATH = DATA_DIR / "lugares_destacados.json"

# Cache ubicación por IP (1 h). Clave: IP → (timestamp, { city, country, lat, lon })
_ubicacion_ip_cache: dict[str, tuple[float, dict]] = {}
_UBICACION_IP_TTL = 3600
_DEFAULT_LAT, _DEFAULT_LON = 40.4168, -3.7038


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


@router.get("/lugares")
def lugares(
    lat: float | None = None,
    lon: float | None = None,
    ciudad: str | None = None,
    radio: float = 5.0,
    tipo: str | None = None,
):
    """
    Alias moderno de /api/lugares-cerca para clientes web/móvil.
    """
    return lugares_cerca(lat=lat, lon=lon, ciudad=ciudad, radio=radio, tipo=tipo)


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


@router.get("/ubicacion-ip")
async def ubicacion_ip(request: Request):
    """
    Geolocalización inteligente: devuelve ciudad, país y coordenadas aproximadas según la IP del cliente.
    Pensado para centrar el mapa o mostrar "Estás en Madrid" sin pedir GPS.
    En localhost/dev devuelve Madrid por defecto. approx=true indica que es por IP, no GPS.
    """
    ip = (request.headers.get("x-forwarded-for") or getattr(request.client, "host", "") or "").strip()
    if "," in ip:
        ip = ip.split(",")[0].strip()
    if not ip or ip in ("127.0.0.1", "localhost", "::1"):
        return {
            "city": "Madrid",
            "country": "España",
            "country_code": "ES",
            "lat": _DEFAULT_LAT,
            "lon": _DEFAULT_LON,
            "approx": True,
        }
    now = time.time()
    if ip in _ubicacion_ip_cache:
        ts, data = _ubicacion_ip_cache[ip]
        if now - ts < _UBICACION_IP_TTL:
            return data
    try:
        import httpx
        async with httpx.AsyncClient(timeout=6.0) as client:
            r = await client.get(
                f"https://ipapi.co/{ip}/json/",
                headers={"User-Agent": "VINO-PRO-IA-Backend/1.0 (geolocalizacion)"},
            )
            if r.status_code != 200:
                return {
                    "city": "Madrid",
                    "country": "España",
                    "country_code": "ES",
                    "lat": _DEFAULT_LAT,
                    "lon": _DEFAULT_LON,
                    "approx": True,
                }
            data = r.json()
            if data.get("error"):
                return {
                    "city": "Madrid",
                    "country": "España",
                    "country_code": "ES",
                    "lat": _DEFAULT_LAT,
                    "lon": _DEFAULT_LON,
                    "approx": True,
                }
            try:
                lat = float(data.get("latitude")) if data.get("latitude") is not None else _DEFAULT_LAT
                lon = float(data.get("longitude")) if data.get("longitude") is not None else _DEFAULT_LON
            except (TypeError, ValueError):
                lat, lon = _DEFAULT_LAT, _DEFAULT_LON
            out = {
                "city": (data.get("city") or "Madrid").strip() or "Madrid",
                "country": (data.get("country_name") or "España").strip() or "España",
                "country_code": (data.get("country_code") or "ES").strip().upper() or "ES",
                "lat": lat,
                "lon": lon,
                "approx": True,
            }
            _ubicacion_ip_cache[ip] = (now, out)
            return out
    except Exception:
        return {
            "city": "Madrid",
            "country": "España",
            "country_code": "ES",
            "lat": _DEFAULT_LAT,
            "lon": _DEFAULT_LON,
            "approx": True,
        }
