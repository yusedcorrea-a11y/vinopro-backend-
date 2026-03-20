# 100 vinos añadidos – Castilla y León (`espana.json`)

## Qué se hizo

- Se insertaron **100 fichas nuevas** en `data/espana.json` con claves **`cyl_*`** (sin pisar las claves ya existentes como `pingus`, `vega_sicilia`, etc.).
- **Enfoque geográfico:** Ribera del Duero, Rueda, Toro, Bierzo, Cigales, Arribes, Tierra de León (referencias), V.T. Castilla y León donde aplica.
- **Enfoque por marcas:** prioridad a productores y líneas muy reconocidos (Emilio Moro, Valduero, Villacreces, Cepa 21, Felix Callejo, Pagos de Carraovejas, Protos, Naia, Shaya, Maurodos, Pintia, Descendientes J. Palacios, etc.) y a vinos **corrientes** de súper/hostelería (Naia, Yllera, Colegiata, etc.).

## Cómo repetir o ampliar

```bash
python scripts/merge_cyl_100_espana.py
```

Si ya existen claves `cyl_*`, el script **fallará** con lista de colisiones (así no se duplica al ejecutar dos veces).

Para otra tanda, duplica el patrón en `scripts/merge_cyl_100_espana.py` con nuevas claves `cyl2_*` o edita el diccionario `NUEVOS`.

## Reinicio del servidor

Tras cambios en `espana.json`, **reinicia el backend** para recargar el catálogo.
