# Guías de vino por país – ¿Dónde tomarlo?

## Descripción

En la página de compra de cada vino (`/vino/{id}/comprar`) se muestra una sección **«¿Dónde tomarlo?»** que enlaza a una guía de vinos, vinotecas o restaurantes según el **país detectado** del usuario. Así, un usuario en España ve la Guía Repsol; uno en Italia, Gambero Rosso; etc.

## Cómo se determina el país

- El país se obtiene por **IP** en el backend con el servicio `enlaces_service.detectar_pais_por_ip(ip)`.
- Se usa el API pública de **ip-api.com** (solo código de país, sin clave).
- Si la IP es localhost o falla la petición, se usa **ES** (España) por defecto.
- El código de país es de dos letras en mayúsculas (ES, IT, FR, etc.).

## Guías implementadas

### Europa

| País        | Código | Guía                 | URL |
|-------------|--------|----------------------|-----|
| España      | ES     | Guía Repsol          | https://www.guiarepsol.com/es/soletes/vinotecas-y-bodegas/ |
| Italia      | IT     | Gambero Rosso         | https://www.gamberorosso.it/vini/ |
| Francia     | FR     | Guide Hachette        | https://www.leguidehachette.com/ |
| Portugal    | PT     | Revista de Vinhos     | https://www.revistadevinhos.pt/ |
| Alemania    | DE     | Gault&Millau          | https://www.gaultmillau.de/wein/ |
| Reino Unido | GB/UK  | Decanter              | https://www.decanter.com/wine-reviews/ |
| Bélgica     | BE     | Gault&Millau Belgique | https://www.gaultmillau.be/ |
| Países Bajos| NL     | Gault&Millau Nederland| https://www.gaultmillau.nl/ |
| Suiza       | CH     | Gault&Millau Suisse   | https://www.gaultmillau.ch/ |
| Austria     | AT     | Falstaff              | https://www.falstaff.at/wein/ |
| Suecia      | SE     | Vinjournalen          | https://www.vinjournalen.se/ |
| Noruega     | NO     | Vinforum              | https://www.vinforum.no/ |
| Dinamarca   | DK     | Vinbladet             | https://www.vinbladet.dk/ |
| Finlandia   | FI     | Viinilehti            | https://www.viinilehti.fi/ |
| Polonia     | PL     | Czas Wina             | https://www.czaswina.pl/ |
| Rep. Checa  | CZ     | Víno z Moravy a z Čech| https://www.vinazmoravyvinazcech.cz/ |
| Hungría     | HU     | Magyar Bor            | https://winesofhungary.hu/ |
| Grecia      | GR     | Oinorama              | https://www.oinorama.gr/ |

### América

| País      | Código | Guía                      | URL |
|-----------|--------|---------------------------|-----|
| EE.UU.    | US     | Wine Spectator            | https://www.winespectator.com/ |
| México    | MX     | Guía del Vino México       | https://www.guiadelvinomexico.com/ |
| Argentina | AR     | Guía de Vinos Argentina   | https://www.guiadevinos.com.ar/ |
| Chile     | CL     | Guía de Vinos Chile       | https://www.guiadevinos.cl/ |
| Brasil    | BR     | Guia de Vinhos Brasil     | https://www.guiadevinosbrasil.com/ |
| Uruguay   | UY     | Guía de Vinos Uruguay     | https://www.guiadevinosuruguay.com/ |
| Perú      | PE     | Guía de Vinos Perú        | https://www.guiadevinosperu.com/ |
| Colombia  | CO     | Guía de Vinos Colombia    | https://www.guiadevinoscolombia.com/ |

### Otros continentes

| País         | Código | Guía                  | URL |
|--------------|--------|-----------------------|-----|
| Sudáfrica    | ZA     | Platter's Wine Guide  | https://www.wineonaplatter.com/ |
| Australia    | AU     | Halliday Wine Companion | https://www.winecompanion.com.au/ |
| Nueva Zelanda| NZ     | Bob Campbell MW       | https://www.bobcampbell.nz/ |
| Japón        | JP     | JWINE (日本ワイン)     | https://jwine.net/ |

### Países sin guía específica (fallback)

Para **Cuba (CU), Rep. Dominicana (DO), Costa Rica (CR), Panamá (PA), Ecuador (EC), Bolivia (BO), Paraguay (PY), Turquía (TR), China (CN), India (IN), Israel (IL), Líbano (LB)** y cualquier otro país no listado se usa el **fallback**: Guía Repsol (vinotecas y bodegas) con icono 🌍.

## Dónde está el código

- **Mapa país → guía:** `services/enlaces_service.py`: constantes `GUIA_VINO_POR_PAIS` y `FALLBACK_GUIA`, función `get_guia_vinos_por_pais(pais)`.
- **Página de compra:** `routes/comprar.py` obtiene la guía con `get_guia_vinos_por_pais(pais)` y pasa `guia_vinos` al template.
- **Plantilla:** `templates/comprar_vino.html`: bloque «comprar-guia-pais» con título, descripción (con nombre del país traducido) y botón con emoji + «Buscar en [Nombre guía]».
- **Traducciones:** En `data/translations/*.json`, dentro de `comprar`: `guia_descripcion`, `guia_buscar`, `pais_ES`, `pais_IT`, …, `pais_OTROS`.

## Cómo añadir una nueva guía

1. En **`services/enlaces_service.py`**, añade una entrada en **`GUIA_VINO_POR_PAIS`**:

   ```python
   "XX": {  # Código ISO del país (2 letras mayúsculas)
       "nombre": "Nombre de la guía",
       "url": "https://...",
       "emoji": "🇽🇽",
   },
   ```

2. En **`data/translations/`**, en cada idioma (es, en, pt, fr, de, it), añade la clave del país dentro de **comprar**:

   ```json
   "pais_XX": "Nombre del país en ese idioma"
   ```

3. Reinicia el backend (o recarga) y prueba entrando en `/vino/{id}/comprar` con una IP del país XX (o simulando el código en pruebas).

## Limitaciones

- El país se basa **solo en la IP**; no se usa geolocalización del navegador ni preferencia del usuario.
- Las URLs de las guías son enlaces externos; si una guía cambia de dominio o ruta, hay que actualizar `GUIA_VINO_POR_PAIS` manualmente.
- No hay integración con APIs de esas guías; solo se redirige a la web correspondiente.
