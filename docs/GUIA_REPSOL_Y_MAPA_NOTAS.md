# Guía Repsol, mapa y “información básica” por país

## Qué ya hace la app

- **Página Comprar vino** (`/vino/.../comprar`): el botón “Guía…” usa **`get_guia_vinos_por_pais(pais)`** en `services/enlaces_service.py`.
  - **España** → enlace directo a Repsol (vinotecas y bodegas).
  - **Argentina, Chile, México, etc.** → cada país tiene su **URL propia** (no siempre Repsol): por ejemplo AR usa guía argentina, IT usa Gambero Rosso, etc.
- **Página Mapa → pestaña Guía Repsol**: el botón abre `guiarepsol.com` con búsqueda opcional si el usuario escribió una ciudad en el campo de arriba (`?q=Valladolid`). Lo que muestre Repsol al entrar **lo controla su web**, no podemos “forzar” que salga solo información básica sin que ellos expongan API o parámetros documentados.

## Limitación

Repsol (y el resto de guías externas) son **webs de terceros**. Podemos:

- Abrir la **URL correcta por país** en Comprar (ya hecho).
- En el mapa, abrir Repsol **+ término de búsqueda** si el usuario escribe ciudad (ya hecho en `buildRepsolUrl()`).

No podemos modificar el **contenido interno** de la guía Repsol (qué sale al buscar Valladolid) sin acuerdo/API con ellos.

## Mejora futura posible

- Si Repsol (u otra guía) publica **URLs estables por ciudad o región**, se pueden añadir en `GUIA_VINO_POR_PAIS` o en un mapa `ciudad → url`.
- **WebView propia** con resumen “solo básico” solo tendría sentido si generamos nosotros el resumen (scraping no recomendable por legal/técnica).

## Cambios recientes (mapa)

- **Mi ubicación**: además de rellenar lista y mapa Leaflet en la pestaña **Selección VINO PRO**, abre **Google Maps** en nueva pestaña con búsqueda de vinotecas/bares de vino cerca de las coordenadas.
- **Selección VINO PRO**: sigue siendo el sitio del **mini mapa + lista** de la API; el usuario puede volver a esa pestaña después de cerrar Google Maps.
