# Suiza – vinos típicos, bodegas y guía “tipo Repsol”

## Resumen para el producto

- **Guía en la app (¿Dónde tomarlo?):** **Ya implementada.** Código **CH** → **Gault&Millau Suisse** (`https://www.gaultmillau.ch/`). En España usáis **Guía Repsol**; en Suiza el equivalente habitual de **restauración / escena gastronómica** que ya mapeamos es **Gault&Millau** (como en DE, BE, NL). **Repsol no tiene guía suiza** equivalente a la española.
- **Compra / búsqueda local:** En `enlaces_service.py` ya existe tienda **Wein.ch** para **CH** (búsqueda genérica).
- **Catálogo de vinos:** Se añade **`data/suiza.json`** con vinos representativos (`"pais": "Suiza"`) para que búsqueda y escáner tengan **base mínima** en CH.

---

## Vinos y variedades más característicos en Suiza

| Tipo / nombre | Notas |
|---------------|--------|
| **Chasselas** (en Vaud a menudo vendido como vino de **Lavaux**, **Dézaley**, etc.) | Uva blanca dominante en **Vaud**; vinos secos, ligeros, muy “suizos”. |
| **Fendant** | Nombre tradicional en **Valais** para Chasselas (misma uva en la práctica comercial). |
| **Petite Arvine**, **Amigne**, **Heida (Païen)** | Blancos de **Valais** muy identitarios. |
| **Cornalin**, **Humagne Rouge** | Tintos autóctonos del **Valais**. |
| **Pinot Noir** (**Blauburgunder**) | Muy presente en **Suiza alemana** y en buena parte del país. |
| **Gamay** | Sobre todo **Ginebra** y zonas vecinas. |
| **Merlot** | Estrella en **Ticino** (cerca de Italia). |

La producción suiza es **pequeña** y **casi todo se consume en el país**; por eso en escaneo muchas etiquetas serán **importadas** (IT, FR, ES) — la base local ayuda a **no quedar vacíos** en vinos suizos típicos.

---

## Regiones y bodegas (referencia, no exhaustivo)

- **Valais (Wallis):** mayor volumen; muchas cooperativas y productores como **Provins**, bodegas boutique en terrazas al Ródano.
- **Vaud:** **Lavaux** (UNESCO), Chablais; Chasselas y espumosos.
- **Ticino:** Merlot, clima mediterráneo.
- **Suiza alemana:** Pinot Noir, Riesling, Müller-Thurgau en zonas como **Zürichsee**, **Schaffhausen** (Klettgau), **Grisons** (Bündner Herrschaft con Pinot Noir).

Para **ampliar catálogo** sin inventar: **Swiss Wine** (`swisswine.ch`) agrega información oficial sobre regiones y productores.

---

## Implementación técnica (igual que otros países)

1. **Guía:** `services/enlaces_service.py` → `GUIA_VINO_POR_PAIS["CH"]` (ya hecho).
2. **Tests:** `scripts/test_guia_por_pais_unit.py` incluye **CH** (ya hecho).
3. **BD vinos:** archivo **`data/suiza.json`**, mismo esquema que `espana.json` (clave slug → objeto con `nombre`, `bodega`, `region`, `pais`, `tipo`, etc.). El servidor carga **todos** los `.json` de `data/` salvo la lista de exclusión en `app.py` → al reiniciar, entran los vinos suizos.
4. **Más vinos:** `python scripts/generar_vinos_ia.py --pais suiza --cantidad 200 --output data/vinos_ch_masivos.json` (fusiona según el script; revisar que `pais` en cada registro sea **Suiza**).

---

## Documentación relacionada

- `docs/GUIAS_VINO_POR_PAIS.md` – tabla Europa incluye **Suiza | CH | Gault&Millau Suisse**.
