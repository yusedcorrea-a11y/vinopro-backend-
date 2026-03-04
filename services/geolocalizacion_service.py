"""
Geolocalización: geocodificación (Nominatim) y búsqueda de lugares cercanos (Overpass API).
Sin API key; uso conforme a política de uso de OSM (User-Agent identificando la app).
"""
import json
import math
import time
import urllib.parse
import urllib.request
from typing import Any

# Nominatim: 1 petición por segundo, User-Agent obligatorio
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "VinoProIA/1.0 (app sumiller; contacto en web)"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Cache simple en memoria para no repetir geocoding (ciudad -> lat, lon)
_geocode_cache: dict[str, tuple[float, float]] = {}
_last_nominatim_call: float = 0


def _nominatim_rate_limit() -> None:
    """Respetar 1 req/s de Nominatim."""
    global _last_nominatim_call
    now = time.time()
    if now - _last_nominatim_call < 1.0:
        time.sleep(1.0 - (now - _last_nominatim_call))
    _last_nominatim_call = time.time()


def geocode_ciudad(ciudad: str) -> tuple[float, float] | None:
    """
    Convierte ciudad/código postal/dirección en coordenadas (lat, lon).
    Usa Nominatim (OSM). Devuelve None si no hay resultados o hay error.
    """
    ciudad = (ciudad or "").strip()
    if len(ciudad) < 2:
        return None
    cache_key = ciudad.lower()
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]
    _nominatim_rate_limit()
    try:
        params = {"q": ciudad, "format": "json", "limit": 1}
        req = urllib.request.Request(
            NOMINATIM_URL + "?" + urllib.parse.urlencode(params),
            headers={"User-Agent": USER_AGENT},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if data and isinstance(data, list) and len(data) > 0:
            lat = float(data[0].get("lat", 0))
            lon = float(data[0].get("lon", 0))
            _geocode_cache[cache_key] = (lat, lon)
            return (lat, lon)
    except Exception:
        pass
    return None


def _distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en km entre dos puntos."""
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _extraer_centro(elemento: dict) -> tuple[float, float] | None:
    """De un elemento Overpass (node/way/relation) obtiene lat, lon."""
    if elemento.get("type") == "node":
        lat = elemento.get("lat")
        lon = elemento.get("lon")
        if lat is not None and lon is not None:
            return (float(lat), float(lon))
    if "center" in elemento:
        c = elemento["center"]
        return (float(c.get("lat", 0)), float(c.get("lon", 0)))
    if "lat" in elemento and "lon" in elemento:
        return (float(elemento["lat"]), float(elemento["lon"]))
    return None


def _nombre_y_direccion(tags: dict) -> tuple[str, str]:
    name = (tags.get("name") or tags.get("brand") or "Sin nombre").strip()
    addr = []
    for k in ["street", "housenumber", "addr:street", "addr:housenumber"]:
        v = tags.get(k)
        if v:
            addr.append(str(v))
    if not addr and tags.get("address"):
        addr.append(str(tags["address"]))
    for k in ["city", "addr:city", "town", "village"]:
        v = tags.get(k)
        if v and str(v) not in addr:
            addr.append(str(v))
    return (name, ", ".join(addr) if addr else "")


def buscar_lugares_cerca(
    lat: float,
    lon: float,
    radio_km: float = 5.0,
    tipo: str | None = None,
) -> list[dict[str, Any]]:
    """
    Busca lugares (restaurantes, bares, vinotecas) cerca de (lat, lon) usando Overpass.
    tipo: "restaurante" | "vinoteca" | "bar" | None (todos).
    Devuelve lista de { nombre, direccion, lat, lon, distancia_km, tipo, ... }.
    """
    radio_m = min(int(radio_km * 1000), 10000)  # máx 10 km
    # Consulta: restaurantes, bares, cafés, tiendas de alcohol/vino
    condiciones = []
    if tipo is None or tipo in ("restaurante", "restaurant"):
        condiciones.append('nwr["amenity"="restaurant"](around:{},{},{});'.format(radio_m, lat, lon))
    if tipo is None or tipo in ("bar",):
        condiciones.append('nwr["amenity"="bar"](around:{},{},{});'.format(radio_m, lat, lon))
    if tipo is None or tipo in ("vinoteca", "wine", "tienda"):
        condiciones.append('nwr["shop"="wine"](around:{},{},{});'.format(radio_m, lat, lon))
        condiciones.append('nwr["shop"="alcohol"](around:{},{},{});'.format(radio_m, lat, lon))
    if tipo is None:
        condiciones.append('nwr["amenity"="cafe"](around:{},{},{});'.format(radio_m, lat, lon))

    overpass_query = "[out:json][timeout:20];(" + " ".join(condiciones) + ");out center;"
    try:
        body = "data=" + urllib.parse.quote(overpass_query)
        req = urllib.request.Request(
            OVERPASS_URL,
            data=body.encode("utf-8"),
            headers={"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []

    resultados: list[dict[str, Any]] = []
    elementos = data.get("elements") or []
    for el in elementos:
        tags = el.get("tags") or {}
        centro = _extraer_centro(el)
        if not centro:
            continue
        plat, plon = centro
        dist = round(_distancia_haversine(lat, lon, plat, plon), 2)
        nombre, direccion = _nombre_y_direccion(tags)
        amenity = tags.get("amenity") or ""
        shop = tags.get("shop") or ""
        if amenity == "restaurant":
            tipo_lugar = "restaurante"
        elif amenity == "bar":
            tipo_lugar = "bar"
        elif amenity == "cafe":
            tipo_lugar = "café"
        elif shop in ("wine", "alcohol"):
            tipo_lugar = "vinoteca"
        else:
            tipo_lugar = "lugar"
        resultados.append({
            "nombre": nombre,
            "direccion": direccion,
            "lat": plat,
            "lon": plon,
            "distancia_km": dist,
            "tipo": tipo_lugar,
            "telefono": tags.get("phone") or tags.get("contact:phone") or "",
            "web": tags.get("website") or tags.get("contact:website") or "",
        })
    resultados.sort(key=lambda x: x["distancia_km"])
    return resultados[:30]  # límite razonable
