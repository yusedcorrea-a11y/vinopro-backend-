#!/usr/bin/env python3
"""
Genera el Reel promocional de Vino Pro IA (15 s, vertical 9:16) para Instagram/TikTok.
Escenas: escaneo -> info vino -> sumiller IA -> compra/guías -> logo + CTA.
Requiere: pip install moviepy pillow
Uso: python scripts/generar_reel_vino_pro.py [--output vino_pro_ia_reel.mp4] [--sin-musica]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Colores marca (desde style.css)
BURDEOS = (107, 45, 60)       # #6b2d3c
BURDEOS_OSCURO = (74, 31, 42) # #4a1f2a
DORADO = (184, 134, 11)       # #b8860b
CREMA = (250, 248, 245)        # #faf8f5
NEGRO = (26, 21, 18)          # #1a1512
BLANCO = (255, 255, 255)

W, H = 1080, 1920
FPS = 30
DURACION_ESCENA = 3.0
# Texto principal por escena (cada escena es COMPLETAMENTE DIFERENTE)
ESCENAS = [
    {"titulo": "¿Vino sin información?", "subtitulo": "Escanea la etiqueta"},
    {"titulo": "Descubre todo sobre tu vino", "subtitulo": "Nombre, bodega, puntuación y precio"},
    {"titulo": "Pregunta a nuestro sumiller IA", "subtitulo": "¿Qué vino para carne?"},
    {"titulo": "Compra online o descubre dónde tomarlo", "subtitulo": "Guías en más de 30 países"},
    {"titulo": "Vino Pro IA", "subtitulo": "Tu sommelier personal"},
]

# Subtítulos para redes (legibles sin sonido): blanco + borde negro, barra semitransparente
SUBTITULOS_ES = [
    ["¿Vino sin información? Escanea la etiqueta"],
    ["Descubre nombre, bodega, puntuación y precio"],
    ["Pregunta a nuestro sumiller IA", "¿Qué vino para carne?"],
    ["Compra online o descubre dónde tomarlo", "Guías en más de 30 países"],
    ["Vino Pro IA · Tu sommelier personal", "Descárgala ya (enlace en bio)"],
]
SUBTITULOS_EN = [
    ["Wine with no info? Scan the label"],
    ["Discover name, winery, rating and price"],
    ["Ask our AI sommelier", "What wine for steak?"],
    ["Buy online or find where to drink it", "Guides in 30+ countries"],
    ["Vino Pro IA · Your personal sommelier", "Download now (link in bio)"],
]


def get_font():
    """Ruta a una fuente disponible (Windows / Linux / macOS)."""
    candidatos = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ]
    for p in candidatos:
        if p.exists():
            return str(p)
    return None


def _draw_text_con_borde(draw, x: int, y: int, texto: str, font, fill=BLANCO, borde=NEGRO, grosor=3):
    """Dibuja texto con borde negro para máximo contraste (subtítulos)."""
    for dx in range(-grosor, grosor + 1):
        for dy in range(-grosor, grosor + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), texto, font=font, fill=borde)
    draw.text((x, y), texto, font=font, fill=fill)


def _centrar_texto(draw, texto, font, y, fill=BLANCO, borde=NEGRO):
    try:
        bbox = draw.textbbox((0, 0), texto, font=font)
    except AttributeError:
        sz = draw.textsize(texto, font=font)
        bbox = (0, 0, sz[0], sz[1])
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if borde:
        for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2)]:
            draw.text((x+dx, y+dy), texto, font=font, fill=borde)
    draw.text((x, y), texto, font=font, fill=fill)
    return y + (bbox[3] - bbox[1]) + 10


def crear_imagen_escena(escena: dict, indice: int, idioma: str = "es") -> "Image.Image":
    """Genera 5 escenas TOTALMENTE DIFERENTES: escaneo, info vino, sumiller, compra/guías, logo+CTA."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("ERROR: pip install pillow")
        sys.exit(1)

    img = Image.new("RGB", (W, H), color=BURDEOS_OSCURO)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H], fill=BURDEOS_OSCURO)

    font_path = get_font()
    font_titulo = ImageFont.truetype(font_path, 64) if font_path else ImageFont.load_default()
    font_sub = ImageFont.truetype(font_path, 32) if font_path else ImageFont.load_default()
    font_peq = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    font_subtitulo = ImageFont.truetype(font_path, 52) if font_path else ImageFont.load_default()
    font_subtitulo2 = ImageFont.truetype(font_path, 42) if font_path else ImageFont.load_default()
    font_logo = ImageFont.truetype(font_path, 88) if font_path else ImageFont.load_default()

    titulo = escena["titulo"]

    # ----- ESCENA 1: Escaneo de etiqueta (móvil + botella + icono cámara) -----
    if indice == 0:
        # Marco de móvil (vertical)
        px, py = W//2 - 140, 280
        draw.rounded_rectangle([px, py, px + 280, py + 520], radius=28, outline=DORADO, width=5)
        # Pantalla interior (oscura) + línea de escaneo
        draw.rounded_rectangle([px+12, py+12, px+268, py+508], radius=20, fill=NEGRO, outline=BURDEOS)
        for i in range(0, 400, 12):
            draw.line([(px+40, py+120+i), (px+240, py+120+i)], fill=DORADO, width=2)
        # Silueta botella (rectángulo + cuello)
        bx, by = W//2 + 120, 400
        draw.rectangle([bx-35, by+80, bx+35, by+280], fill=(60, 40, 45))
        draw.rectangle([bx-18, by, bx+18, by+90], fill=(60, 40, 45))
        # Icono cámara (círculo)
        draw.ellipse([W//2 - 45, 920, W//2 + 45, 1010], outline=DORADO, width=4)
        draw.ellipse([W//2 - 25, 940, W//2 + 25, 990], fill=DORADO)
        # Texto principal
        _centrar_texto(draw, titulo, font_titulo, 1080, fill=BLANCO, borde=NEGRO)

    # ----- ESCENA 2: Información del vino (mock pantalla app: nombre, bodega, estrellas, precio) -----
    elif indice == 1:
        # Card tipo app (glass)
        cx, cy = W//2 - 260, 320
        draw.rounded_rectangle([cx, cy, cx + 520, cy + 580], radius=24, fill=(40, 28, 32), outline=DORADO, width=3)
        # Líneas de datos
        draw.text((cx + 40, cy + 50), "Vega Sicilia Único", font=font_titulo, fill=CREMA)
        draw.text((cx + 40, cy + 130), "Bodega Vega Sicilia · Ribera del Duero", font=font_peq, fill=DORADO)
        # Estrellas
        draw.text((cx + 40, cy + 200), "★★★★★ 98 pts", font=font_sub, fill=DORADO)
        draw.text((cx + 40, cy + 260), "350-400 €", font=font_titulo, fill=BLANCO)
        draw.text((cx + 40, cy + 340), "Fruta madura, cuero, especias.", font=font_peq, fill=CREMA)
        # Texto principal arriba
        _centrar_texto(draw, titulo, font_sub, 180, fill=BLANCO, borde=NEGRO)

    # ----- ESCENA 3: Sumiller IA (chat + bocadillo + icono voz) -----
    elif indice == 2:
        # Bocadillo de diálogo (usuario)
        bubble = [W//2 - 320, 700, W//2 + 320, 880]
        draw.rounded_rectangle(bubble, radius=24, fill=(50, 35, 40), outline=DORADO, width=3)
        _centrar_texto(draw, "¿Qué vino para carne?", font_titulo, 750, fill=BLANCO, borde=None)
        # Pequeña cola del bocadillo
        draw.polygon([(W//2 - 20, 878), (W//2 + 20, 878), (W//2, 920)], fill=(50, 35, 40), outline=DORADO)
        # Icono de voz/chat (círculo + onda)
        draw.ellipse([W//2 - 50, 420, W//2 + 50, 520], outline=DORADO, width=4)
        draw.ellipse([W//2 - 28, 445, W//2 + 28, 501], fill=DORADO)
        draw.ellipse([W//2 - 80, 380, W//2 + 80, 560], outline=DORADO, width=2)
        # Texto principal
        _centrar_texto(draw, titulo, font_titulo, 220, fill=BLANCO, borde=NEGRO)

    # ----- ESCENA 4: Compra y guías (bloque Comprar + bloque Dónde tomarlo + banderas) -----
    elif indice == 3:
        # Bloque "Comprar" (card)
        draw.rounded_rectangle([120, 320, W - 120, 520], radius=20, fill=(40, 28, 32), outline=DORADO, width=2)
        draw.text((W//2 - 180, 380), "Comprar", font=font_titulo, fill=CREMA)
        # Icono carrito (rectángulo + ruedas)
        car_x, car_y = W//2 + 175, 368
        draw.rounded_rectangle([car_x, car_y, car_x + 75, car_y + 55], radius=6, outline=DORADO, width=2)
        draw.ellipse([car_x + 8, car_y + 42, car_x + 28, car_y + 62], outline=DORADO, width=2)
        draw.ellipse([car_x + 47, car_y + 42, car_x + 67, car_y + 62], outline=DORADO, width=2)
        # Bloque "¿Dónde tomarlo?"
        draw.rounded_rectangle([120, 580, W - 120, 780], radius=20, fill=(40, 28, 32), outline=DORADO, width=2)
        draw.text((W//2 - 220, 620), "¿Dónde tomarlo?", font=font_titulo, fill=CREMA)
        draw.text((W//2 - 200, 700), "ES  IT  FR  AR  ...", font=font_sub, fill=DORADO)
        # Texto principal
        _centrar_texto(draw, titulo, font_sub, 180, fill=BLANCO, borde=NEGRO)

    # ----- ESCENA 5: Cierre y CTA (logo grande + Tu sommelier + botón Descargar) -----
    else:
        _centrar_texto(draw, "Vino Pro IA", font_logo, 680, fill=BLANCO, borde=NEGRO)
        _centrar_texto(draw, "Tu sommelier personal", font_titulo, 820, fill=DORADO, borde=None)
        # Botón ficticio "Descargar"
        btn_y = 1050
        draw.rounded_rectangle([W//2 - 200, btn_y, W//2 + 200, btn_y + 90], radius=16, fill=DORADO, outline=CREMA, width=2)
        draw.text((W//2 - 85, btn_y + 28), "Descargar", font=font_titulo, fill=NEGRO)

    # --- Barra de subtítulos (parte inferior): fondo semitransparente + texto blanco con borde negro ---
    lineas_sub = SUBTITULOS_EN[indice] if idioma == "en" else SUBTITULOS_ES[indice]
    barra_h = 220
    barra_y = H - barra_h - 80
    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, barra_h), (0, 0, 0, 180))
    img_rgba.paste(overlay, (0, barra_y), overlay.split()[3])
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    y_linea = barra_y + 40
    for i, linea in enumerate(lineas_sub):
        f = font_subtitulo if i == 0 else font_subtitulo2
        try:
            bbox_s = draw.textbbox((0, 0), linea, font=f)
        except AttributeError:
            sz = draw.textsize(linea, font=f)
            bbox_s = (0, 0, sz[0], sz[1])
        tw_s = bbox_s[2] - bbox_s[0]
        x_s = (W - tw_s) // 2
        _draw_text_con_borde(draw, x_s, y_linea, linea, f, fill=BLANCO, borde=NEGRO, grosor=3)
        y_linea += 58

    return img


def _añadir_barra_subtitulos(img: "Image.Image", indice: int, idioma: str):
    """Añade la barra de subtítulos (fondo negro semitransparente + texto) a cualquier imagen PIL."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return img
    draw = ImageDraw.Draw(img)
    font_path = get_font()
    font_subtitulo = ImageFont.truetype(font_path, 52) if font_path else ImageFont.load_default()
    font_subtitulo2 = ImageFont.truetype(font_path, 42) if font_path else ImageFont.load_default()
    lineas_sub = SUBTITULOS_EN[indice] if idioma == "en" else SUBTITULOS_ES[indice]
    barra_h = 220
    barra_y = H - barra_h - 80
    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, barra_h), (0, 0, 0, 180))
    img_rgba.paste(overlay, (0, barra_y), overlay.split()[3])
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)
    y_linea = barra_y + 40
    for i, linea in enumerate(lineas_sub):
        f = font_subtitulo if i == 0 else font_subtitulo2
        try:
            bbox_s = draw.textbbox((0, 0), linea, font=f)
        except AttributeError:
            sz = draw.textsize(linea, font=f)
            bbox_s = (0, 0, sz[0], sz[1])
        tw_s = bbox_s[2] - bbox_s[0]
        x_s = (W - tw_s) // 2
        _draw_text_con_borde(draw, x_s, y_linea, linea, f, fill=BLANCO, borde=NEGRO, grosor=3)
        y_linea += 58
    return img


def _redimensionar_9_16(im: "Image.Image") -> "Image.Image":
    """Recorta/redimensiona a 1080x1920 (9:16) centrado."""
    try:
        from PIL import Image
    except ImportError:
        return im
    w, h = im.size
    target_r = W / H
    r = w / h
    if r > target_r:
        new_h = h
        new_w = int(h * target_r)
    else:
        new_w = w
        new_h = int(w / target_r)
    im = im.resize((new_w, new_h), getattr(Image, "Resampling", Image).LANCZOS)
    left = (new_w - W) // 2
    top = (new_h - H) // 2
    return im.crop((left, top, left + W, top + H))


def cargar_escena_desde_foto(carpeta: Path, indice: int, idioma: str) -> "Image.Image":
    """Carga la foto de la escena (1..5), redimensiona a 9:16 y añade subtítulos."""
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: pip install pillow")
        sys.exit(1)
    # Nombres posibles: escena_1.jpg, 1.jpg, 1.png, reel_1.jpg, img_1.png
    i = indice + 1
    nombres = [f"escena_{i}.jpg", f"escena_{i}.png", f"{i}.jpg", f"{i}.png", f"reel_{i}.jpg", f"reel_{i}.png", f"img_{i}.jpg", f"img_{i}.png"]
    for nombre in nombres:
        p = carpeta / nombre
        if p.exists():
            im = Image.open(p).convert("RGB")
            im = _redimensionar_9_16(im)
            return _añadir_barra_subtitulos(im, indice, idioma)
    raise FileNotFoundError(f"No se encontró imagen para escena {i} en {carpeta}. Prueba: escena_{i}.jpg o {i}.jpg")


def main():
    parser = argparse.ArgumentParser(description="Genera Reel Vino Pro IA (15s, 9:16) con subtítulos")
    parser.add_argument("--output", type=str, default="", help="Archivo MP4 de salida (por defecto: subtitulado ES o EN)")
    parser.add_argument("--idioma", type=str, default="es", choices=["es", "en", "ambos"], help="Subtítulos: es, en, o ambos (genera 2 archivos)")
    parser.add_argument("--solo-imagenes", action="store_true", help="Solo guardar imágenes de cada escena (PNG)")
    parser.add_argument("--imagenes-dir", type=str, default="", help="Carpeta con 5 fotos (escena_1.jpg ... escena_5.jpg). Genera video con tus fotos + subtítulos.")
    args = parser.parse_args()

    idiomas = ["es", "en"] if args.idioma == "ambos" else [args.idioma]
    base_dir = (ROOT / args.output).parent if args.output else ROOT
    base_dir.mkdir(parents=True, exist_ok=True)
    usar_fotos = args.imagenes_dir.strip()
    if usar_fotos:
        carpeta_fotos = Path(usar_fotos)
        if not carpeta_fotos.is_dir():
            print(f"ERROR: La carpeta no existe: {carpeta_fotos}")
            sys.exit(1)

    for idioma in idiomas:
        suf = "_es" if idioma == "es" else "_en"
        if args.solo_imagenes:
            for i, escena in enumerate(ESCENAS):
                if usar_fotos:
                    img = cargar_escena_desde_foto(carpeta_fotos, i, idioma)
                else:
                    img = crear_imagen_escena(escena, i, idioma=idioma)
                p = base_dir / f"reel_escena_{i+1}{suf}.png"
                img.save(p)
            print(f"Imagenes ({idioma}) guardadas en {base_dir}")
            continue

        try:
            from moviepy import ImageClip, concatenate_videoclips
        except ImportError:
            try:
                from moviepy.editor import ImageClip, concatenate_videoclips
            except ImportError:
                print("ERROR: pip install moviepy")
                sys.exit(1)
        import numpy as np

        print("Generando 5 escenas...")
        clips = []
        for i, escena in enumerate(ESCENAS):
            print(f"  Escena {i+1}/5...")
            if usar_fotos:
                img = cargar_escena_desde_foto(carpeta_fotos, i, idioma)
            else:
                img = crear_imagen_escena(escena, i, idioma=idioma)
            arr = np.array(img)
            clip = ImageClip(arr).with_duration(DURACION_ESCENA)
            clips.append(clip)
        print("Uniendo escenas...")
        clip = concatenate_videoclips(clips, method="compose")

        if args.output and len(idiomas) == 1:
            out_file = args.output
        else:
            nombre = f"vino_pro_ia_reel_subtitulado{suf}.mp4"
            out_file = str(base_dir / nombre)
        print("Escribiendo video (puede tardar 1-2 min)...")
        clip.write_videofile(
            out_file,
            fps=FPS,
            codec="libx264",
            audio=False,
            preset="medium",
            threads=4,
            logger=None,
        )
        print(f"OK: Reel ({idioma}) guardado en {out_file}")
        print("   Duracion: 15 s | Formato: 1080x1920 (9:16) | Subtitulos integrados.")


if __name__ == "__main__":
    main()
