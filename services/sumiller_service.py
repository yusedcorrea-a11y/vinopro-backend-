"""
Servicio para el Sumiller Virtual: maridajes y recomendaciones desde la base de vinos,
soporte de contexto (últimas preguntas) y fallback cuando no hay resultados (conocimiento + similares).
"""
import json
import re
from pathlib import Path
from typing import Any

# Ruta al conocimiento de tipos de vino (fallback cuando no hay coincidencias)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONOCIMIENTO_PATH = DATA_DIR / "conocimiento_vinos.json"
_conocimiento_cache: dict | None = None


def _cargar_conocimiento() -> dict:
    global _conocimiento_cache
    if _conocimiento_cache is not None:
        return _conocimiento_cache
    if not CONOCIMIENTO_PATH.is_file():
        _conocimiento_cache = {"tipos": {}, "claves_busqueda": {}}
        return _conocimiento_cache
    try:
        with open(CONOCIMIENTO_PATH, "r", encoding="utf-8") as f:
            _conocimiento_cache = json.load(f)
    except Exception:
        _conocimiento_cache = {"tipos": {}, "claves_busqueda": {}}
    return _conocimiento_cache

# Palabras clave de comida para maridaje
MARIDAJE_PALABRAS = {
    "carne": ["carne", "carnes", "solomillo", "ternera", "vacío", "chuletón", "entrecot"],
    "pescado": ["pescado", "pescados", "marisco", "mariscos", "salmón", "salmon", "bacalao", "atún", "tuna", "lubina", "dorada"],
    "cordero": ["cordero", "cordero asado", "lechazo"],
    "caza": ["caza", "caza mayor", "jabalí", "jabali", "venado", "perdiz"],
    "queso": ["queso", "quesos", "curados"],
    "pasta": ["pasta", "arroz", "risotto"],
    "ensalada": ["ensalada", "verduras", "vegetal"],
    "postre": ["postre", "dulce", "chocolate"],
}

# Cocinas del mundo / platos específicos -> tipos de vino o palabras para buscar en nombre/descripción
MARIDAJE_COCINA = {
    "india": ["tikka", "masala", "curry", "india", "indio", "indios", "especiado", "especiada"],
    "china": ["china", "chino", "wok", "sweet and sour", "agridulce", "pato laqueado"],
    "japonesa": ["japon", "japones", "sushi", "sashimi", "sake", "koshu", "umami", "tempura"],
}
# Para cocina india/especiada: priorizar blancos aromáticos (Chenin, Gewürztraminer, Riesling) y vinos indios por nombre
PALABRAS_VINO_COCINA_INDIA = ["chenin", "gewürztraminer", "gewurztraminer", "riesling", "sula", "india", "blanco"]
PALABRAS_VINO_ASIA = ["gewürztraminer", "gewurztraminer", "riesling", "blanco", "koshu", "sake", "sula", "china", "japon", "india"]

# Términos de perfil de gusto para recomendaciones
PREFERENCIA_TIPO = {"tinto": "tinto", "tintos": "tinto", "blanco": "blanco", "blancos": "blanco", "rosado": "rosado", "rosados": "rosado", "espumoso": "espumoso", "espumosos": "espumoso", "dulce": "dulce"}
PREFERENCIA_ESTILO = ["robusto", "potente", "ligero", "elegante", "frutal", "mineral", "tanino", "taninos", "crianza", "roble", "suave", "afrutado", "seco", "dulce"]

