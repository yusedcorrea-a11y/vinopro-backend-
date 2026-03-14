# Cómo conseguir que las tiendas os paguen por los enlaces

En la app ya hay **enlaces de compra** por país (Amazon donde existe + **tiendas locales** en países sin Amazon). Para que os paguen por cada clic o venta, tenéis que **daros de alta como afiliados** y configurar vuestro ID en el servidor.

---

## 1. Qué hace la app

- **Países con Amazon:** se usa vuestro **AMAZON_ASSOCIATE_TAG** (variable de entorno). Si está definido, todos los enlaces a Amazon llevan vuestro tag y Amazon os paga según el programa Associates del país correspondiente.
- **Países sin Amazon:** la app muestra **tiendas locales** (Argentina, Chile, Israel, etc.). Cada tienda tiene una variable de entorno opcional (ej. `AFILIADO_AR`, `AFILIADO_IL`). Si la definís con el ID que os dé esa tienda o su red de afiliados, el enlace incluirá ese ID y podréis cobrar.

---

## 2. Qué tenéis que hacer para que os paguen

### Amazon (todos los países con marketplace)

1. Entrad en **Amazon Associates** en cada país donde queráis monetizar:
   - [associates.amazon.es](https://affiliate-program.amazon.es) (España)
   - [affiliate-program.amazon.com](https://affiliate-program.amazon.com) (EE.UU.)
   - Y lo mismo para .co.uk, .de, .fr, .it, .com.mx, .com.br, .co.jp, .com.au, .in, .nl, .com.tr, etc.
2. Cada país os dará un **tag distinto**. En el `.env` usad una variable por país:
   ```env
   AMAZON_TAG_JP=vinoproia-22
   AMAZON_TAG_US=vinoproia-20
   AMAZON_TAG_GB=vinoproia-21
   AMAZON_TAG_FR=vinoproia-21
   AMAZON_TAG_DE=vinoproia-21
   AMAZON_TAG_NL=vinoproia-21
   AMAZON_TAG_ES=vinoproia-21
   ```
   El sistema busca primero `AMAZON_TAG_XX` (donde XX es el código de país). Si no existe, usa `AMAZON_ASSOCIATE_TAG` como fallback global:
   ```env
   AMAZON_ASSOCIATE_TAG=vinoproia-21
   ```

### Tiendas locales (países sin Amazon)

Para cada país la app usa una **URL de búsqueda** a una tienda (ej. Argentina, Chile, Israel). Para monetizar:

1. **Comprobar si la tienda tiene programa de afiliados**
   - En la web de la tienda: buscad “afiliados”, “partners”, “programa de afiliados” o “affiliate”.
   - O entrad en redes de afiliados que agrupan tiendas:
     - **Awin** (awin.com): muchas tiendas de varios países
     - **CJ Affiliate** (cj.com)
     - **TradeDoubler**, **Rakuten Advertising**, etc.
2. **Daros de alta** en ese programa y que os asignen un **ID / tag** (suele ser un código o parámetro que se añade a la URL, ej. `?ref=TU_ID`).
3. **Configurar la variable en el servidor**  
   En `services/enlaces_service.py` cada país tiene una clave `afiliado_env` (ej. `AFILIADO_AR`, `AFILIADO_IL`). En el `.env` del servidor:
   ```env
   AFILIADO_AR=tu-id-argentina
   AFILIADO_IL=tu-id-israel
   ```
   La app ya está preparada para añadir ese parámetro a la URL cuando la variable existe.

Si una tienda **no tiene afiliados**, podéis:
- Cambiar la URL en `TIENDAS_LOCALES_POR_PAIS` por otra tienda del mismo país que sí tenga programa, o
- Contactar con la tienda y proponer un acuerdo (pago por clic, por venta o por colocación).

---

## 3. Variables de entorno resumen

| Variable | Uso |
|----------|-----|
| `AMAZON_TAG_JP` | Tag de Amazon Associates Japón |
| `AMAZON_TAG_US` | Tag de Amazon Associates EE.UU. |
| `AMAZON_TAG_GB` | Tag de Amazon Associates Reino Unido |
| `AMAZON_TAG_FR` | Tag de Amazon Associates Francia |
| `AMAZON_TAG_DE` | Tag de Amazon Associates Alemania |
| `AMAZON_TAG_NL` | Tag de Amazon Associates Holanda |
| `AMAZON_TAG_ES` | Tag de Amazon Associates España |
| `AMAZON_ASSOCIATE_TAG` | Tag global (fallback si no hay tag específico por país) |
| `AFILIADO_AR` | ID afiliado tienda Argentina |
| `AFILIADO_CL` | ID afiliado tienda Chile |
| `AFILIADO_IL` | ID afiliado tienda Israel |
| `AFILIADO_NZ`, `AFILIADO_ZA`, etc. | Igual para el resto de países en `TIENDAS_LOCALES_POR_PAIS` |

Las claves exactas están en `services/enlaces_service.py` en cada entrada de `TIENDAS_LOCALES_POR_PAIS` (campo `afiliado_env`).

---

## 4. Comprobar que funciona

1. Definid en `.env` al menos `AMAZON_ASSOCIATE_TAG` y, si tenéis, un `AFILIADO_XX` de prueba.
2. Entrad en la app a **Comprar** un vino desde un país con tienda local (o cambiando el país con `?pais=AR` en la URL).
3. Abrid el enlace de “Amazon” o de la tienda local: la URL debe llevar `tag=...` (Amazon) o el parámetro que use la tienda (ej. `ref=...`) con vuestro ID.

Si queréis, el siguiente paso puede ser revisar juntos las URLs de una tienda concreta (por país) para dejarlas listas con vuestro ID de afiliado.
