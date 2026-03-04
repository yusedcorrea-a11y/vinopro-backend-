"""
Validación anti-tonterías para nombres, añada y grado alcohólico.
Evita datos falsos o de prueba en registro de vinos / bodega.
"""

PALABRAS_PROHIBIDAS = frozenset({
    "test", "prueba", "asdf", "xxx", "ñññ", "aaa",
    "qwerty", "123", "abc", "fake", "falso", "no", "nope",
})
ANIO_MIN = 1900
ANIO_MAX = 2026
ALCOHOL_MIN = 5
ALCOHOL_MAX = 25


def validar_nombre(nombre: str) -> tuple[bool, str]:
    """
    Mínimo 3 caracteres, no solo números, no palabras prohibidas.
    Convierte a minúsculas y hace trim antes de comparar.
    Devuelve (True, "") o (False, mensaje_error).
    """
    print(f"Validando nombre: '{nombre}'")
    if not nombre or not isinstance(nombre, str):
        return False, "Nombre vacío."
    t = (nombre or "").strip()
    lower = t.lower()
    if len(t) < 3:
        return False, "nombre_corto"
    if t.isdigit():
        return False, "nombre_solo_numeros"
    for p in PALABRAS_PROHIBIDAS:
        if p in lower or lower == p:
            return False, "nombre_prohibido"
    return True, ""


def validar_anio(anio: int | None) -> tuple[bool, str]:
    """Añada entre 1900 y 2026. None se considera válido (opcional)."""
    if anio is None:
        return True, ""
    try:
        a = int(anio)
        if ANIO_MIN <= a <= ANIO_MAX:
            return True, ""
        return False, "anio_invalido"
    except (TypeError, ValueError):
        return False, "anio_invalido"


def validar_alcohol(alcohol: float | int | None) -> tuple[bool, str]:
    """Grado alcohólico entre 5 y 25. None se considera válido (opcional)."""
    if alcohol is None:
        return True, ""
    try:
        a = float(alcohol)
        if ALCOHOL_MIN <= a <= ALCOHOL_MAX:
            return True, ""
        return False, "alcohol_invalido"
    except (TypeError, ValueError):
        return False, "alcohol_invalido"


def validar_vino_completo(
    nombre: str,
    bodega: str | None = None,
    anio: int | None = None,
    alcohol: float | int | None = None,
) -> tuple[bool, str]:
    """
    Valida nombre obligatorio; bodega, añada y alcohol opcionales.
    Devuelve (True, "") o (False, clave_mensaje para traducción).
    """
    ok, msg = validar_nombre(nombre)
    if not ok:
        return False, msg
    if bodega is not None and (bodega or "").strip():
        ok, msg = validar_nombre((bodega or "").strip())
        if not ok and msg == "nombre_corto":
            pass  # bodega puede ser corta, no exigimos 3 chars
        elif not ok:
            return False, msg
    ok, msg = validar_anio(anio)
    if not ok:
        return False, msg
    ok, msg = validar_alcohol(alcohol)
    if not ok:
        return False, msg
    return True, ""