# País/región mencionados en texto -> valor para filtrar en vino.pais (debe coincidir con data/*.json)
PAIS_REGION_PALABRAS = {
    "Argentina": ["argentino", "argentina", "mendoza", "malbec"],
    "España": ["español", "española", "españa", "espana", "rioja", "ribera", "priorat", "ribera del duero", "cataluña"],
    "Chile": ["chileno", "chile", "carmenere"],
    "Francia": ["francés", "frances", "francia", "burdeos", "borgoña", "champagne"],
    "Italia": ["italiano", "italiana", "italia", "toscana", "piamonte"],
    "Portugal": ["portugués", "portugues", "portugal", "dão", "douro"],
    "Estados Unidos": ["americano", "americana", "california", "napa", "estados unidos"],
    "Australia": ["australiano", "australia"],
    "Nueva Zelanda": ["nueva zelanda", "zelanda", "marlborough"],
    "Alemania": ["alemán", "alemana", "alemania", "riesling"],
    "Brasil": ["brasileño", "brasileña", "brasil", "serra gaúcha", "vale dos vinhedos", "campanha"],
    "Turquía": ["turco", "turca", "turquía", "turquia", "anatolia", "öküzgözü", "boğazkere", "tracia"],
    "Rusia": ["ruso", "rusa", "rusia", "krasnodar", "crimea", "saperavi"],
    "China": ["chino", "china", "ningxia", "yantai", "changyu", "grace vineyard"],
    "Japón": ["japonés", "japones", "japón", "japon", "yamanashi", "koshu", "muscat bailey"],
    "Corea": ["coreano", "coreana", "corea", "yeongdong", "jeju", "campbell early", "meoru"],
    "India": ["indio", "india", "nashik", "sula", "fratelli", "grover zampa"],
    "Líbano": ["libanes", "libanés", "libano", "líbano", "bekaa", "musar", "château musar"],
    "Marruecos": ["marruecos", "marroquí", "marroqui", "atlas", "meknès", "méknès"],
    "Argelia": ["argelino", "argelia", "mascara"],
    "Túnez": ["tunecino", "túnez", "tunez", "tunisia", "mornag", "nabeul"],
    "Israel": ["israelí", "israeli", "israel", "golan", "galilea", "yarden", "dalton"],
}


def _normalizar(t: str) -> str:
    if not t or not isinstance(t, str):
        return ""
    return re.sub(r"[^a-z0-9áéíóúüñ ]+", " ", t.lower().strip())


def _es_cocina_especial(comida_norm: str) -> str | None:
    """Devuelve 'india', 'china' o 'japonesa' si la comida encaja en esa cocina."""
    for cocina, palabras in MARIDAJE_COCINA.items():
        if any(p in comida_norm for p in palabras):
            return cocina
    return None


def buscar_vinos_por_maridaje(
    vinos_dict: dict, comida: str, limite: int = 5, exclude_keys: list[str] | None = None
) -> list[dict]:
    """
    Busca vinos cuyo campo maridaje coincida con la comida indicada.
    Soporta cocinas del mundo (india, china, japonesa): prioriza blancos aromáticos y vinos de la región.
    exclude_keys: keys ya recomendadas en esta sesión para no repetir la misma respuesta.
    Devuelve lista de { "key", "vino" } ordenada por puntuación (mejor primero).
    """
    comida_norm = _normalizar(comida)
    if not comida_norm:
        return []
    exclude = set((exclude_keys or []))
    tokens = [w for w in comida_norm.split() if len(w) > 2]
    cocina = _es_cocina_especial(comida_norm)
    palabras_vinos_especial = PALABRAS_VINO_COCINA_INDIA if cocina == "india" else PALABRAS_VINO_ASIA if cocina else []

    resultados = []
    for key, vino in vinos_dict.items():
        if key in exclude or not isinstance(vino, dict):
            continue
        maridaje = _normalizar(vino.get("maridaje") or "")
        nombre = _normalizar(vino.get("nombre") or "")
        desc = _normalizar(vino.get("descripcion") or "")
        tipo = (vino.get("tipo") or "").strip().lower()
        uva = _normalizar(vino.get("uva_principal") or "")
        pais = _normalizar(vino.get("pais") or "")
        concat = nombre + " " + desc + " " + uva + " " + pais
        score = 0
        for t in tokens:
            if maridaje and t in maridaje:
                score += 2
            elif maridaje and any(t in m for m in maridaje.split()):
                score += 1
        for categoria, palabras in MARIDAJE_PALABRAS.items():
            if any(p in comida_norm for p in palabras) and maridaje and any(p in maridaje for p in palabras):
                score += 3
                break
        if cocina and palabras_vinos_especial:
            for pv in palabras_vinos_especial:
                if pv in concat or pv in tipo:
                    score += 4
            if tipo == "blanco" and any(u in concat for u in ["chenin", "gewurz", "riesling", "gewürz"]):
                score += 3
        if score > 0:
            resultados.append({
                "score": score,
                "key": key,
                "vino": vino,
                "puntuacion": vino.get("puntuacion") or 0,
            })
    resultados.sort(key=lambda x: (-x["score"], -x["puntuacion"]))
    return [{"key": r["key"], "vino": r["vino"]} for r in resultados[:limite]]


