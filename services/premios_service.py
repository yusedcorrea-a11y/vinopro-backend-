"""
Premios Service — VINO PRO IA
Evidence Engine · Capa 4: Verificación por Premios Internacionales

Cuando el usuario pregunta por los mejores vinos del mundo, devuelve:
  1. Top 5 mundial verificado por fuentes reales (Wine Spectator, Decanter, Parker, etc.)
  2. El mejor vino de su país/región según su geolocalización
  3. En qué posición está el vino local en el ranking mundial

Fuente de datos: data/premios_vinos.json (curado y verificado manualmente)
"""
import json
import re
import unicodedata
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "premios_vinos.json"
_cache: dict | None = None

# Palabras clave que activan la capa de premios
_PALABRAS_RANKING = [
    "mejor vino del mundo", "mejores vinos del mundo", "top vino", "top vinos",
    "vino numero uno", "vino número uno", "vino más premiado", "vino mas premiado",
    "vino más famoso", "vino mas famoso", "vino más caro", "vino mas caro",
    "cual es el mejor vino", "cuál es el mejor vino",
    "que vino es el mejor", "qué vino es el mejor",
    "ranking vinos", "ranking de vinos", "lista mejores vinos",
    "vinos premiados", "vinos de culto", "vino de culto",
    "vino más valorado", "vino mas valorado", "vino top mundial",
    "wine of the year", "mejor vino internacional", "premios vinos",
    "vino con más puntos", "vino con mas puntos",
]

# Mapeo de países comunes a código ISO
_PAIS_A_CODIGO = {
    "españa": "ESP", "spain": "ESP", "espana": "ESP",
    "france": "FRA", "francia": "FRA",
    "italy": "ITA", "italia": "ITA",
    "australia": "AUS",
    "united states": "USA", "estados unidos": "USA", "usa": "USA", "eeuu": "USA",
    "argentina": "ARG",
    "chile": "CHL",
    "portugal": "PRT",
    "germany": "DEU", "alemania": "DEU",
    "south africa": "ZAF", "sudafrica": "ZAF", "sudáfrica": "ZAF",
    "new zealand": "NZL", "nueva zelanda": "NZL", "nueva zelandia": "NZL",
    "mexico": "MEX", "méxico": "MEX",
    "united kingdom": "GBR", "reino unido": "GBR", "england": "GBR", "inglaterra": "GBR",
}


def _normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


def _cargar() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            _cache = json.load(f)
    except Exception:
        _cache = {}
    return _cache


def es_pregunta_de_ranking(pregunta: str) -> bool:
    """
    Detecta si la pregunta es sobre el ranking/mejores vinos del mundo.
    Devuelve True si debe activarse la Capa 4 de Premios.
    """
    p = _normalizar(pregunta)
    return any(_normalizar(kw) in p for kw in _PALABRAS_RANKING)


def obtener_top5_mundial() -> list[dict]:
    """Devuelve los 5 primeros del ranking mundial."""
    data = _cargar()
    top = data.get("top_mundial", [])
    return sorted(top, key=lambda x: x.get("posicion", 99))[:5]


def obtener_vino_por_pais(codigo_pais: str) -> dict | None:
    """
    Devuelve el vino emblema del país del usuario y su posición mundial.
    codigo_pais: código ISO 3166-1 alpha-3 (ESP, FRA, ITA…)
    """
    if not codigo_pais:
        return None
    data = _cargar()
    por_pais = data.get("top_por_pais", {})
    info = por_pais.get(codigo_pais.upper())
    if not info:
        # Buscar en top_mundial si el país tiene algún vino
        for vino in data.get("top_mundial", []):
            if vino.get("codigo_pais", "").upper() == codigo_pais.upper():
                return {
                    "vino_emblema": vino["vino"],
                    "posicion_mundial": vino["posicion"],
                    "otros_destacados": [],
                    "dato_curioso": vino.get("por_que_reconocido", ""),
                    "_desde_top": True,
                }
        return None
    info["codigo_pais"] = codigo_pais.upper()
    return info


def codigo_pais_desde_nombre(nombre_pais: str) -> str | None:
    """Convierte nombre de país en texto libre a código ISO."""
    if not nombre_pais:
        return None
    clave = _normalizar(nombre_pais)
    return _PAIS_A_CODIGO.get(clave)


def formatear_respuesta_premios(
    top5: list[dict],
    vino_local: dict | None,
    pais_usuario: str | None,
) -> str:
    """
    Formatea la respuesta completa de la Capa 4:
    - Top 5 mundial con fuentes verificadas
    - Posición del vino del país del usuario
    """
    if not top5:
        return ""

    lineas = ["🏆 **Top 5 Mejores Vinos del Mundo** *(según premios internacionales verificados)*\n"]

    for v in top5:
        pos = v.get("posicion", "?")
        nombre = v.get("vino", "")
        bodega = v.get("bodega", "")
        pais = v.get("pais", "")
        region = v.get("region", "")
        premios = v.get("premios", [])

        # Resumir premios
        premios_txt = []
        for p in premios[:2]:  # Máximo 2 premios por vino para no saturar
            fuente = p.get("fuente", "")
            premio = p.get("premio", "")
            anio = p.get("anio", "")
            puntos = p.get("puntuacion", "")
            entry = f"{fuente}: {premio}"
            if anio:
                entry += f" ({anio})"
            if puntos:
                entry += f" · {puntos}"
            premios_txt.append(entry)

        premios_str = " | ".join(premios_txt) if premios_txt else ""
        lineas.append(
            f"**#{pos} {nombre}** — {bodega}\n"
            f"   📍 {region}, {pais}\n"
            f"   🏅 {premios_str}"
        )

    # Sección del vino local
    if vino_local and pais_usuario:
        lineas.append("")
        pos_local = vino_local.get("posicion_mundial")
        vino_emblema = vino_local.get("vino_emblema", "")
        otros = vino_local.get("otros_destacados", [])
        dato = vino_local.get("dato_curioso", "")

        if pos_local:
            lineas.append(
                f"📌 **El mejor vino de tu región ({pais_usuario}) ocupa el #{pos_local} mundial:**\n"
                f"   🍷 {vino_emblema}"
            )
        else:
            lineas.append(
                f"📌 **El vino emblema de tu región ({pais_usuario}):**\n"
                f"   🍷 {vino_emblema}"
            )

        if otros:
            lineas.append(f"   También destacados: {', '.join(otros[:2])}")

        if dato:
            lineas.append(f"\n💡 *{dato}*")

    lineas.append(
        "\n📄 *Fuentes verificadas: Wine Spectator, Decanter World Wine Awards, "
        "Robert Parker Wine Advocate, James Suckling, Wine Enthusiast*"
    )

    return "\n".join(lineas)
