"""
Normalizador de texto OCR: corrige errores típicos de lectura (Tesseract) en etiquetas
para mejorar el match en BD y la experiencia con el sumiller.
"""
import re

# Correcciones: texto erróneo (OCR) -> texto corregido. Se aplican en orden.
# Claves se reemplazan sin distinguir mayúsculas/minúsculas.
# IMPORTANTE: primero se colapsan espacios/saltos de línea para que "Sina\nPadwosa" -> "Sina Padwosa".
CORRECCIONES = [
    # Viña Pedrosa y variantes (Sadhosi, Padwosa con/sin salto de línea)
    ("Sina Padwosa", "Viña Pedrosa"),
    ("Sina Sadhosi", "Viña Pedrosa"),
    ("Sina Pedrosa", "Viña Pedrosa"),
    ("Sados", "Viña Pedrosa"),
    ("Vina Pedrosa", "Viña Pedrosa"),
    ("Sadhosi", "Pedrosa"),
    ("Padwosa", "Pedrosa"),
    # Bodega
    ("BopEGAs", "Bodegas"),
    ("BopEGas", "Bodegas"),
    ("Bobgcas", "Bodegas"),
    ("BobeGas", "Bodegas"),
    ("Bobgcas HNos.", "Bodegas Hnos."),
    ("HNos.", "Hnos."),
    ("HINOs.", "Hnos."),
    ("PEREZ PASCUAS", "Pérez Pascuas"),
    ("Perez Pascuas", "Pérez Pascuas"),
    ("PERE ", "Pérez "),  # "Hnos. PERE GCRIANZA" -> "Hnos. Pérez GCRIANZA"
    # Crianza / año
    ("GCRIANZA", "CRIANZA"),
    ("BO21", "2021"),
    ("DO21", "2021"),
    # Ribera del Duero
    ("RIBERA pet DUERO", "Ribera del Duero"),
    ("RIBERA peL DUERO", "Ribera del Duero"),
    ("RIBERA pet", "Ribera del"),
    ("RIBERA peL", "Ribera del"),
    ("pet DUERO", "del Duero"),
    ("peL DUERO", "del Duero"),
    ("pet [DUERO", "del Duero"),
    ("[DUERO", "Duero"),
    ("RiBER A He", "Ribera del"),
    ("RIBERA ppL", "Ribera del"),
    ("ppL DUERO", "del Duero"),
    # Denominaciones
    ("DENomINaciOn DEORIGEN", "Denominación de Origen"),
    ("DENOMINACION DEORIGEN", "Denominación de Origen"),
    ("Denommn ACION DE ORIGEN", "Denominación de Origen"),
    ("Denommn ACION", "Denominación"),
    ("MINACION DEORO*", "Denominación de Origen"),
    ("MINACION DEORO", "Denominación de Origen"),
    ("Denomanac ION DE ORIGEN", "Denominación de Origen"),
    # Protos / producto España
    ("propucto", "Producto"),
    ("PROpucto pe ESPANA", "Producto de España"),
    ("PRopucto pe ESPANA", "Producto de España"),
    ("Gin 9\"", "Protos"),
    ("Est. 1927", "Protos"),
    ("ROBLE", "Roble"),
]

# Palabras basura conocidas del OCR (se eliminan como token completo)
PALABRAS_BASURA = {"mh", "suto", "fop"}

# Palabras cortas que SÍ conservamos (1-3 letras útiles)
PALABRAS_CORTAS_OK = {"del", "de", "el", "la", "y", "en", "al", "un", "una", "los", "las"}


def _quitar_palabras_basura_cortas(texto: str) -> str:
    """Elimina palabras de 1-3 letras que suelen ser errores OCR, excepto del, de, el, la, etc."""
    if not texto or not texto.strip():
        return texto
    palabras = texto.split()
    filtradas = []
    for p in palabras:
        p_low = p.lower()
        if p_low in PALABRAS_BASURA:
            continue
        if len(p) <= 3 and p_low not in PALABRAS_CORTAS_OK:
            continue
        filtradas.append(p)
    return " ".join(filtradas)


def _quitar_tokens_solo_numeros(texto: str) -> str:
    """Quita tokens que son solo dígitos o comillas+dígitos (ej. 420342, 00201, \"420342\"). Mejora la búsqueda en BD y OFF."""
    if not texto or not texto.strip():
        return texto
    palabras = texto.split()
    filtradas = []
    for p in palabras:
        limpio = p.strip().strip('"\'')
        if limpio.isdigit():
            continue
        filtradas.append(p)
    return " ".join(filtradas)


def limpiar(texto_sucio: str) -> str:
    """
    Aplica correcciones conocidas de OCR al texto.
    Primero colapsa saltos de línea y espacios para que "Sina\\nPadwosa" -> "Sina Padwosa".
    No modifica el texto si está vacío. Devuelve string normalizado.
    """
    if not texto_sucio or not isinstance(texto_sucio, str):
        return (texto_sucio or "").strip()
    texto = texto_sucio.strip()
    if not texto:
        return ""
    # Primero: colapsar todos los espacios y saltos de línea a un solo espacio,
    # para que "Sina\nPadwosa" y "Sina  Padwosa" se conviertan en "Sina Padwosa".
    texto = re.sub(r"\s+", " ", texto)
    for error, correccion in CORRECCIONES:
        pat = re.escape(error)
        texto = re.sub(pat, correccion, texto, flags=re.IGNORECASE)
    # Quitar palabras basura conocidas (Mh, Suto, FOP) y palabras cortas 1-3 letras que son errores OCR
    texto = _quitar_palabras_basura_cortas(texto)
    # Quitar tokens que son solo números (420342, 00201, "420342") para no ensuciar búsqueda BD/OFF
    texto = _quitar_tokens_solo_numeros(texto)
    texto = re.sub(r"\s+", " ", texto)
    # Quitar comillas sueltas al inicio/final que deja el OCR
    texto = texto.strip().strip("'\"").strip()
    # Si aparece bodega Pérez Pascuas + Crianza + Ribera/Duero pero no "Pedrosa", es casi seguro Viña Pedrosa
    t_low = texto.lower()
    if "pérez pascuas" in t_low and "crianza" in t_low and ("ribera" in t_low or "duero" in t_low) and "pedrosa" not in t_low:
        if t_low.startswith("odes "):
            texto = texto[5:].strip()
        texto = "Viña Pedrosa Crianza " + texto
    return texto.strip()
