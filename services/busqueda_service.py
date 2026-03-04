"""
Servicio de búsqueda de vinos en la base de datos.
Reutiliza la lógica de búsqueda avanzada (nombre, bodega, región, fuzzy matching).
"""
import re
import difflib

STOP_WORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "y", "en", "por", "para", "con", "a",
    "the", "of", "and",
    "le", "les", "des", "du", "au", "aux",
}

PESOS_CAMPO = {
    "nombre": 3.0,
    "bodega": 2.0,
    "region": 1.5,
    "uva_principal": 1.2,
}


def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparación: minúsculas y sin signos raros."""
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9áéíóúüñçàèìòùâêîôûäëïöüãõœæ ]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto


def obtener_tokens_busqueda(texto: str):
    """Convierte el texto de entrada en tokens útiles de búsqueda."""
    texto_norm = normalizar_texto(texto)
    return [
        t for t in texto_norm.split()
        if t and len(t) > 2 and t not in STOP_WORDS
    ]


def similitud_palabras(a: str, b: str) -> float:
    """Devuelve una medida de similitud entre 0 y 1."""
    return difflib.SequenceMatcher(None, a, b).ratio()


# Regiones con prioridad: si el usuario menciona estas claves, se filtra por esa región (nombre en BD)
REGION_PRIORITARIA = [
    (["ribera", "duero"], "Ribera del Duero"),
    (["rioja"], "Rioja"),
]


def _detectar_region_prioritaria(texto_norm: str) -> str | None:
    """Si el texto indica una región prioritaria, devuelve su nombre exacto (como en BD)."""
    for claves, region_nombre in REGION_PRIORITARIA:
        if all(c in texto_norm for c in claves) or (len(claves) >= 1 and claves[0] in texto_norm):
            return region_nombre
    return None


def _extraer_precio_max(texto_norm: str) -> float | None:
    """Extrae precio máximo de la búsqueda: 'menos de 20', '20€', '20 euros'."""
    import re
    m = re.search(r"(?:menos de|por menos de|debajo de|maximo|máximo)\s*(\d+)", texto_norm)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+)\s*(?:euros?|eur|€)", texto_norm)
    if m:
        return float(m.group(1))
    return None


def _extraer_tipo(texto_norm: str) -> str | None:
    """Extrae tipo de vino si se menciona: tinto, blanco, rosado, espumoso."""
    for t in ["tinto", "blanco", "rosado", "espumoso"]:
        if t in texto_norm:
            return t
    return None


def _precio_num(precio_str: str) -> float:
    """Extrae número de precio (máximo de un rango) para filtrar."""
    if not precio_str or not isinstance(precio_str, str):
        return 0.0
    import re
    nums = re.findall(r"[0-9]+", precio_str.replace(",", "."))
    return max([float(n) for n in nums]) if nums else 0.0


def buscar_por_codigo_barras_bd(vinos_dict: dict, codigo: str) -> dict | None:
    """
    Busca un vino en la BD local por código de barras (EAN/GTIN).
    Si el vino tiene campo opcional 'ean' o 'codigo_barras', lo compara con codigo (solo dígitos).
    :return: primer vino que coincida o None
    """
    if not vinos_dict or not codigo:
        return None
    codigo_limpio = re.sub(r"\D", "", str(codigo).strip())
    if len(codigo_limpio) < 8 or len(codigo_limpio) > 14:
        return None
    for key, vino in vinos_dict.items():
        if not isinstance(vino, dict):
            continue
        for campo in ("ean", "codigo_barras", "gtin"):
            val = vino.get(campo)
            if not val:
                continue
            val_limpio = re.sub(r"\D", "", str(val).strip())
            if val_limpio == codigo_limpio:
                return {"key": key, "vino": vino}
    return None


def buscar_vinos_avanzado(vinos_dict: dict, texto: str, limite: int = 5, precio_max: float | None = None, tipo: str | None = None) -> list:
    """
    Búsqueda mejorada en el diccionario de vinos:
    - Prioridad: si se menciona "ribera" / "ribera del duero", solo vinos de esa región
    - Usa nombre, bodega, región y uva_principal; tolera errores ortográficos (fuzzy matching)
    - Acepta filtros en el texto: precio máximo (menos de 20€) y tipo (tinto, blanco, etc.)
    - Ordena por relevancia (score)
    """
    texto_norm = normalizar_texto(texto)
    if precio_max is None:
        precio_max = _extraer_precio_max(texto_norm)
    if tipo is None:
        tipo = _extraer_tipo(texto_norm)

    vinos_a_buscar = vinos_dict
    region_prioritaria = _detectar_region_prioritaria(texto_norm)
    if region_prioritaria:
        region_norm = normalizar_texto(region_prioritaria)
        vinos_a_buscar = {
            k: v for k, v in vinos_dict.items()
            if isinstance(v, dict) and region_norm in normalizar_texto(v.get("region") or "")
        }
        if not vinos_a_buscar:
            return []

    tokens = obtener_tokens_busqueda(texto)
    resultados = []

    for key, vino in vinos_a_buscar.items():
        vino_tipo = (vino.get("tipo") or "").strip().lower()
        if tipo and vino_tipo and tipo not in vino_tipo:
            continue
        if precio_max is not None and precio_max > 0:
            p = _precio_num(vino.get("precio") or "")
            if p > precio_max:
                continue

        nombre = normalizar_texto(vino.get("nombre", ""))
        bodega = normalizar_texto(vino.get("bodega", ""))
        region = normalizar_texto(vino.get("region", ""))
        uva = normalizar_texto(vino.get("uva_principal") or "")

        score = 0.0
        if nombre and nombre == texto_norm:
            score += 100.0

        for token in tokens:
            for valor, peso in [
                (nombre, PESOS_CAMPO["nombre"]),
                (bodega, PESOS_CAMPO["bodega"]),
                (region, PESOS_CAMPO["region"]),
                (uva, PESOS_CAMPO["uva_principal"]),
            ]:
                if not valor:
                    continue
                if token in valor:
                    score += peso
                else:
                    mejor_sim = 0.0
                    for palabra_campo in valor.split():
                        sim = similitud_palabras(token, palabra_campo)
                        if sim > mejor_sim:
                            mejor_sim = sim
                    if mejor_sim >= 0.78:
                        score += peso * mejor_sim

        if score > 0:
            resultados.append({
                "score": score,
                "key": key,
                "vino": vino,
                "puntuacion": vino.get("puntuacion") or 0,
            })

    if region_prioritaria:
        resultados.sort(key=lambda r: -r["puntuacion"])
    else:
        resultados.sort(key=lambda r: r["score"], reverse=True)
    return resultados[:limite]


def buscar_vinos_con_sugerencia(vinos_dict: dict, texto: str, limite: int = 5) -> dict:
    """
    Igual que buscar_vinos_avanzado pero devuelve además 'quizas_quisiste_decir' cuando
    la búsqueda es de un solo token y el mejor resultado coincide por fuzzy (no exacto).
    Return: {"resultados": list, "quizas_quisiste_decir": str | None}
    """
    resultados = buscar_vinos_avanzado(vinos_dict, texto, limite=limite)
    tokens = obtener_tokens_busqueda(texto)
    sugerencia = None
    if len(tokens) == 1 and resultados:
        token = tokens[0]
        top = resultados[0]
        v = top.get("vino") or {}
        nombre_norm = normalizar_texto(v.get("nombre") or "")
        if token != nombre_norm and token not in nombre_norm:
            if similitud_palabras(token, nombre_norm.split()[0] if nombre_norm else "") >= 0.78 or any(
                similitud_palabras(token, p) >= 0.78 for p in nombre_norm.split()
            ):
                sugerencia = v.get("nombre")
    return {"resultados": resultados, "quizas_quisiste_decir": sugerencia}
