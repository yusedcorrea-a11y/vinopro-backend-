"""
Servicio de enlaces de compra: tiendas afiliadas y subastas por vino y país.
Incluye tiendas locales por país (sin Amazon) para monetizar vía afiliados.
"""
import json
import os
import urllib.parse
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from models.enlaces_compra import EnlacesVino, TiendaAfiliado

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
ENLACES_PATH = os.path.join(DATA_FOLDER, "enlaces_compra.json")


def _load_enlaces() -> dict:
    if os.path.exists(ENLACES_PATH):
        try:
            with open(ENLACES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def get_enlaces_vino(vino_id: str) -> EnlacesVino | None:
    """Lee enlaces de compra para un vino_id desde data/enlaces_compra.json."""
    data = _load_enlaces()
    raw = data.get(vino_id)
    if not raw:
        # Intentar por clave normalizada (minúsculas, sin espacios extra)
        vid = (vino_id or "").strip().lower()
        for k, v in data.items():
            if k.strip().lower() == vid:
                raw = v
                break
    if not raw:
        return None
    if isinstance(raw, dict):
        return EnlacesVino.from_dict({"vino_id": vino_id, **raw})
    return None


# Códigos de país (IP) -> dominio Amazon para enlace de búsqueda universal
DOMINIOS_AMAZON: dict[str, str] = {
    "ES": "amazon.es",
    "IT": "amazon.it",
    "FR": "amazon.fr",
    "DE": "amazon.de",
    "GB": "amazon.co.uk",
    "UK": "amazon.co.uk",
    "US": "amazon.com",
    "MX": "amazon.com.mx",
    "CA": "amazon.ca",
    "BR": "amazon.com.br",
    "JP": "amazon.co.jp",
    "AU": "amazon.com.au",
    "IN": "amazon.in",
    "PT": "amazon.es",  # Portugal suele usar Amazon España
    "NL": "amazon.nl",
    "BE": "amazon.fr",
    "PL": "amazon.de",
    "TR": "amazon.com.tr",
}

# Países donde Amazon NO tiene marketplace propio: mostramos tiendas locales + Amazon España como fallback
# url_busqueda: usa {busqueda} que se sustituye por el nombre del vino (URL-encoded)
# afiliado_param + afiliado_env: si defines la variable de entorno, se añade a la URL para monetizar
TIENDAS_LOCALES_POR_PAIS: dict[str, list[dict]] = {
    "AR": [
        {"nombre": "Tienda de Vinos (AR)", "url_busqueda": "https://www.tiendadevinos.com.ar/buscar?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_AR"},
    ],
    "CL": [
        {"nombre": "Vinoteca Chile", "url_busqueda": "https://www.vinoteca.cl/buscar?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_CL"},
    ],
    "UY": [
        {"nombre": "Vinos del Uruguay", "url_busqueda": "https://www.vinosdeluruguay.com.uy/buscar?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_UY"},
    ],
    "PE": [
        {"nombre": "Vinos Perú", "url_busqueda": "https://www.vinosperu.com/buscar?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_PE"},
    ],
    "CO": [
        {"nombre": "Vinoteca Colombia", "url_busqueda": "https://www.vinotecacolombia.com/buscar?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_CO"},
    ],
    "CH": [
        {"nombre": "Wein.ch", "url_busqueda": "https://www.wein.ch/de/search?query={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_CH"},
    ],
    "AT": [
        {"nombre": "Wein & Co (AT)", "url_busqueda": "https://www.weinco.at/suche?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_AT"},
    ],
    "NZ": [
        {"nombre": "The Wine Collective (NZ)", "url_busqueda": "https://www.thewinecollective.co.nz/search?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_NZ"},
    ],
    "GR": [
        {"nombre": "Skroutz Vinos (GR)", "url_busqueda": "https://www.skroutz.gr/s?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_GR"},
    ],
    "IL": [
        {"nombre": "Yayin (IL)", "url_busqueda": "https://www.yayin.co.il/search?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_IL"},
    ],
    "LB": [
        {"nombre": "Château Musar / vinotecas LB", "url_busqueda": "https://www.chateaumusar.com.lb/search?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_LB"},
    ],
    "ZA": [
        {"nombre": "Wine of the Month (ZA)", "url_busqueda": "https://www.wineofthemonth.co.za/search?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_ZA"},
    ],
    "NO": [
        {"nombre": "Vinmonopolet (NO)", "url_busqueda": "https://www.vinmonopolet.no/search?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_NO"},
    ],
    "DK": [
        {"nombre": "Vinens Verden (DK)", "url_busqueda": "https://www.vinensverden.dk/sog?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_DK"},
    ],
    "SE": [
        {"nombre": "Systembolaget (SE)", "url_busqueda": "https://www.systembolaget.se/sok/?searchquery={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_SE"},
    ],
    "FI": [
        {"nombre": "Alko (FI)", "url_busqueda": "https://www.alko.fi/tuotteet/?search={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_FI"},
    ],
    "HU": [
        {"nombre": "Bortársaság (HU)", "url_busqueda": "https://www.bortarsasag.hu/kereses?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_HU"},
    ],
    "CZ": [
        {"nombre": "Vínum (CZ)", "url_busqueda": "https://www.vinum.cz/vyhledavani?q={busqueda}", "afiliado_param": "ref", "afiliado_env": "AFILIADO_CZ"},
    ],
    "MA": [
        {"nombre": "Vin Maroc / cavas MA", "url_busqueda": "https://www.google.com/search?q=vin+maroc+{busqueda}", "afiliado_param": None, "afiliado_env": None},
    ],
    "DZ": [
        {"nombre": "Vins Algérie", "url_busqueda": "https://www.google.com/search?q=vin+algerie+{busqueda}", "afiliado_param": None, "afiliado_env": None},
    ],
    "TN": [
        {"nombre": "Vins Tunisie", "url_busqueda": "https://www.google.com/search?q=vin+tunisie+{busqueda}", "afiliado_param": None, "afiliado_env": None},
    ],
}

# Guías de vino / vinotecas / restaurantes por país para "¿Dónde tomarlo?"
# Código país -> { nombre, url, emoji }. Fallback: Guía Repsol (ES) con 🌍
GUIA_VINO_POR_PAIS: dict[str, dict[str, str]] = {
    "ES": {
        "nombre": "Guía Repsol",
        "url": "https://www.guiarepsol.com/es/soletes/vinotecas-y-bodegas/",
        "emoji": "🇪🇸",
    },
    "IT": {
        "nombre": "Gambero Rosso",
        "url": "https://www.gamberorosso.it/vini/",
        "emoji": "🇮🇹",
    },
    "FR": {
        "nombre": "Guide Hachette",
        "url": "https://www.leguidehachette.com/",
        "emoji": "🇫🇷",
    },
    "PT": {
        "nombre": "Revista de Vinhos",
        "url": "https://www.revistadevinhos.pt/",
        "emoji": "🇵🇹",
    },
    "DE": {
        "nombre": "Gault&Millau",
        "url": "https://www.gaultmillau.de/wein/",
        "emoji": "🇩🇪",
    },
    "GB": {
        "nombre": "Decanter",
        "url": "https://www.decanter.com/wine-reviews/",
        "emoji": "🇬🇧",
    },
    "UK": {
        "nombre": "Decanter",
        "url": "https://www.decanter.com/wine-reviews/",
        "emoji": "🇬🇧",
    },
    "US": {
        "nombre": "Wine Spectator",
        "url": "https://www.winespectator.com/",
        "emoji": "🇺🇸",
    },
    "AR": {
        "nombre": "Guía de Vinos Argentina",
        "url": "https://www.guiadevinos.com.ar/",
        "emoji": "🇦🇷",
    },
    "CL": {
        "nombre": "Guía de Vinos Chile",
        "url": "https://www.guiadevinos.cl/",
        "emoji": "🇨🇱",
    },
    "MX": {
        "nombre": "Guía del Vino México",
        "url": "https://www.guiadelvinomexico.com/",
        "emoji": "🇲🇽",
    },
    # América Latina adicional
    "BR": {
        "nombre": "Guia de Vinhos Brasil",
        "url": "https://www.guiadevinhosbrasil.com/",
        "emoji": "🇧🇷",
    },
    "UY": {
        "nombre": "Guía de Vinos Uruguay",
        "url": "https://www.guiadevinosuruguay.com/",
        "emoji": "🇺🇾",
    },
    "PE": {
        "nombre": "Guía de Vinos Perú",
        "url": "https://www.guiadevinosperu.com/",
        "emoji": "🇵🇪",
    },
    "CO": {
        "nombre": "Guía de Vinos Colombia",
        "url": "https://www.guiadevinoscolombia.com/",
        "emoji": "🇨🇴",
    },
    # Europa adicional
    "BE": {
        "nombre": "Gault&Millau Belgique",
        "url": "https://www.gaultmillau.be/",
        "emoji": "🇧🇪",
    },
    "NL": {
        "nombre": "Gault&Millau Nederland",
        "url": "https://www.gaultmillau.nl/",
        "emoji": "🇳🇱",
    },
    "CH": {
        "nombre": "Gault&Millau Suisse",
        "url": "https://www.gaultmillau.ch/",
        "emoji": "🇨🇭",
    },
    "AT": {
        "nombre": "Falstaff",
        "url": "https://www.falstaff.at/wein/",
        "emoji": "🇦🇹",
    },
    "SE": {
        "nombre": "Vinjournalen",
        "url": "https://www.vinjournalen.se/",
        "emoji": "🇸🇪",
    },
    "NO": {
        "nombre": "Vinforum",
        "url": "https://www.vinforum.no/",
        "emoji": "🇳🇴",
    },
    "DK": {
        "nombre": "Vinbladet",
        "url": "https://www.vinbladet.dk/",
        "emoji": "🇩🇰",
    },
    "FI": {
        "nombre": "Viinilehti",
        "url": "https://www.viinilehti.fi/",
        "emoji": "🇫🇮",
    },
    "PL": {
        "nombre": "Czas Wina",
        "url": "https://www.czaswina.pl/",
        "emoji": "🇵🇱",
    },
    "CZ": {
        "nombre": "Víno z Moravy a z Čech",
        "url": "https://www.vinazmoravyvinazcech.cz/",
        "emoji": "🇨🇿",
    },
    "HU": {
        "nombre": "Magyar Bor",
        "url": "https://winesofhungary.hu/",
        "emoji": "🇭🇺",
    },
    "GR": {
        "nombre": "Oinorama",
        "url": "https://www.oinorama.gr/",
        "emoji": "🇬🇷",
    },
    # Otros continentes
    "ZA": {
        "nombre": "Platter's Wine Guide",
        "url": "https://www.wineonaplatter.com/",
        "emoji": "🇿🇦",
    },
    "AU": {
        "nombre": "Halliday Wine Companion",
        "url": "https://www.winecompanion.com.au/",
        "emoji": "🇦🇺",
    },
    "NZ": {
        "nombre": "Bob Campbell MW",
        "url": "https://www.bobcampbell.nz/",
        "emoji": "🇳🇿",
    },
    "JP": {
        "nombre": "JWINE (日本ワイン)",
        "url": "https://jwine.net/",
        "emoji": "🇯🇵",
    },
    "IN": {
        "nombre": "Indian Wine Academy / Sula Vineyards",
        "url": "https://www.sulawines.com/",
        "emoji": "🇮🇳",
    },
    # Rusia y mercados árabes / Mediterráneo oriental (Fase 6)
    "RU": {
        "nombre": "Simple Wine News / Russian Wine Guide",
        "url": "https://simplewinenews.com/",
        "emoji": "🇷🇺",
    },
    "LB": {
        "nombre": "Wines of Lebanon / Château Musar",
        "url": "https://www.chateaumusar.com/",
        "emoji": "🇱🇧",
    },
    "MA": {
        "nombre": "Vins du Maroc / Moroccan Wines",
        "url": "https://www.morocco.com/food-drink/wine/",
        "emoji": "🇲🇦",
    },
    "DZ": {
        "nombre": "Vins d'Algérie",
        "url": "https://www.vinsdalgerie.com/",
        "emoji": "🇩🇿",
    },
    "TN": {
        "nombre": "Vins de Tunisie",
        "url": "https://www.tunisie.com/vins/",
        "emoji": "🇹🇳",
    },
    "IL": {
        "nombre": "Israeli Wine Guide / Golan Heights",
        "url": "https://www.golanwines.co.il/",
        "emoji": "🇮🇱",
    },
}

FALLBACK_GUIA = {
    "nombre": "Guía Repsol",
    "url": "https://www.guiarepsol.com/es/soletes/vinotecas-y-bodegas/",
    "emoji": "🌍",
}


def get_guia_vinos_por_pais(pais: str) -> dict[str, str]:
    """
    Devuelve la guía de vinos/vinotecas para el país detectado.
    Keys: nombre, url, emoji. Si el país no está mapeado, devuelve fallback (Guía Repsol, 🌍).
    """
    codigo = (pais or "ES").strip().upper()
    return GUIA_VINO_POR_PAIS.get(codigo, FALLBACK_GUIA).copy()


def _generar_tienda_local(plantilla: dict, vino_nombre: str, pais: str) -> TiendaAfiliado:
    """Construye TiendaAfiliado desde una plantilla de TIENDAS_LOCALES_POR_PAIS (url_busqueda + afiliado opcional)."""
    busqueda = (vino_nombre or "vino").strip().replace(" ", "+")
    busqueda_enc = urllib.parse.quote(busqueda)
    url = (plantilla.get("url_busqueda") or "").replace("{busqueda}", busqueda_enc)
    param = plantilla.get("afiliado_param")
    env_key = plantilla.get("afiliado_env")
    if param and env_key:
        tag = os.environ.get(env_key, "").strip()
        if tag:
            sep = "&" if "?" in url else "?"
            url += f"{sep}{param}={urllib.parse.quote(tag)}"
    return TiendaAfiliado(
        nombre=plantilla.get("nombre", "Tienda"),
        url=url,
        tipo="tienda_online",
        moneda="local",
        afiliado=bool(param and env_key),
        envio_internacional=False,
        pais_origen=pais,
        es_amazon=False,
    )


def generar_enlace_amazon(vino_nombre: str, pais: str) -> TiendaAfiliado:
    """
    Genera un enlace de búsqueda en Amazon para el vino, adaptado al país del usuario.
    Permite que todos los vinos tengan al menos un enlace de compra real.
    Opcional: AMAZON_ASSOCIATE_TAG en .env (ej. tu-id-21) para monetización con Amazon Associates.
    """
    pais_upper = (pais or "ES").strip().upper()
    dominio = DOMINIOS_AMAZON.get(pais_upper, "amazon.es")
    nombre_busqueda = (vino_nombre or "").strip().replace(" ", "+")
    if not nombre_busqueda:
        nombre_busqueda = "vino"
    url = f"https://www.{dominio}/s?k={urllib.parse.quote(nombre_busqueda)}"
    tag = os.environ.get("AMAZON_ASSOCIATE_TAG", "").strip()
    if tag:
        url += f"&tag={urllib.parse.quote(tag)}"
    return TiendaAfiliado(
        nombre="Amazon",
        url=url,
        tipo="marketplace",
        moneda="local",
        afiliado=True,
        envio_internacional=False,
        pais_origen=pais_upper,
        es_amazon=True,
    )


def _tiendas_locales_para_pais(vino_nombre: str, pais: str) -> list[TiendaAfiliado]:
    """Devuelve tiendas locales (enlaces de búsqueda) para países sin Amazon o con tiendas adicionales."""
    pais_upper = (pais or "").strip().upper()
    plantillas = TIENDAS_LOCALES_POR_PAIS.get(pais_upper, [])
    return [_generar_tienda_local(p, vino_nombre, pais_upper) for p in plantillas if p.get("url_busqueda")]


def detectar_pais_por_ip(ip: str | None) -> str:
    """
    Usa ip-api.com (sin key) para obtener código de país.
    Límite: 45 req/min. Devuelve "ES" por defecto si falla o ip es localhost.
    """
    if not ip or ip.strip() in ("127.0.0.1", "::1", ""):
        return "ES"
    try:
        url = f"http://ip-api.com/json/{ip.strip()}?fields=countryCode"
        with urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            return (data.get("countryCode") or "ES").upper()
    except (URLError, HTTPError, KeyError, ValueError):
        return "ES"


def buscar_tiendas_para_pais(vino_id: str, vino_nombre: str, pais: str) -> list[TiendaAfiliado]:
    """
    Devuelve lista de TiendaAfiliado para el vino y el país:
    1) tiendas del JSON (nacionales + internacionales con envío),
    2) tiendas locales por país (países sin Amazon o con tiendas adicionales),
    3) Amazon como fallback universal.
    """
    out: list[TiendaAfiliado] = []
    pais_upper = (pais or "ES").strip().upper()
    nombre_para_busqueda = (vino_nombre or vino_id or "").strip()
    enlaces = get_enlaces_vino(vino_id)
    if enlaces:
        for t in enlaces.nacional.get(pais_upper, []):
            if isinstance(t, dict):
                out.append(TiendaAfiliado.from_dict(t))
        for t in enlaces.internacional:
            if isinstance(t, dict) and t.get("envio_internacional"):
                out.append(TiendaAfiliado.from_dict(t))
    # Tiendas locales (vinotecas por país sin Amazon): enlaces de búsqueda + afiliado si está en .env
    out.extend(_tiendas_locales_para_pais(nombre_para_busqueda, pais_upper))
    # Amazon al final: enlace de búsqueda adaptado al país (o amazon.es si no hay marketplace local)
    out.append(generar_enlace_amazon(nombre_para_busqueda, pais_upper))
    return out


def get_todas_tiendas_internacional(vino_id: str) -> list[TiendaAfiliado]:
    """Todas las tiendas de la sección internacional (para pestaña Internacional)."""
    enlaces = get_enlaces_vino(vino_id)
    if not enlaces:
        return []
    return [TiendaAfiliado.from_dict(t) for t in enlaces.internacional if isinstance(t, dict)]


def get_todas_nacionales_por_pais(vino_id: str) -> dict[str, list[TiendaAfiliado]]:
    """Por país, lista de tiendas nacionales (para mostrar en pestaña Nacional por país)."""
    enlaces = get_enlaces_vino(vino_id)
    if not enlaces:
        return {}
    return {
        pais: [TiendaAfiliado.from_dict(t) for t in tiendas if isinstance(t, dict)]
        for pais, tiendas in enlaces.nacional.items()
    }


def get_subastas(vino_id: str) -> list[dict]:
    """Lista de subastas para el vino (dict para template)."""
    enlaces = get_enlaces_vino(vino_id)
    if not enlaces:
        return []
    return enlaces.subastas
