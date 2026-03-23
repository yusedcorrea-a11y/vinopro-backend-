"""
Recorta las PNG de la nueva mascota (quita texto inferior derecho) y guarda en static/images/mascota/.
Ejecutar desde la raíz del repo: python scripts/prepare_mascota_zorro.py
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "static" / "images" / "mascota"

# Origen: assets de Cursor (misma composición 1024x1024, texto abajo-derecha)
ASSETS_DIR = Path(
    os.environ.get(
        "MASCOTA_SOURCE_DIR",
        str(
            Path.home()
            / ".cursor"
            / "projects"
            / "c-Users-yused-Documents-VINO-PRO-FINAL-backend-optimized"
            / "assets"
        ),
    )
)

SOURCES_ORDERED = [
    "c__Users_yused_AppData_Roaming_Cursor_User_workspaceStorage_b5087e1e5aaab2e1aea91bfe205d3863_images_nueva_mascota-df8dd34f-c309-45e7-aeae-ffbea1b9cabd.png",
    "c__Users_yused_AppData_Roaming_Cursor_User_workspaceStorage_b5087e1e5aaab2e1aea91bfe205d3863_images_nueva_mascota_2-826b37b1-8d4b-4afc-894f-efc21b47b038.png",
    "c__Users_yused_AppData_Roaming_Cursor_User_workspaceStorage_b5087e1e5aaab2e1aea91bfe205d3863_images_nueva_mascota_3-37aea2c0-05e1-4191-87e1-7d6080c855ed.png",
    "c__Users_yused_AppData_Roaming_Cursor_User_workspaceStorage_b5087e1e5aaab2e1aea91bfe205d3863_images_nueva_mascota_4-2dbfc51c-636f-44f7-b1f3-81edcd4c9935.png",
]


def crop_no_logo(im: Image.Image) -> Image.Image:
    """Elimina la zona típica del rótulo 'Zorrito / VINO PRO' (abajo-derecha)."""
    w, h = im.size
    # Recorte conservador: quitar ~14% derecha y ~10% abajo (1024px)
    new_w = int(w * 0.86)
    new_h = int(h * 0.90)
    return im.crop((0, 0, new_w, new_h))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(SOURCES_ORDERED, start=1):
        src = ASSETS_DIR / name
        if not src.is_file():
            print(f"Falta archivo: {src}")
            print("Copia las 4 PNG a esa carpeta o define MASCOTA_SOURCE_DIR.")
            raise SystemExit(1)
        im = Image.open(src).convert("RGBA")
        out = crop_no_logo(im)
        dest = OUT_DIR / f"mascota-{i}.png"
        out.save(dest, optimize=True)
        print(f"OK {dest} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
