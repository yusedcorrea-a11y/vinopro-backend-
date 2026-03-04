# Imágenes de fondo Vino Pro IA

El CSS está configurado para usar estas imágenes. Si no existen, se verá el color de fondo.

## Modo claro (página Inicio)
- **Archivo:** `vino-pro-ia-fondo-claro-espectacular.jpg`
- **Descripción:** Viñedo infinito en colina al atardecer, hileras de vides verdes/doradas, cielo naranja/rosa/púrpura, copas sobre madera clara, estilo 8K horizontal.

## Modo oscuro (todas las páginas)
- **Archivo:** `vino-pro-ia-fondo-oscuro-espectacular.jpg`
- **Descripción:** Bodega antigua con barricas, iluminación dramática, tonos negros/marrones/ámbar, estilo cinematográfico.

## Página Planes
- **Modo claro:** `vino-pro-ia-fondo-planes-claro.jpg` — Mujer en bodega elegante, mesa con copa de vino y tableta con opciones de planes. Iluminación cálida.
- **Modo oscuro:** `vino-pro-ia-fondo-planes-oscuro.jpg` — Hombre en bodega con iluminación tenue, junto a barrica, copa de vino y teléfono con opciones. Ambiente nocturno elegante.

## Página Adaptador (restaurantes)
- **Modo claro:** `vino-pro-ia-fondo-adaptador-claro.jpg` — La Sumiller: mujer sumiller en restaurante de alta gama, traje profesional, cerca de barra o bodega; al fondo camarero lleva vino a la mesa. Iluminación cálida, ambiente sofisticado.
- **Modo oscuro:** `vino-pro-ia-fondo-adaptador-oscuro.jpg` — El Sumiller: hombre sumiller en restaurante elegante con luz tenue, chaqueta profesional, junto a bodega o estantería de vinos; al fondo camarero sirve vino a mesa con velas. Ambiente nocturno, tonos cálidos, elegancia.

Puedes generarlas con la herramienta de imágenes del proyecto o añadir aquí tus propias fotos con estos nombres.

## Comportamiento en móvil y tablet

En **móvil** (ancho &lt; 768px) las imágenes de fondo usan `background-size: contain` para que se vea la imagen completa (sin recortar el sujeto); el espacio sobrante se rellena con color oscuro. En **tablet** (768px–1024px) se mantiene `cover` con `background-position: top center` para priorizar el punto focal.

### Opción avanzada: imágenes por dispositivo

Si quieres una imagen distinta en móvil (por ejemplo recorte vertical centrado en la persona), puedes crear versiones con sufijo y añadir en `style.css` las URLs en los `@media` correspondientes:

- `-mobile.jpg` — Enfoque en sujeto principal, formato vertical recomendado.
- `-tablet.jpg` — Versión intermedia (opcional).

Hoy el CSS usa la misma imagen en todos los tamaños y solo cambia `background-size` y `background-position`.