def _precio_maximo_num(precio_str: str) -> float:
    """Extrae el número máximo de un precio (ej. '25-35€' -> 35, '18€' -> 18)."""
    if not precio_str or not isinstance(precio_str, str):
        return 0.0
    nums = re.findall(r"[0-9]+", precio_str.replace(",", "."))
    return max([float(n) for n in nums]) if nums else 0.0


def _extraer_precio_max_usuario(texto: str) -> float | None:
    """Si el usuario pide 'menos de 20€' / 'por menos de 20' / 'barato', devuelve 20 o un tope razonable."""
    texto_norm = _normalizar(texto)
    # "menos de 20", "por menos de 20", "20 euros", "por debajo de 25"
    match = re.search(r"(?:menos de|por menos de|debajo de|maximo|máximo)\s*(\d+)", texto_norm)
    if match:
        return float(match.group(1))
    match = re.search(r"(\d+)\s*(?:euros?|eur|€)", texto_norm)
    if match:
        return float(match.group(1))
    if any(p in texto_norm for p in ["barato", "economico", "económico", "bueno y barato"]):
        return 25.0
    return None


def _extraer_pais_o_region(texto: str) -> str | None:
    """Devuelve el país (como en BD) si el usuario menciona uno."""
    texto_norm = _normalizar(texto)
    for pais, palabras in PAIS_REGION_PALABRAS.items():
        if any(p in texto_norm for p in palabras):
            return pais
    return None


def _extraer_region_prioritaria(texto: str) -> str | None:
    """Si el usuario pide explícitamente una región (ej. Ribera del Duero), devuelve su nombre exacto."""
    texto_norm = _normalizar(texto)
    if "ribera" in texto_norm and ("duero" in texto_norm or len(texto_norm) < 25):
        return "Ribera del Duero"
    return None


def buscar_vinos_por_preferencia(
    vinos_dict: dict, texto: str, limite: int = 5, exclude_keys: list[str] | None = None
) -> list[dict]:
    """
    Busca vinos que coincidan con la preferencia: tipo, país/región, precio máximo, estilo.
    Prioridad: si menciona "ribera" / "ribera del duero", solo vinos de esa región.
    exclude_keys: keys ya recomendadas en esta sesión para no repetir.
    """
    exclude = set((exclude_keys or []))
    texto_norm = _normalizar(texto)
    # Prioridad región: Ribera del Duero
    region_prioritaria = _extraer_region_prioritaria(texto)
    if region_prioritaria:
        vinos_dict = {
            k: v for k, v in vinos_dict.items()
            if k not in exclude and isinstance(v, dict) and _normalizar(v.get("region") or "") == _normalizar(region_prioritaria)
        }
        if not vinos_dict:
            return []
        lista = [
            {"key": k, "vino": v, "puntuacion": v.get("puntuacion") or 0}
            for k, v in vinos_dict.items()
        ]
        lista.sort(key=lambda x: -x["puntuacion"])
        return [{"key": r["key"], "vino": r["vino"]} for r in lista[:limite]]

    tipo_buscado = None
    for t, v in PREFERENCIA_TIPO.items():
        if t in texto_norm:
            tipo_buscado = v
            break
    pais_buscado = _extraer_pais_o_region(texto)
    precio_max = _extraer_precio_max_usuario(texto)
    estilos = [e for e in PREFERENCIA_ESTILO if e in texto_norm]

    resultados = []
    for key, vino in vinos_dict.items():
        if key in exclude or not isinstance(vino, dict):
            continue
        tipo = (vino.get("tipo") or "").strip().lower()
        if tipo not in ("tinto", "blanco", "rosado", "espumoso", "dulce"):
            tipo = "tinto"
        pais = (vino.get("pais") or "").strip()
        region = _normalizar(vino.get("region") or "")
        desc = _normalizar(vino.get("descripcion") or "")
        notas = _normalizar(vino.get("notas_cata") or "")
        concat = desc + " " + notas
        puntuacion = vino.get("puntuacion") or 0
        precio_num = _precio_maximo_num(vino.get("precio_estimado") or "")

        # Filtro por precio máximo
        if precio_max is not None and precio_num > 0 and precio_num > precio_max:
            continue
        # Filtro por país
        if pais_buscado:
            if (pais or "").strip() != pais_buscado and pais_buscado.lower() not in region:
                continue
        score = 0
        if tipo_buscado:
            if tipo == tipo_buscado:
                score += 10
            else:
                continue  # si pidió tipo concreto, solo ese tipo
        else:
            if tipo:
                score += 1
        if pais_buscado and (pais == pais_buscado or pais_buscado.lower() in region):
            score += 5
        for e in estilos:
            if e in concat:
                score += 3
        for w in texto_norm.split():
            if len(w) > 3 and w not in ("gustan", "gusta", "quiero", "busco", "vino", "vinos", "los", "las", "una", "unos", "recomendacion", "recomendaciones", "recomienda", "recomiendas", "recomiendame", "puedes", "hacer", "me"):
                if w in concat:
                    score += 2
        # Priorizar por puntuación cuando hay empate
        resultados.append({
            "score": score,
            "key": key,
            "vino": vino,
            "puntuacion": puntuacion,
        })
    resultados.sort(key=lambda x: (-x["score"], -x["puntuacion"]))
    return [{"key": r["key"], "vino": r["vino"]} for r in resultados[:limite]]


