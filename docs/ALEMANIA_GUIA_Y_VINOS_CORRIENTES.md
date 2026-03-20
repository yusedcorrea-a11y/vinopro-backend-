# Alemania – guía y vinos corrientes en la BD

## Guía “¿Dónde tomarlo?”

- Código **DE** → **Gault&Millau** (sección vino): `https://www.gaultmillau.de/wein/`  
- Configurado en `services/enlaces_service.py` → `GUIA_VINO_POR_PAIS["DE"]`.  
- **No** es Guía Repsol (es España); en Alemania el enlace equivalente de prestigio editorial que ya usáis es Gault&Millau.

## Compra (Amazon)

- Variable de país **DE** → `amazon.de` (tags de afiliado por `.env` si los tenéis).

## Base de datos `data/alemania.json`

- Ya contenía vinos **premium** (Mosel, Nahe, Rheingau, GG, etc.).
- Se amplió con **~28 fichas “corrientes”**: supermercado, marcas muy difundidas (Blue Nun, Black Tower, Dr. Zenzen, Leonard Kreusch, Moselland, Rotkäppchen, Henkell…), variedades de consumo diario (**Dornfelder**, **Portugieser**, **Trollinger**, **Lemberger**, **Müller-Thurgau**, **Silvaner** en Bocksbeutel, **Grauburgunder** / **Weißburgunder** de entrada, **Regent**, Riesling **halbtrocken** de Rheinhessen, **Bag in Box** Mosel, etc.).
- Tras **reiniciar el backend**, el total de vinos alemanes sube automáticamente (carga global de `data/*.json`).

## Ampliar más

```bash
python scripts/generar_vinos_ia.py --pais alemania --cantidad 200 --output data/vinos_de_masivos.json
```

(Revisar que cada registro conserve `"pais": "Alemania"`.)
