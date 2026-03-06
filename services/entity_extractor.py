"""
Extracción de entidades de vino desde texto OCR.
Bodega, Añada (año), Denominación de Origen, Variedad.
Sin APIs externas; eficiente para CPU (regex + listas).
"""
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Variedades de uva más comunes en etiquetas españolas e internacionales
VARIEDADES = frozenset({
    "tempranillo", "garnacha", "graciano", "mazuelo", "cariñena", "monastrell",
    "cabernet", "cabernet sauvignon", "merlot", "syrah", "pinot noir", "pinot",
    "chardonnay", "sauvignon", "sauvignon blanc", "verdejo", "albariño", "albarino",
    "viura", "macabeo", "parellada", "xarel", "xarel·lo", "airén", "airen",
    "mencia", "bobal", "prieto picudo", "godello", "treixadura", "loureiro",
    "malbec", "petit verdot", "sangiovese", "nebbiolo", "barbera", "riesling",
    "gewürztraminer", "gewurztraminer", "muscat", "moscatel", "palomino",
    "pedro ximénez", "pedro ximenez", "parellada",
})

# Denominaciones de Origen españolas (principales)
DO_ESPANA = frozenset({
    "ribera del duero", "rioja", "riorja", "rueda", "ribera del guadiana",
    "ribera del júcar", "cava", "priorat", "priorato", "penedès", "penedes",
    "toro", "bierzo", "denominación de origen", "denominacion de origen",
    "do calificada", "doca", "doc rioja", "doca rioja", "vt", "vino de la tierra",
    "vt castilla y león", "vt castilla y leon", "vt de castilla",
})

# Patrones para extraer DO desde texto
_PATRON_DO = re.compile(
    r"(?:denominaci[oó]n\s+de\s+origen\s+(?:calificada\s+)?|do\s+)?"
    r"([A-Za-záéíóúüñ\s]+?(?:del\s+[A-Za-záéíóúüñ]+|de\s+[A-Za-záéíóúüñ]+)?)",
    re.IGNORECASE
)

_PATRON_BODEGA = re.compile(
    r"(?:bodegas?\s+)?([A-Za-záéíóúüñ][A-Za-záéíóúüñ\s\.\-]+?)(?:\s+crianza|\s+reserva|\s+gran|\s+[\d]{4}|$)",
    re.IGNORECASE
)

_PATRON_ANIO = re.compile(r"\b(19[5-9]\d|20[0-3]\d)\b")


def extraer_entidades(texto: str) -> dict[str, Any]:
    """
    Extrae Bodega, Nombre del vino, Añada, Denominación de Origen y Variedad del texto OCR.
    :param texto: texto crudo o normalizado de la etiqueta
    :return: dict con claves bodega, nombre, añada, denominacion_origen, variedad (None si no se encuentra)
    """
    resultado = {
        "bodega": None,
        "nombre": None,
        "añada": None,
        "denominacion_origen": None,
        "variedad": None,
    }
    if not texto or not isinstance(texto, str) or len(texto.strip()) < 3:
        return resultado

    t = texto.strip()
    t_lower = t.lower()

    # Añada: año de 4 dígitos (1950-2039)
    anios = _PATRON_ANIO.findall(t)
    if anios:
        resultado["añada"] = int(anios[0])

    # Denominación de Origen
    for do in DO_ESPANA:
        if do in t_lower:
            # Normalizar nombre (capitalizar)
            nombre_do = "Rioja" if do == "riorja" else do.title()
            if not resultado["denominacion_origen"] or len(nombre_do) > len(resultado["denominacion_origen"] or ""):
                resultado["denominacion_origen"] = nombre_do
    if not resultado["denominacion_origen"]:
        match_do = _PATRON_DO.search(t)
        if match_do:
            do_val = match_do.group(1).strip()
            if len(do_val) > 3 and len(do_val) < 80:
                resultado["denominacion_origen"] = do_val.strip()

    # Variedad
    palabras = set(re.findall(r"[a-zA-Záéíóúüñ]+", t_lower))
    for var in VARIEDADES:
        if var in t_lower:
            resultado["variedad"] = var.title()
            break
    if not resultado["variedad"]:
        for palabra in sorted(palabras, key=len, reverse=True):
            if len(palabra) >= 5 and palabra in VARIEDADES:
                resultado["variedad"] = palabra.title()
                break

    # Bodega: "Bodegas X" o "Bodega X" o "Hnos. X"
    match_bodega = _PATRON_BODEGA.search(t)
    if match_bodega:
        b = match_bodega.group(1).strip()
        if len(b) > 2 and len(b) < 100:
            resultado["bodega"] = b.strip()
    if not resultado["bodega"]:
        if "bodegas" in t_lower or "bodega" in t_lower:
            idx = t_lower.find("bodegas") if "bodegas" in t_lower else t_lower.find("bodega")
            resto = t[idx:].split("\n")[0].strip()
            partes = resto.split()
            if len(partes) >= 2:
                resultado["bodega"] = " ".join(partes[1:4])[:80]  # Hasta 3 palabras tras "Bodegas"
    if not resultado["bodega"] and "hnos" in t_lower:
        idx = t_lower.find("hnos")
        resto = t[idx:].replace(".", " ").split()
        if len(resto) >= 2:
            resultado["bodega"] = " ".join(resto[:4])[:80]

    # Nombre del vino: primera línea o frase significativa (antes de Bodega, Crianza, etc.)
    palabras_nombre = []
    for p in t.split():
        p_low = p.lower()
        if p_low in ("bodega", "bodegas", "crianza", "reserva", "gran", "denominacion", "denominación", "origen", "producto"):
            break
        if len(p) > 1 and not p.isdigit():
            palabras_nombre.append(p)
        if len(palabras_nombre) >= 4:
            break
    if palabras_nombre:
        resultado["nombre"] = " ".join(palabras_nombre)[:120]

    return resultado


def formatear_entidades_para_json(entidades: dict[str, Any]) -> dict[str, Any]:
    """
    Devuelve solo los campos no nulos, con tipos correctos para JSON.
    Añada como int o None; el resto como str.
    """
    out = {}
    if entidades.get("bodega"):
        out["bodega"] = str(entidades["bodega"]).strip()[:200]
    if entidades.get("nombre"):
        out["nombre"] = str(entidades["nombre"]).strip()[:120]
    if entidades.get("añada") is not None:
        out["añada"] = int(entidades["añada"])
    if entidades.get("denominacion_origen"):
        out["denominacion_origen"] = str(entidades["denominacion_origen"]).strip()[:150]
    if entidades.get("variedad"):
        out["variedad"] = str(entidades["variedad"]).strip()[:80]
    return out