def formatear_respuesta_maridaje(vinos: list[dict], comida: str, perfil: str = "aficionado") -> str:
    """Genera texto elegante con recomendaciones de maridaje. Soporta cocina india/china/japonesa."""
    if not vinos:
        return "No tenemos en la carta vinos especialmente recomendados para ese plato. Puedo recomendarte tintos para carne, blancos para pescado o cordero si me dices qué prefieres."
    comida_low = comida.lower()
    intro = "Para "
    if any(p in comida_low for p in ["tikka", "masala", "curry", "india", "indio"]):
        intro += "la cocina india especiada, "
    elif any(p in comida_low for p in ["china", "chino", "wok"]):
        intro += "la cocina china, "
    elif any(p in comida_low for p in ["japon", "japones", "sushi", "sashimi"]):
        intro += "la cocina japonesa, "
    elif any(p in comida_low for p in ["cordero", "lechazo"]):
        intro += "un cordero asado, "
    elif "carne" in comida_low or "ternera" in comida_low:
        intro += "carnes rojas, "
    elif "pescado" in comida_low or "marisco" in comida_low:
        intro += "pescado o marisco, "
    else:
        intro += f"\"{comida.strip()}\", "
    intro += "le recomiendo "
    partes = []
    for i, item in enumerate(vinos[:5]):
        v = item["vino"]
        nombre = v.get("nombre") or "—"
        bodega = v.get("bodega") or "—"
        region = v.get("region") or ""
        pais = v.get("pais") or ""
        if i == 0:
            partes.append(f"un {nombre} ({bodega}, {region})")
        else:
            partes.append(f"{nombre} ({bodega})")
    if len(partes) == 1:
        texto = intro + partes[0] + "."
    else:
        texto = intro + ", ".join(partes[:-1]) + " y " + partes[-1] + "."
    if perfil == "principiante" and ("crianza" in texto or "tanino" in texto or "roble" in texto):
        texto += " (Crianza: tiempo en barrica; taninos: sensación en boca; roble: madera que aporta especias.)"
    return texto


def _descripcion_corta(vino: dict, max_chars: int = 85) -> str:
    """Primera frase o fragmento de descripción/notas para la recomendación."""
    desc = (vino.get("descripcion") or "").strip()
    notas = (vino.get("notas_cata") or "").strip()
    texto = (desc + " " + notas).strip() or "Vino de calidad."
    if len(texto) <= max_chars:
        return texto
    cortado = texto[: max_chars + 1].rsplit(" ", 1)[0] if " " in texto[: max_chars + 1] else texto[:max_chars]
    return cortado + "…" if len(cortado) < len(texto) else cortado


def formatear_respuesta_recomendacion(vinos: list[dict], perfil: str = "aficionado", tipo_pedido: str = "") -> str:
    """Genera respuesta con recomendaciones reales: nombre, bodega, región, descripción breve y precio."""
    if not vinos:
        return "No hay vinos en la base que encajen con esa preferencia en este momento."
    intro = "¡Claro! Basado en nuestra base de datos, estos son los que mejor encajan"
    if tipo_pedido:
        intro += f" ({tipo_pedido})"
    intro += ":\n\n"
    lineas = []
    for item in vinos[:5]:
        v = item["vino"]
        nombre = v.get("nombre") or "—"
        bodega = v.get("bodega") or "—"
        region = (v.get("region") or "").strip()
        pais = (v.get("pais") or "").strip()
        precio = v.get("precio_estimado") or "consultar"
        desc_corta = _descripcion_corta(v)
        ubicacion = f"{region}, {pais}" if region and pais else (region or pais or "")
        lineas.append(f"🍷 {nombre} ({ubicacion})\n   {desc_corta}. {precio}")
    texto = intro + "\n".join(lineas) + "\n\n¿Te interesa alguno en particular? Puedo darte más detalles."
    if perfil == "principiante":
        texto += " (Si quieres el más económico o el mejor valorado de estos, pregúntamelo.)"
    return texto


