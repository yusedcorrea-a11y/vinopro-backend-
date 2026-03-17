#!/usr/bin/env python3
r"""
Convierte un video a MP4 estandar (H.264 + AAC) para que se reproduzca
en cualquier reproductor (Windows, Android, Google Play, navegadores).

Uso:
  python scripts/convertir_video_universal.py
  python scripts/convertir_video_universal.py ruta/al/video.mp4

Si no tienes ffmpeg: winget install ffmpeg
"""
import os
import sys
import subprocess
import shutil

def find_ffmpeg():
    return shutil.which("ffmpeg")

def convert_to_universal_mp4(input_path: str, output_path: str = None) -> bool:
    if not os.path.isfile(input_path):
        print(f"Error: no se encuentra el archivo: {input_path}")
        return False
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_universal.mp4"
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("No se encontró ffmpeg en el sistema.")
        print("Instálalo con: winget install ffmpeg")
        print("O descarga desde: https://ffmpeg.org/download.html")
        return False
    # H.264 video + AAC audio = compatible con todo (Windows, Android, Google, navegadores)
    cmd = [
        ffmpeg,
        "-y",  # sobrescribir sin preguntar
        "-i", input_path,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.0",
        "-pix_fmt", "yuv420p",  # mejor compatibilidad
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",  # empieza a reproducir antes de descargar todo
        output_path,
    ]
    print(f"Convirtiendo: {input_path}")
    print(f"Salida:       {output_path}")
    try:
        subprocess.run(cmd, check=True)
        print("Listo. Ya puedes usar el archivo *_universal.mp4 en cualquier sitio.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error en la conversión: {e}")
        return False

def main():
    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        # Buscar un MP4 en la carpeta del script o en la raíz del proyecto
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        parent_root = os.path.dirname(project_root)
        candidates = [
            os.path.join(project_root, "vino_pro_reel_final.mp4"),
            os.path.join(parent_root, "vino_pro_reel_final.mp4"),
            os.path.join(project_root, "video_promocional.mp4"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                input_path = c
                break
        else:
            print("Uso: python convertir_video_universal.py <ruta_al_video.mp4>")
            print("Ejemplo: python convertir_video_universal.py vino_pro_reel_final.mp4")
            sys.exit(1)
    convert_to_universal_mp4(input_path)
    sys.exit(0 if find_ffmpeg() else 1)

if __name__ == "__main__":
    main()
