"""
Servicio para consultar APIs externas de productos (Open Food Facts).
Se usa cuando el vino no está en nuestra base de datos.
Extrae información real: nombre, bodega, país/región y descripción genérica.
"""
import logging
import re
from typing import Any

import requests

logger = logging.getLogger(__name__)

OFF_API_PRODUCT = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
OFF_API_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl"
# Timeout y reintentos: OFF a veces responde lento; evitar llenar consola con tracebacks
OFF_TIMEOUT = 20
OFF_RETRIES = 3

# Mapeo de códigos OFF (countries_tags) a nombre legible
PAISES_OFF = {
    "en:spain": "España", "en:france": "Francia", "en:italy": "Italia", "en:portugal": "Portugal",
    "en:germany": "Alemania", "en:austria": "Austria", "en:argentina": "Argentina", "en:chile": "Chile",
    "en:australia": "Australia", "en:united-states": "Estados Unidos", "en:south-africa": "Sudáfrica",
    "en:new-zealand": "Nueva Zelanda", "en:greece": "Grecia", "en:hungary": "Hungría", "en:canada": "Canadá",
    "en:united-kingdom": "Reino Unido",
}

# Regiones típicas por país (para inferir desde categorías)
REGIONES_POR_PAIS = {
    "España": ["Rioja", "Ribera del Duero", "Priorat", "Rías Baixas", "Rueda", "Jerez", "Penedès", "Toro", "Bierzo"],
    "Francia": ["Burdeos", "Borgoña", "Champagne", "Rhône", "Loire", "Alsacia", "Languedoc", "Provenza"],
    "Italia": ["Toscana", "Piamonte", "Veneto", "Sicilia", "Cerdeña", "Abruzzo", "Campania"],
    "Portugal": ["Douro", "Alentejo", "Vinho Verde", "Dão", "Lisboa"],
    "Argentina": ["Mendoza", "Salta", "Patagonia"],
    "Chile": ["Valle Central", "Colchagua", "Maipo", "Casablanca"],
}


def _pais_desde_producto(product: dict) -> str:
    """Extrae el país de venta/origen desde countries_tags o categories."""
    tags = product.get("countries_tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")] if tags else []
    for t in tags:
        t = (t or "").strip().lower()
        if t in PAISES_OFF:
            return PAISES_OFF[t]
    countries_str = product.get("countries") or ""
    if countries_str:
        for key, nombre in PAISES_OFF.items():
            if key.replace("en:", "") in countries_str.lower():
                return nombre
    categories = (product.get("categories") or "").lower()
    if "spain" in categories or "espagne" in categories or "rioja" in categories or "ribera" in categories:
        return "España"
    if "france" in categories or "frankreich" in categories or "bordeaux" in categories or "burgundy" in categories:
        return "Francia"
    if "italy" in categories or "italie" in categories or "toscana" in categories:
        return "Italia"
    if "portugal" in categories or "douro" in categories:
        return "Portugal"
    if "argentina" in categories:
        return "Argentina"
    if "chile" in categories:
        return "Chile"
    if "germany" in categories or "deutschland" in categories:
        return "Alemania"
    if "australia" in categories:
        return "Australia"
    if "austria" in categories:
        return "Austria"
    return "Información no especificada"


def _region_desde_producto(product: dict, pais: str) -> str:
    """Infiere región desde categories o nombre del producto."""
    categories = (product.get("categories") or "").lower()
    name = (product.get("product_name") or "").lower()
    for region in REGIONES_POR_PAIS.get(pais, []):
        if region.lower() in categories or region.lower() in name:
            return region
    if "rioja" in categories or "rioja" in name:
        return "Rioja"
    if "bordeaux" in categories or "burdeos" in name or "pauillac" in name or "saint-émilion" in categories:
        return "Burdeos"
    if "champagne" in categories:
        return "Champagne"
    if "toscana" in categories or "toscana" in name or "chianti" in categories:
        return "Toscana"
    if "douro" in categories or "porto" in name:
        return "Douro"
    if pais != "Información no especificada":
        return "Región por determinar"
    return "Por determinar"


def _nombre_producto(product: dict) -> str:
    """Nombre en español, francés o inglés."""
    for key in ("product_name_es", "product_name_fr", "product_name_en", "product_name"):
        val = (product.get(key) or "").strip()
        if val and len(val) > 1:
            return val[:200]
    return "Vino (información externa)"


def _bodega_producto(product: dict) -> str:
    """Marca o bodega."""
    brands = product.get("brands") or ""
    if brands:
        return (brands.strip() or "")[:200]
    tags = product.get("brands_tags") or []
    if isinstance(tags, list) and tags:
        return ", ".join(str(t).replace("en:", "").replace("-", " ").title() for t in tags[:2])[:200]
    return "Marca no especificada"


