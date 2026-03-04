"""
Servicio de imágenes de vinos: ruta por clave o por tipo (tinto, blanco, rosado, espumoso, genérico).
"""
from pathlib import Path

STATIC_DIR = Path("static")
VINOS_IMAGES_DIR = STATIC_DIR / "images" / "vinos"


def get_imagen_vino(vino_key: str, tipo: str = "tinto") -> str:
    """
    Devuelve la URL de imagen del vino: específica por clave > por tipo > genérica.
    vino_key: clave del vino (ej. marques_de_riscal).
    tipo: tinto, blanco, rosado, espumoso (para fallback por tipo).
    """
    vino_key = (vino_key or "").strip()
    tipo = (tipo or "tinto").strip().lower()
    if tipo not in ("tinto", "blanco", "rosado", "espumoso"):
        tipo = "tinto"

    if vino_key:
        ruta_especifica = VINOS_IMAGES_DIR / f"{vino_key}.jpg"
        if ruta_especifica.exists():
            return f"/static/images/vinos/{vino_key}.jpg"

    ruta_tipo = VINOS_IMAGES_DIR / f"{tipo}.jpg"
    if ruta_tipo.exists():
        return f"/static/images/vinos/{tipo}.jpg"

    return "/static/images/vinos/generico.jpg"
