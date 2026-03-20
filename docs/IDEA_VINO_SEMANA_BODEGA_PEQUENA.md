# Idea de producto: Vino de la semana (bodegas pequeñas / humildes)

## Objetivo

Acercar **bodegas pequeñas, artesanales o de países poco habituales** a la comunidad, rotando un **destacado gratuito** (p. ej. una semana) para generar **historia, confianza y uso** de la app fuera del catálogo mainstream.

## Ejemplo de calendario

| Semana | Enfoque |
|--------|---------|
| N | Vino de una **bodega humilde de Rusia** (o Georgia, Líbano, etc.) |
| N+1 | **Microbodegas** no reconocidas de un país elegido (España, Italia, Perú…) |
| N+2 | **Productor emergente** propuesto por la comunidad (votación ligera) |

## Qué mostraría la app

- Ficha del vino (o entrada editorial si aún no está en BD).
- Texto corto: **quién es el productor**, **dónde está**, **por qué lo elegimos**.
- CTA: escanear, guardar en bodega, compartir en VINEROS.

## Criterios de selección (borrador)

- Bodega **independiente** o **pequeña producción** (definir umbral simple).
- Acuerdo **tácito o explícito** con el productor (email / DM).
- **Sin conflicto** con publicidad de pago (esta franja es “editorial / comunidad”).

## Ejecución (implementado – v1)

1. **Config:** `data/vino_semana.json`  
   - `activo`, `desde`, `hasta`, `vino_key` (clave en catálogo, opcional), `titulo_es` / `texto_es`, `titulo_en` / `texto_en`, `pais_destacado`, `bodega_pequena`, `contacto_productores`.
2. **API:** `GET /api/vino-semana?lang=es` devuelve JSON con texto + `vino` si `vino_key` existe en la BD cargada.
3. **Catálogo:** `vino_semana.json` está **excluido** en `app.py` de la fusión de vinos (no cuenta como ficha de botella).
4. **Front / app móvil:** consumir el endpoint y mostrar banner o tarjeta en home o comunidad.

### Cómo poner un vino real una semana

1. Elige una clave existente (ej. `pe_intipalka_reserva` en `peru.json`).
2. Edita `data/vino_semana.json`: `"vino_key": "pe_intipalka_reserva"`, ajusta fechas y textos.
3. Despliega o reinicia el servidor.

---

*Idea aportada por el equipo; v1 API lista; pulir UI cuando toque.*