def _descripcion_generica(product: dict, nombre: str, bodega: str, pais: str) -> str:
    """Descripción útil a partir de campos disponibles."""
    parts = []
    generic = (product.get("generic_name_es") or product.get("generic_name_fr") or product.get("generic_name") or "").strip()
    if generic:
        parts.append(generic[:300])
    if product.get("ingredients_text_es"):
        ing = (product.get("ingredients_text_es") or "")[:200]
        if ing:
            parts.append(f"Ingredientes: {ing}.")
    if not parts:
        parts.append(
            f"Vino {nombre}. "
            + (f"Marca o bodega: {bodega}. " if bodega and bodega != "Marca no especificada" else "")
            + (f"Origen: {pais}. " if pais and pais != "Información no especificada" else "")
            + "Información obtenida de fuentes abiertas; no está en nuestra base de datos."
        )
    return (parts[0][:500] + ("..." if len(parts[0]) > 500 else "")) if parts else "Información externa disponible."


def _mapear_producto_a_vino(product: dict) -> dict:
    """Convierte un producto de Open Food Facts al formato de vino de nuestra BD con datos reales."""
    nombre = _nombre_producto(product)
    bodega = _bodega_producto(product)
    pais = _pais_desde_producto(product)
    region = _region_desde_producto(product, pais)

    categories = (product.get("categories") or "").lower()
    tipo = "tinto"
    if "white" in categories or "blanc" in categories or "weiß" in categories or "blanco" in categories or "bianco" in categories:
        tipo = "blanco"
    elif "rosé" in categories or "rose" in categories or "rosado" in categories or "rosato" in categories:
        tipo = "rosado"
    elif "champagne" in categories or "sparkling" in categories or "espumoso" in categories or "cava" in categories:
        tipo = "espumoso"

    descripcion = _descripcion_generica(product, nombre, bodega, pais)

    return {
        "nombre": nombre,
        "bodega": bodega[:200] if bodega else "Marca no especificada",
        "region": region[:150] if region else "Por determinar",
        "pais": pais[:100] if pais else "Información no especificada",
        "tipo": tipo,
        "puntuacion": None,
        "precio_estimado": None,
        "descripcion": descripcion,
        "notas_cata": "No disponibles para este vino en fuentes externas.",
        "maridaje": "Recomendamos maridar según el tipo: tintos con carnes rojas, blancos con pescado y aves, espumosos con aperitivos.",
        "_origen": "open_food_facts",
    }


def buscar_por_codigo_barras(barcode: str) -> dict | None:
    """
    Obtiene un producto de Open Food Facts por código de barras.
    :return: diccionario en formato vino o None si no hay resultado
    """
    barcode = re.sub(r"\D", "", str(barcode))
    if not barcode:
        return None
    try:
        url = OFF_API_PRODUCT.format(barcode=barcode)
        r = requests.get(url, timeout=OFF_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != 1 or not data.get("product"):
            return None
        return _mapear_producto_a_vino(data["product"])
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        logger.warning("Open Food Facts barcode %s: timeout/conexión - %s", barcode, e)
        return None
    except Exception as e:
        logger.exception("Error Open Food Facts barcode %s: %s", barcode, e)
        return None


def buscar_por_texto(texto: str, limite: int = 5) -> list[dict]:
    """
    Busca productos en Open Food Facts por texto (nombre, marca, etc.).
    Filtra por categorías que contengan 'wine' / 'vino' cuando sea posible.
    :return: lista de vinos en nuestro formato (puede estar vacía)
    """
    texto = (texto or "").strip()
    if not texto or len(texto) < 2:
        return []
    params = {
        "search_terms": texto,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": max(limite * 3, 20),
    }
    last_error = None
    for intento in range(OFF_RETRIES):
        try:
            r = requests.get(OFF_API_SEARCH, params=params, timeout=OFF_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            products = data.get("products") or []
            resultados = []
            for p in products:
                if not p or not p.get("product_name"):
                    continue
                categories = (p.get("categories") or "").lower()
                if "wine" not in categories and "vino" not in categories and "wein" not in categories and "vin" not in categories:
                    continue
                vino = _mapear_producto_a_vino(p)
                resultados.append(vino)
                if len(resultados) >= limite:
                    break
            if not resultados and products:
                for p in products[:3]:
                    if p and p.get("product_name"):
                        vino = _mapear_producto_a_vino(p)
                        resultados.append(vino)
                        break
            return resultados
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_error = e
            logger.warning("Open Food Facts timeout/conexión (intento %d/%d) para '%s': %s", intento + 1, OFF_RETRIES, texto[:60], e)
            if intento == OFF_RETRIES - 1:
                return []
            continue
        except Exception as e:
            logger.exception("Error Open Food Facts search '%s': %s", texto[:60], e)
            return []
    return []