def _buscar_similares_por_tipo_o_pais(vinos_dict: dict, tipo: str | None, pais: str | None, limite: int = 3) -> list[dict]:
    """Devuelve vinos del mismo tipo o país, ordenados por puntuación."""
    candidatos = []
    tipo = (tipo or "").strip().lower() if tipo else None
    pais = (pais or "").strip() if pais else None
    for key, vino in vinos_dict.items():
        if not isinstance(vino, dict):
            continue
        t = (vino.get("tipo") or "").strip().lower()
        p = (vino.get("pais") or "").strip()
        if tipo and t == tipo:
            candidatos.append({"key": key, "vino": vino, "puntuacion": vino.get("puntuacion") or 0})
        elif pais and p == pais:
            candidatos.append({"key": key, "vino": vino, "puntuacion": vino.get("puntuacion") or 0})
    candidatos.sort(key=lambda x: -x["puntuacion"])
    return candidatos[:limite]


def _pais_desde_origen(origen: str) -> str | None:
    """Extrae el país principal desde el campo origen (ej. 'Emilia-Romagna, Italia' -> 'Italia')."""
    if not origen or not isinstance(origen, str):
        return None
    # Mapeo de nombres en conocimiento a como están en la BD
    for term in ["Italia", "España", "Argentina", "Chile", "Francia", "Portugal", "Alemania", "Estados Unidos", "Australia", "Nueva Zelanda"]:
        if term in origen:
            return term
    parte = origen.strip().split(",")[-1].strip() if "," in origen else origen.strip()
    return parte if parte else None


def _buscar_vinos_por_palabras(vinos_dict: dict, palabras: list[str], limite: int = 5) -> list[dict]:
    """Vinos cuyo nombre o descripción contienen alguna de las palabras (normalizadas)."""
    resultados = []
    for key, vino in vinos_dict.items():
        if not isinstance(vino, dict):
            continue
        concat = _normalizar((vino.get("nombre") or "") + " " + (vino.get("descripcion") or "") + " " + (vino.get("uva_principal") or ""))
        for p in palabras:
            if p in concat:
                resultados.append({"key": key, "vino": vino, "puntuacion": vino.get("puntuacion") or 0})
                break
    resultados.sort(key=lambda x: -x["puntuacion"])
    return [{"key": r["key"], "vino": r["vino"]} for r in resultados[:limite]]


