# Perú – guía, compra, base de datos y nota cultural

## Implementación en la app

| Pieza | Estado |
|--------|--------|
| **Guía “¿Dónde tomarlo?”** (IP **PE**) | **Guía de Vinos Perú** → `https://www.guiadevinosperu.com/` (`GUIA_VINO_POR_PAIS["PE"]`) |
| **Tienda local** | **Vinos Perú** (`vinosperu.com` búsqueda; afiliado `AFILIADO_PE` en `.env` opcional) |
| **Amazon** | Dominio **`amazon.com`** para usuarios Perú (envío/contexto habitual); tag `AMAZON_TAG_PE` o fallback global |
| **Catálogo** | **`data/peru.json`** – vinos nacionales (Ica, Cañete, Lunahuaná, Tacna, Majes) + **referencias importadas** frecuentes en Lima (Chile, Argentina, España) con `pais: "Perú"` para búsqueda desde usuario peruano |

## Nota cultural (producto / copy)

- El **pisco** es el destilado emblemático; el **vino** crece en ciudad. Conviene comunicar **respeto al pisco** y **valor al vino** sin competir en el mismo mensaje.
- Precios orientativos en **soles (PEN)** en las fichas nuevas.

## Idea: “Vino de la semana” – bodegas pequeñas (producto)

**Concepto:** cada semana destacar **gratis** en la app (banner, feed, push opcional) **un vino de una bodega humilde o poco conocida** (ej. una semana una bodega rusa, otra semana microbodegas de cualquier país).

**Por qué funciona:**

- Da **visibilidad** a quien no puede pagar marketing.
- Genera **contenido** y **historia** (“conoce al productor”).
- Refuerza la **comunidad VINEROS** y la percepción de que la app **no es solo grandes marcas**.

**Riesgos / cuidados:**

- **Calidad y verdad:** la promoción debe ser **honesta** (habéis probado el vino o confiáis en la fuente).
- **Logística:** contacto con la bodega (permiso de uso de nombre/imagen), **mayoría de edad**, **alcohol**.
- **Repetición:** reglas claras (1 vino/semana, criterio de elegibilidad).

**Implementación técnica futura (esqueleto):**

- JSON `data/vino_semana.json` con `{ "clave_vino", "desde", "hasta", "nota_editorial" }` o tabla si migráis a BD.
- Endpoint o flag en API para que el front muestre el bloque “Vino de la semana”.
- Opcional: formulario para que **bodegas pequeñas** soliciten ser candidatas.

Documento de producto ampliado: **`docs/IDEA_VINO_SEMANA_BODEGA_PEQUENA.md`**.
