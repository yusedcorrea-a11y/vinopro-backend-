# Salone del Vino Torino – refuerzo de Italia (Piamonte)

## Aclaración importante

**No son bodegas “solo de Turín”.** El evento se llama Salone del Vino **Torino**, pero el listado de expositores incluye productores de **toda la región Piamonte**, identificados por **provincia** en el folleto:

| Sigla | Provincia        | Ejemplos de vinos / zonas                          |
|-------|------------------|----------------------------------------------------|
| **TO** | Torino           | Canavese, Carema, Pinerolese, collina torinese    |
| **CN** | Cuneo            | Langhe, Barolo, Barbaresco, Roero, Alta Langa      |
| **AT** | Asti             | Barbera d’Asti, Nizza, Moscato, Monferrato astigiano |
| **AL** | Alessandria      | Gavi, Ovada, Timorasso (Derthona), Monferrato     |
| **NO** | Novara           | Ghemme, Alto Piemonte                              |
| **BI** | Biella           | Lessona, Bramaterra (área histórica)              |

## Qué hay en la base de datos

- Archivo generado: **`data/italia_piemonte_salone_torino.json`**
- Claves internas: prefijo **`sdt_`** (Salone del Vino Torino), para no pisar entradas de `italia.json`.
- Cada ítem es una **ficha de vino representativa** por productor (nombre comercial genérico según zona: Barbera, Barolo, Gavi, Timorasso, etc.), con **bodega**, **comune** implícito en la descripción y **región** tipo `Piamonte, subzona (CN|AT|...)`.
- **No** se han volcado stands meramente institucionales (Region Piemonte, cámara de comercio, seguros, etc.) ni consorzi puros sin botella propia; sí **productores, cantine sociali, castelli, tenute**.

## Regenerar o ampliar

Si tienes una lista nueva del salón, edita el array `RAW` en:

`scripts/gen_italia_piemonte_salone_torino.py`

y ejecuta:

```bash
python scripts/gen_italia_piemonte_salone_torino.py
```

## Carga en el servidor

`app.py` carga **todos** los `.json` de `data/` (salvo exclusiones). Este archivo se mezcla automáticamente con el catálogo. **Reinicia el backend** tras generar o cambiar el JSON.

## Italia y guía en la app

Para usuarios en **Italia**, la guía “¿Dónde tomarlo?” sigue siendo **Gambero Rosso** (`GUIA_VINO_POR_PAIS["IT"]` en `enlaces_service.py`).

---

## Estado (v1 – cerrado para producción)

- **Implementación aceptada:** catálogo complementario **`data/italia_piemonte_salone_torino.json`** (~132 fichas, claves `sdt_*`).
- **Búsqueda / escaneo:** mismos campos que el resto del catálogo (`nombre`, `bodega`, `region`, `pais: Italia`, `tipo`, etc.).
- **Mantenimiento:** nuevas ediciones del salón → script `scripts/gen_italia_piemonte_salone_torino.py` y regenerar JSON.
- **Siguiente mejora opcional (otro día):** añadir expositores que faltan del folleto 1–151 o segunda botella por bodega si hace falta más granularidad.