def fallback_sin_resultados(pregunta: str, vinos_dict: dict) -> tuple[str, list[dict]]:
    """
    Cuando no hay vinos en la base que coincidan: información real del tipo de vino
    (desde conocimiento_vinos.json) y sugerencia de vinos similares de la BD.
    Para cocina india/china/japonesa ofrece texto específico y blancos aromáticos si hay.
    """
    conocimiento = _cargar_conocimiento()
    tipos = conocimiento.get("tipos") or {}
    claves_busqueda = conocimiento.get("claves_busqueda") or {}
    pregunta_norm = _normalizar(pregunta)

    cocina = _es_cocina_especial(pregunta_norm)
    if cocina == "india":
        similares_cocina = _buscar_vinos_por_palabras(vinos_dict, [x for x in PALABRAS_VINO_COCINA_INDIA if len(x) > 3], limite=5)
        if similares_cocina:
            texto = "Para la cocina india especiada (pollo tikka masala, curry, etc.) recomendamos un blanco aromático: Chenin Blanc, Gewürztraminer o Riesling. En nuestra carta:"
            return texto, similares_cocina
        texto = "Para la cocina india especiada recomendamos un Sula Chenin Blanc (India) o un Gewürztraminer alsaciano. No tenemos esos vinos exactos en la carta; aquí van alternativas que pueden ir bien:"
        todos = [{"key": k, "vino": v, "puntuacion": (v.get("puntuacion") or 0) if isinstance(v, dict) else 0} for k, v in vinos_dict.items() if isinstance(v, dict)]
        todos.sort(key=lambda x: -x["puntuacion"])
        return texto, [{"key": r["key"], "vino": r["vino"]} for r in todos[:3]]
    if cocina in ("china", "japonesa"):
        similares_cocina = _buscar_vinos_por_palabras(vinos_dict, [x for x in PALABRAS_VINO_ASIA if len(x) > 3], limite=5)
        if similares_cocina:
            texto = f"Para la cocina {cocina} recomendamos blancos aromáticos o ligeros (Riesling, Gewürztraminer, Koshu). En nuestra carta:"
            return texto, similares_cocina

    info_tipo = None
    tipo_key = None
    for clave, palabras in claves_busqueda.items():
        if any(p in pregunta_norm for p in palabras):
            tipo_key = clave
            info_tipo = tipos.get(clave)
            break

    if not info_tipo:
        for t in ["tinto", "blanco", "rosado", "espumoso"]:
            if t in pregunta_norm:
                tipo_key = t
                break

    similares = []
    pais_para_similares = None
    if tipo_key and isinstance(tipos.get(tipo_key), dict):
        origen = tipos.get(tipo_key, {}).get("origen", "")
        pais_para_similares = _pais_desde_origen(origen)
        tipo_buscado = tipos.get(tipo_key, {}).get("tipo") or tipo_key
        if pais_para_similares:
            similares = _buscar_similares_por_tipo_o_pais(vinos_dict, None, pais_para_similares, limite=3)
        if not similares:
            similares = _buscar_similares_por_tipo_o_pais(vinos_dict, tipo_buscado, None, limite=3)
    elif tipo_key:
        tipo_buscado = tipo_key
        similares = _buscar_similares_por_tipo_o_pais(vinos_dict, tipo_buscado, None, limite=3)
    if not similares:
        todos = [{"key": k, "vino": v, "puntuacion": (v.get("puntuacion") or 0) if isinstance(v, dict) else 0} for k, v in vinos_dict.items() if isinstance(v, dict)]
        todos.sort(key=lambda x: -x["puntuacion"])
        similares = todos[:3]

    lineas = []
    if info_tipo and isinstance(info_tipo, dict):
        nombre_tipo = info_tipo.get("nombre") or tipo_key or "ese vino"
        tipo_vino = info_tipo.get("tipo") or "tinto"
        origen = info_tipo.get("origen") or ""
        desc = info_tipo.get("descripcion") or ""
        ejemplos = info_tipo.get("ejemplos_famosos") or ""
        maridaje = info_tipo.get("maridaje") or ""
        lineas.append(f"El {nombre_tipo} es un vino {tipo_vino} originario de la región de {origen}. {desc}")
        lineas.append("")
        lineas.append("Los más famosos son:")
        for ej in [e.strip() for e in ejemplos.split(",")]:
            if ej:
                lineas.append(f"🍾 {ej}")
        lineas.append("")
        lineas.append(f"Maridaje típico: {maridaje}.")
        lineas.append("")
        if similares:
            region_label = f"vinos de {pais_para_similares}" if pais_para_similares else "vinos que te pueden interesar"
            lineas.append(f"En nuestra base de datos no tenemos {nombre_tipo} actualmente, pero sí estos excelentes {region_label}:")
        else:
            lineas.append(f"En nuestra base no tenemos {nombre_tipo} en este momento. Aquí van algunos de los mejor valorados:")
            todos = [{"key": k, "vino": v, "puntuacion": (v.get("puntuacion") or 0) if isinstance(v, dict) else 0} for k, v in vinos_dict.items() if isinstance(v, dict)]
            todos.sort(key=lambda x: -x["puntuacion"])
            similares = [{"key": r["key"], "vino": r["vino"]} for r in todos[:3]]
            lineas.append("")
            for item in similares:
                v = item["vino"]
                nombre = v.get("nombre") or "—"
                region = (v.get("region") or "").strip()
                pais = (v.get("pais") or "").strip()
                precio = v.get("precio_estimado") or "consultar"
                ubicacion = f"{region}, {pais}" if region and pais else (region or pais or "")
                lineas.append(f"🍷 {nombre} ({ubicacion}) — {precio}")
            lineas.append("")
            lineas.append("¿Quieres que te cuente más sobre alguno de ellos?")
            return ("\n".join(lineas), similares)
    else:
        lineas.append("No hemos encontrado ese vino concreto en nuestra base.")
        lineas.append("")
        if similares:
            lineas.append("Estos son algunos de los mejor valorados que sí tenemos:")
        else:
            todos = [{"key": k, "vino": v, "puntuacion": (v.get("puntuacion") or 0) if isinstance(v, dict) else 0} for k, v in vinos_dict.items() if isinstance(v, dict)]
            todos.sort(key=lambda x: -x["puntuacion"])
            similares = [{"key": r["key"], "vino": r["vino"]} for r in todos[:3]]
            if similares:
                lineas.append("Algunos de los mejor valorados:")
            else:
                return ("\n".join(lineas), [])

    if similares:
        lineas.append("")
        for item in similares:
            v = item["vino"]
            nombre = v.get("nombre") or "—"
            region = (v.get("region") or "").strip()
            pais = (v.get("pais") or "").strip()
            precio = v.get("precio_estimado") or "consultar"
            ubicacion = f"{region}, {pais}" if region and pais else (region or pais or "")
            lineas.append(f"🍷 {nombre} ({ubicacion}) — {precio}")
        lineas.append("")
        lineas.append("¿Quieres que te cuente más sobre alguno de ellos?")
    return ("\n".join(lineas), similares)


