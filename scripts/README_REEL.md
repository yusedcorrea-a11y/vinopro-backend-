# Reel promocional Vino Pro IA

Video vertical 15 s (9:16) para Instagram Reels y TikTok, **con subtítulos integrados** (efectivo sin sonido).

## Requisitos

```bash
pip install moviepy pillow
```

(En Windows, si `moviepy` falla al escribir el MP4, instala **ffmpeg** y añádelo al PATH.)

## Uso

```bash
# Reel subtitulado en español (por defecto)
python scripts/generar_reel_vino_pro.py
# -> vino_pro_ia_reel_subtitulado_es.mp4

# Reel subtitulado en inglés
python scripts/generar_reel_vino_pro.py --idioma en
# -> vino_pro_ia_reel_subtitulado_en.mp4

# Ambos idiomas (2 MP4)
python scripts/generar_reel_vino_pro.py --idioma ambos

# Solo imágenes PNG por escena (con subtítulos)
python scripts/generar_reel_vino_pro.py --solo-imagenes --idioma es
# -> reel_escena_1_es.png ... reel_escena_5_es.png
python scripts/generar_reel_vino_pro.py --solo-imagenes --idioma en
# -> reel_escena_1_en.png ... reel_escena_5_en.png
```

## Formato de subtítulos

- **Tamaño:** Grande (52 px línea principal), legible en móvil.
- **Color:** Blanco con borde negro (máximo contraste).
- **Posición:** Barra fija en la parte inferior.
- **Fondo:** Barra semitransparente negra para legibilidad.

## Escenas (3 s cada una)

1. **¿Vino sin información?** – Escanea la etiqueta  
2. **Escanea y descubre todo** – Nombre, bodega, puntuación, precio  
3. **Pregunta a nuestro sumiller IA** – ¿Qué vino para carne?  
4. **Recomendaciones, compra y guías** – Comprar · Dónde tomarlo (ES IT FR AR)  
5. **Vino Pro IA · Tu sommelier personal** – CTA “Descargar ya”

## Búsquedas para imágenes reales (stock / IA)

Para un reel con fotos de personas (Unsplash, Pexels, Pixabay o generadores IA):

| Escena | Términos de búsqueda |
|--------|----------------------|
| **1 – Viñedo** | `wine vineyard sunset couple toasting`, `romantic wine tasting sunset`, `wine vineyard sunrise couple`, `couple toasting wine morning vineyard` |
| **2 – Escaneo** | `woman scanning wine bottle with phone`, `girl using phone wine shop`, `woman scanning wine bottle smartphone`, `woman phone scanning wine label` |
| **3 – Sumiller IA** | `man talking on phone wine tasting`, `man smiling using smartphone wine bar`, `man talking to phone smiling`, `person asking phone recommendation` |
| **4 – Compra/guías** | `world map with flags wine regions`, `wine countries map flags`, `hand holding phone map travel`, `smartphone app world map` |
| **5 – Cierre** | `couple toasting wine glasses sunset`, `romantic wine toast golden hour`, `couple toasting wine sunset`, `wine toast golden hour couple` |

Filtrar por **vertical (9:16)** y **alta resolución** para 1080×1920.

## Publicar con tus fotos (imágenes reales)

1. **Descarga 5 fotos** (una por escena) de Unsplash/Pexels/Pixabay con los términos de la tabla.
2. **Guárdalas en una carpeta** con estos nombres (cualquiera de los formatos vale):
   - `escena_1.jpg`, `escena_2.jpg`, … `escena_5.jpg`  
   - o `1.jpg`, `2.jpg`, … `5.jpg`  
   - o `reel_1.png`, … `reel_5.png`
3. **Genera el video** (el script recorta a 9:16 y añade la barra de subtítulos):

   ```bash
   python scripts/generar_reel_vino_pro.py --imagenes-dir "ruta/a/tu/carpeta" --output vino_pro_reel_final.mp4 --idioma es
   ```

4. **Opcional:** Ver las 5 imágenes con subtítulos antes de hacer el video:

   ```bash
   python scripts/generar_reel_vino_pro.py --imagenes-dir "ruta/a/tu/carpeta" --solo-imagenes --idioma es
   ```
   Se guardan `reel_escena_1_es.png` … `reel_escena_5_es.png` en la raíz del proyecto.

5. **Subir a redes:** El MP4 es 1080×1920, 15 s, listo para Instagram Reels y TikTok. Opcional: añade música en CapCut o DaVinci antes de subir.

## Mejorar el reel

- **Música:** Añade una pista (electrónica suave / lo-fi) en CapCut, DaVinci o similar.  
- **Grabación real:** Sustituye las escenas por vídeo real: escaneo con móvil, app en pantalla, sumiller por voz.  
- **Logo:** Inserta el logo de Vino Pro IA en la escena 5 (asset en `static/` si existe).

## Entrega

- `vino_pro_ia_reel.mp4`: listo para subir a Instagram y TikTok.  
- Opcional: versión sin música para doblar en cada red.
