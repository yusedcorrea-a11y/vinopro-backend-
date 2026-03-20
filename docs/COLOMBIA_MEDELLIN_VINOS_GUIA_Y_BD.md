# Colombia y Medellín – vinos, guía y base de datos

## Resumen para el producto

- **Guía “¿Dónde tomarlo?” (usuario con IP en Colombia):** **Ya implementada.** Código **CO** → **Guía de Vinos Colombia** → `https://www.guiadevinoscolombia.com/` (`services/enlaces_service.py`, `GUIA_VINO_POR_PAIS["CO"]`). No hace falta duplicar lógica por ciudad: la guía es **nacional**; Medellín entra como cualquier otra ciudad colombiana.
- **Compra / búsqueda:** **Vinoteca Colombia** ya mapeada para **CO** (`enlaces_service.py`).
- **Catálogo de vinos colombianos:** Nuevo archivo **`data/colombia.json`** con referencias **nacionales** (Antioquia, Boyacá, Cundinamarca, Villa de Leyva, etc.). Reiniciar el servidor para cargarlo.

---

## Medellín en contexto (por qué no hay “solo Medellín” en la BD)

- **Medellín (Antioquia)** es sobre todo **hub de consumo**: vinotecas, restaurantes en **El Poblado**, **Laureles**, **Provenza**, cadenas **Carulla**, **Éxito**, **Makro**, etc. Lo que más verá un tester en Medellín al **escanear** son etiquetas **importadas** (Chile, Argentina, España, EE. UU.) → esas fichas siguen viniendo de **chile.json**, **argentina.json**, **espana.json**, etc.
- La **producción vitivinícola nacional** es **minoritaria** y está repartida: **Antioquia** (p. ej. zona de **Sonsón**, **Rionegro/Llanogrande** con proyectos emergentes), **Boyacá**, **Villa de Leyva**, **Cundinamarca**, algo en **Valle**. Por eso la BD “Colombia” cubre **vinos de país Colombia**, no un archivo separado “solo Medellín”: geográficamente el vino **hecho en Antioquia** sí representa lo más cercano al tester de Medellín.

---

## Qué vinos son “los más comunes” en Colombia

| Origen | Realidad en mercado (incl. Medellín) |
|--------|--------------------------------------|
| **Importados** | **Chile y Argentina** dominan estantería; **España, Italia, Francia** muy presentes en gama media-alta. |
| **Nacionales** | Proyectos **artesanales y boutique**; variedades como **Syrah, Cabernet Sauvignon, Merlot, Sauvignon Blanc**, y en algunas zonas **Criolla Chica / uvas históricas**. Muchos vinos colombianos se venden **directo bodega, e-commerce o vinotecas** más que en súper masivo. |

La app queda redonda si: **colombia.json** cubre **nacional** + el usuario en Medellín sigue teniendo **guía CO** + **Vinoteca** + el resto del catálogo mundial para **importados**.

---

## Implementación técnica

1. **Guía:** `GUIA_VINO_POR_PAIS["CO"]` (ya hecho).
2. **Compra:** `ENLACES_COMPRA_POR_PAIS["CO"]` → Vinoteca Colombia (ya hecho).
3. **BD:** `data/colombia.json`, mismo esquema que `espana.json` / `suiza.json`; campo **`"pais": "Colombia"`** (debe coincidir con `CODIGO_A_NOMBRE_PAIS` en `busqueda_service.py`).
4. **Ampliar:** `python scripts/generar_vinos_ia.py --pais colombia --cantidad 150 --output data/vinos_co_masivos.json` (revisar que cada vino lleve `"pais": "Colombia"`).

---

## Referencias útiles (contenido / marketing)

- **Guía de Vinos Colombia** (web ya enlazada).
- Para **bodegas y turismo**: proyectos en **Villa de Leyva**, **Boyacá**, **Antioquia** (Sonsón, Llanogrande); búsqueda “vinos colombianos bodega” para actualizar el catálogo con nombres reales nuevos.

---

*Documento alineado con `docs/GUIAS_VINO_POR_PAIS.md` y `docs/SUIZA_VINOS_GUIA_Y_BD.md`.*