def resolver_contexto_esos(vinos_ref: list, pregunta: str, vinos_dict: dict) -> str | None:
    """
    Si la pregunta referencia 'de esos' / 'el más económico' / 'el más caro',
    usa vinos_ref (lista de keys o dicts de la última respuesta) para responder.
    """
    print("[SUMILLER] VINOS_REF RECIBIDOS:", vinos_ref)
    if not vinos_ref or not isinstance(vinos_ref, list):
        return None
    pregunta_norm = _normalizar(pregunta)
    if not pregunta_norm:
        return None
    # Normalizar acentos para detectar "económico" / "economico", "más" / "mas"
    pregunta_sin_acentos = pregunta_norm.replace("ó", "o").replace("á", "a").replace("í", "i").replace("é", "e").replace("ú", "u")
    disparadores = [
        "esos", "esas", "el mas", "el más", "economico", "económico", "caro", "barato",
        "mejor", "peor", "mas barato", "más barato", "el mas barato", "el más barato",
        "mas caro", "más caro", "mas economico"
    ]
    if not any((p in pregunta_norm) or (p in pregunta_sin_acentos) for p in disparadores):
        return None
    # Reconstruir vinos desde keys o nombres
    candidatos = []
    for ref in vinos_ref:
        if isinstance(ref, dict):
            candidatos.append(ref)
        elif ref in vinos_dict:
            v = vinos_dict[ref]
            if isinstance(v, dict):
                candidatos.append(v)
        else:
            for v in vinos_dict.values():
                if isinstance(v, dict) and ((v.get("nombre") or "").strip() == ref or ref in (v.get("nombre") or "")):
                    candidatos.append(v)
                    break
    if not candidatos:
        return None

    def _precio_num(val: str) -> float:
        if not val or not isinstance(val, str):
            return 0.0
        import re as re2
        nums = re2.findall(r"[0-9]+", val.replace(",", "."))
        return float(nums[0]) if nums else 0.0

    if "economico" in pregunta_sin_acentos or "económico" in pregunta_norm or "barato" in pregunta_norm:
        con_precio = [(v, _precio_num(v.get("precio_estimado") or "")) for v in candidatos]
        con_precio.sort(key=lambda x: (x[1] if x[1] > 0 else 9999, -(x[0].get("puntuacion") or 0)))
        v = con_precio[0][0]
        return f"De los que le recomendé, el más económico es {v.get('nombre', '—')} ({v.get('bodega', '—')}): {v.get('precio_estimado', 'consultar')}."
    if "caro" in pregunta_norm and "barato" not in pregunta_norm:
        con_precio = [(v, _precio_num(v.get("precio_estimado") or "")) for v in candidatos]
        con_precio.sort(key=lambda x: (-x[1], -(x[0].get("puntuacion") or 0)))
        v = con_precio[0][0]
        return f"De los citados, el de mayor precio es {v.get('nombre', '—')} ({v.get('bodega', '—')}): {v.get('precio_estimado', 'consultar')}."
    if "mejor" in pregunta_norm or "recomienda" in pregunta_norm:
        ordenados = sorted(candidatos, key=lambda v: -(v.get("puntuacion") or 0))
        v = ordenados[0]
        return f"De esos, le recomiendo especialmente {v.get('nombre', '—')} ({v.get('bodega', '—')}), con {v.get('puntuacion', '—')} puntos de valoración."
    return None
