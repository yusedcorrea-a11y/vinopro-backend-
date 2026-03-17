"""
Persistencia de vinos aprendidos: cuando Gemini encuentra un vino en la nube
que no estaba en la base local, se guarda aquí para futuras respuestas offline.
Archivo: data/vinos_aprendidos.json (se carga con el resto del catálogo al iniciar).
"""
import json
import os
import re

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
VINOS_APRENDIDOS_PATH = os.path.join(DATA_FOLDER, "vinos_aprendidos.json")


def _slug(s: str) -> str:
    if not s or not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = re.sub(r"[áàäâ]", "a", s)
    s = re.sub(r"[éèëê]", "e", s)
    s = re.sub(r"[íìïî]", "i", s)
    s = re.sub(r"[óòöô]", "o", s)
    s = re.sub(r"[úùüû]", "u", s)
    s = s.replace("ñ", "n")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80]


def _anada_normalizada(vino: dict) -> str:
    """Añada (año de cosecha) como string de 4 dígitos o vacío."""
    anada = vino.get("anada") or vino.get("añada") or vino.get("cosecha")
    if anada is None:
        return ""
    s = str(anada).strip()
    if not s:
        return ""
    digits = "".join(c for c in s if c.isdigit())
    if len(digits) >= 4:
        return digits[:4]
    if len(digits) == 2:
        return "20" + digits if int(digits) < 50 else "19" + digits
    return digits if digits else ""


def _key_from_vino(vino: dict) -> str:
    nombre = (vino.get("nombre") or "").strip() or "vino"
    bodega = (vino.get("bodega") or "").strip()
    anada = _anada_normalizada(vino)
    base = _slug(nombre)
    if bodega:
        base += "-" + _slug(bodega)[:40]
    if anada:
        base += "-" + anada
    return base or "vino-aprendido"


def _normalizar_para_guardar(vino: dict) -> dict:
    """Normaliza el vino devuelto por Gemini antes de guardar: tipo, añada, longitudes máximas."""
    if not vino or not isinstance(vino, dict):
        return vino
    tipo = (vino.get("tipo") or "tinto").strip().lower()
    if tipo not in ("tinto", "blanco", "rosado", "espumoso", "dulce"):
        tipo = "tinto"
    out = {}
    for k, v in vino.items():
        if v is None or v == "":
            continue
        if k in ("anada", "añada", "cosecha"):
            anada = _anada_normalizada(vino)
            if anada:
                out["anada"] = anada
            continue
        if isinstance(v, str):
            v = v.strip()
            if k in ("descripcion", "notas_cata", "maridaje") and len(v) > 500:
                v = v[:500]
            elif k in ("nombre", "bodega", "region", "pais") and len(v) > 150:
                v = v[:150]
        out[k] = v
    out["tipo"] = tipo
    return out


def _buscar_duplicado_aprendidos(data: dict, nombre: str, bodega: str, anada: str = "") -> str | None:
    """Devuelve la key si ya existe un vino con el mismo nombre, bodega y añada (normalizados)."""
    n = _slug(nombre)
    b = _slug(bodega)
    for key, v in data.items():
        if not isinstance(v, dict):
            continue
        vn = _slug(v.get("nombre") or "")
        vb = _slug(v.get("bodega") or "")
        va = _anada_normalizada(v)
        if n == vn and b == vb and (anada == va or (not anada and not va)):
            return key
    return None


def _load_aprendidos() -> dict:
    if not os.path.exists(VINOS_APRENDIDOS_PATH):
        return {}
    try:
        with open(VINOS_APRENDIDOS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_aprendidos(data: dict) -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(VINOS_APRENDIDOS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def guardar_vino_aprendido(vino: dict) -> str | None:
    """
    Guarda un vino (encontrado por Gemini en la nube) en data/vinos_aprendidos.json.
    Normaliza campos, evita duplicados (mismo nombre+bodega) y genera key única. Devuelve la key asignada o None si falla.
    """
    if not vino or not isinstance(vino, dict):
        return None
    vino = _normalizar_para_guardar(vino)
    nombre = (vino.get("nombre") or "").strip()
    if not nombre:
        return None
    data = _load_aprendidos()
    bodega = (vino.get("bodega") or "").strip()
    anada = _anada_normalizada(vino)
    # Evitar duplicado: si ya existe mismo nombre+bodega+añada, actualizar esa entrada
    key_existente = _buscar_duplicado_aprendidos(data, nombre, bodega, anada)
    if key_existente:
        update = {k: v for k, v in vino.items() if v is not None and v != ""}
        if anada:
            update["anada"] = anada
        data[key_existente].update(update)
        try:
            _save_aprendidos(data)
            return key_existente
        except Exception:
            return None
    key = _key_from_vino(vino)
    if key in data:
        data[key].update({k: v for k, v in vino.items() if v is not None and v != ""})
    else:
        precio = vino.get("precio_estimado")
        if precio is not None and precio != "":
            precio_str = str(precio).strip() if isinstance(precio, str) else str(precio)
        else:
            precio_str = ""
        entry = {
            "nombre": nombre,
            "bodega": bodega,
            "tipo": (vino.get("tipo") or "tinto").strip().lower(),
            "region": (vino.get("region") or "").strip(),
            "pais": (vino.get("pais") or "").strip(),
            "maridaje": (vino.get("maridaje") or "").strip(),
            "descripcion": (vino.get("descripcion") or "").strip(),
            "notas_cata": (vino.get("notas_cata") or "").strip(),
            "precio_estimado": precio_str,
        }
        if anada:
            entry["anada"] = anada
        entry = {k: v for k, v in entry.items() if v is not None and v != ""}
        data[key] = entry
    try:
        _save_aprendidos(data)
        return key
    except Exception:
        return None


def merge_aprendidos_en_vinos(vinos_mundiales: dict) -> dict:
    """Mezcla vinos_aprendidos.json en el diccionario de vinos (in-place). Devuelve el mismo dict."""
    aprendidos = _load_aprendidos()
    for k, v in aprendidos.items():
        if k and isinstance(v, dict) and v.get("nombre"):
            vinos_mundiales[k] = v
    return vinos_mundiales
