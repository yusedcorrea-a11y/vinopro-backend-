# Cómo hacer que el vídeo se vea en cualquier sitio

Si el vídeo solo se reproduce en Cursor y no en el reproductor de Windows, el móvil o Google, suele ser por el **formato o codec**. La solución es tener una copia en **MP4 estándar (H.264 + AAC)**.

---

## Opción 1: Script de conversión (recomendado si tienes el archivo)

1. **Instala ffmpeg** (solo una vez):
   ```bash
   winget install ffmpeg
   ```
   O descarga desde: https://ffmpeg.org/download.html (añade `ffmpeg` al PATH).

2. **Pon tu vídeo** en una carpeta que conozcas (por ejemplo `backend_optimized` o Escritorio) y anota la ruta completa.

3. **Ejecuta el script** desde la carpeta del proyecto:
   ```bash
   cd c:\Users\yused\Documents\VINO_PRO_FINAL\backend_optimized
   python scripts/convertir_video_universal.py "ruta\completa\a\tu_video.mp4"
   ```
   Ejemplo si el vídeo está en el Escritorio:
   ```bash
   python scripts/convertir_video_universal.py "C:\Users\yused\Desktop\mi_reel.mp4"
   ```

4. Se generará un archivo nuevo: **`tu_video_universal.mp4`** en la misma carpeta. Ese es el que debes usar para subir a Google, WhatsApp, etc.

---

## Opción 2: Re-exportar desde CapCut (sin instalar nada más)

Si el vídeo lo has editado en CapCut:

1. Abre el proyecto en **CapCut**.
2. Pulsa **Exportar** / **Export**.
3. En **Formato** o **Codec**, elige **MP4** y, si aparece, **H.264** (no solo HEVC/H.265).
4. Resolución: la que quieras (ej. 1080×1920 para vertical).
5. Exporta y guarda el archivo.

Ese MP4 exportado desde CapCut suele reproducirse en cualquier sitio.

---

## Opción 3: Convertir online (sin instalar programas)

Sube el vídeo a un conversor online que genere **MP4 H.264**, por ejemplo:

- https://cloudconvert.com/mp4-converter  
- https://www.freeconvert.com/video-converter  

Descarga el MP4 resultante y úsalo para Google Play, redes, etc.

---

## Resumen

| Dónde quieres ver el vídeo | Qué hacer |
|----------------------------|-----------|
| Windows (Reproductor, VLC) | Usar el archivo `*_universal.mp4` o exportar desde CapCut como MP4 H.264. |
| Google Play (anuncios) | Mismo MP4 H.264; mínimo 10 s, formatos 16:9, 1:1 y 9:16. |
| Móvil / WhatsApp | Mismo MP4. |

El script está en: **`scripts/convertir_video_universal.py`**. Solo necesitas tener **ffmpeg** instalado y pasarle la ruta de tu vídeo.
