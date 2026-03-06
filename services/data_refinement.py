"""
Refinamiento y normalización de datos extraídos de etiquetas (OCR o IA).
Corrige errores típicos: 2O22 -> 2022, espacios, caracteres confusos.
"""
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Estructura estándar de entidades (siempre la misma)
ESQUEMA_ENTIDADES = {
    "bodega": None,
    "nombre": None,
    "añada": None,
    "denominacion_origen": None,
    "variedad": None,
}


def refinar_texto_ocr(texto: str) -> str:
    """
    Limpia errores típicos de OCR en texto de etiquetas.
    - 2O22, 2o21 -> 2022, 2021 (O/o/l confundidos con 0)
    - Espacios múltiples, saltos de línea
    - Caracteres raros
    """
    if not texto or not isinstance(texto, str):
        return ""
    t = texto.strip()
    if not t:
        return ""
    # Años: 2O22, 2o21, 2l22 -> 2022, 2021, 2022 (O/o/l confundidos con 0)
    t = re.sub(r"\b(19|20)([OoIl])(\d{2})\b", r"\g<1>0\g<3>", t)
    t = re.sub(r"\b(19|20)(\d)([OoIl])(\d)\b", r"\g<1>\g<2>0\g<4>", t)
    t = re.sub(r"\b(2)([OoIl])(\d{2})\b", r"20\g<3>", t)  # 2O21 -> 2021
    # Espacios y saltos
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    return t


def refinar_año(valor: Any) -> int | None:
    """Normaliza año: acepta int, str con 2O22, etc."""
    if valor is None:
        return None
    if isinstance(valor, int) and 1900 <= valor <= 2030:
        return valor
    if isinstance(valor, str):
        s = re.sub(r"[OoIl]", "0", valor)
        s = re.sub(r"\D", "", s)
        if len(s) == 4:
            anio = int(s)
            if 1900 <= anio <= 2030:
                return anio
    return None


def normalizar_entidades(entidades: dict) -> dict:
    """
    Asegura que las entidades tengan la estructura estándar.
    Todos los campos presentes, null si no hay valor.
    """
    out = dict(ESQUEMA_ENTIDADES)
    for k in out:
        v = entidades.get(k)
        if v is None or v == "":
            continue
        if k == "añada":
            out[k] = refinar_año(v)
        else:
            if isinstance(v, str) and v.strip():
                s = v.strip()
                if k in ("bodega", "nombre"):
                    out[k] = s[:200]
                elif k == "denominacion_origen":
                    out[k] = s[:150]
                elif k == "variedad":
                    out[k] = s[:80]
    return out


def entidades_para_json(entidades: dict) -> dict:
    """Devuelve solo campos no nulos para la respuesta JSON."""
    norm = normalizar_entidades(entidades)
    return {k: v for k, v in norm.items() if v is not None}
