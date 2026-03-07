# Análisis: Vino Pro IA vs otras apps de vino

**Objetivo:** Comparar nuestra app con las principales apps de vino del mercado para identificar **qué nos falta**, **qué nos sobra** y **dónde somos diferentes**.

**Referencias:** Vivino, CellarTracker, Wine-Searcher, Wine Spectator (y tendencias 2024).

---

## 1. Inventario actual: qué tiene Vino Pro IA

| Área | Funcionalidad | Estado |
|------|----------------|--------|
| **Escaneo** | Foto etiqueta, texto, código de barras; OCR + BD + Open Food Facts | ✅ |
| **Experto en Vinos IA** | Preguntas en lenguaje natural, maridajes, recomendaciones por tipo/país/precio; contexto conversacional ("y de esos el más barato"); recomendaciones personalizadas; feedback me gusta/no me gusta | ✅ |
| **Experto en Vinos voz** | Reconocimiento de voz en el front; opción IA local (agente 8080) para PRO | ✅ |
| **Bodega virtual** | Lista de botellas (nombre, añada, ubicación, cantidad); límite 50 Gratis / ilimitado PRO; valoración, alertas | ✅ |
| **Comprar** | Enlaces por vino (nacional, internacional, subastas); guías locales por país (30+ países); Amazon por país; detección de país por IP | ✅ |
| **Registro de vinos** | Añadir vino que no está en BD; oferta a otros (Premium); solicitudes de contacto | ✅ |
| **Planes y pago** | Gratis / PRO (4,99 €/mes); Stripe; webhook | ✅ |
| **Mapa** | Lugares cercanos (vinotecas, bares, restaurantes); geolocalización o búsqueda por ciudad | ✅ |
| **Dashboard** | Analytics: búsquedas, escaneos, preguntas experto en vinos; tendencias; por país; preguntas frecuentes | ✅ |
| **Informes** | PDF bodega; PDF cata (por vino) | ✅ |
| **Adaptador restaurantes** | Token API, config (nombre, webhook); integración stock para restaurantes | ✅ |
| **i18n** | 13 idiomas (es, en, pt, fr, de, it, ar, ru, tr, zh, ja, ko, hi) | ✅ |
| **Cobertura global** | Vinos de España, Francia, Italia, Argentina, Chile, India, China, Japón, Líbano, Marruecos, Argelia, Túnez, Israel, Rusia, etc. | ✅ |

---

## 2. Competidores: qué ofrecen

### Vivino (referente #1)

| Feature | Vivino | Vino Pro IA |
|--------|--------|--------------|
| Escaneo etiqueta | ✅ Muy potente, múltiples botellas a la vez | ✅ Una etiqueta + texto + código |
| Valoraciones comunidad | ✅ 340M+ valoraciones, 114M reseñas | ❌ No hay valoraciones de usuarios |
| Bodega / celler | ✅ Por uva, estilo, maridaje, ventana de consumo | ✅ Lista con ubicación, cantidad, alertas |
| Seguir usuarios / amigos | ✅ Ver qué beben, recomendaciones | ❌ No (solo roadmap Fase 6B) |
| Recomendaciones personalizadas | ✅ "Match for You", perfil de gusto tras 5 valoraciones | ✅ Basado en búsquedas y feedback (me gusta/no me gusta) |
| Maridaje | ✅ Por plato, con perfil de gusto | ✅ Por plato/cocina (incl. india, japonesa, etc.) |
| Compra / envío | ✅ Directo en app | ✅ Enlaces a tiendas + guías locales |
| Wishlist | ✅ | ❌ No |
| Juegos / gamificación | ✅ Adivinar vino, etc. | ❌ No |
| Idiomas / mercados | ✅ Muy amplio | ✅ 13 idiomas, muchos países |
| Premium | ✅ ~30 €/año | ✅ 4,99 €/mes |

### CellarTracker

| Feature | CellarTracker | Vino Pro IA |
|--------|----------------|-------------|
| Gestión de bodega | ✅ Ilimitado, ubicaciones, ventana de consumo, notas de consumo | ✅ Lista, ubicación, cantidad, alertas |
| Tasting notes / reseñas | ✅ 13M+ notas; comunidad + profesionales | ❌ No hay reseñas de usuarios |
| Seguir usuarios / descubrir por gusto | ✅ Actividad de seguidos, gustos similares | ❌ No |
| Foros / debates | ✅ Comunidad activa | ❌ No |
| IA (CellarChat) | ✅ Elegir qué beber, maridaje, análisis de bodega | ✅ Experto en Vinos conversacional + recomendaciones |
| Escaneo / código | ✅ Etiqueta, código, hasta recibo | ✅ Foto, texto, código |
| Precios / subastas | ✅ Precio de mercado, datos de subasta | ✅ Enlaces compra + guías |
| Profesionales | ✅ Críticos integrados | ❌ Solo nuestra BD + conocimiento |

### Wine-Searcher

| Feature | Wine-Searcher | Vino Pro IA |
|--------|----------------|-------------|
| Comparador de precios | ✅ 8M ofertas, 55k tiendas; PRO ve todo | ✅ Enlaces por vino + país; no comparador global |
| Críticos / puntuaciones pro | ✅ Decanter, Jane Anson, etc.; búsqueda por crítico | ❌ No |
| Escaneo | ✅ Reconocimiento de etiqueta | ✅ |
| Cercanía / tiendas cerca | ✅ Con precios locales | ✅ Mapa lugares (vinotecas, bares) |
| Enciclopedia / fichas | ✅ Uva, región, productor, añadas | ✅ Ficha por vino (descripción, maridaje, notas) |
| Spirits / cerveza | ✅ Sí | ❌ Solo vino |

### Wine Spectator

- Foco en **críticas y puntuaciones profesionales** (WineRatings Plus). Nosotros no tenemos integración con críticos externos.

---

## 3. Matriz resumida: tenemos / no tenemos / somos distintos

| Funcionalidad | Vivino | CellarTracker | Wine-Searcher | **Vino Pro IA** |
|---------------|--------|----------------|---------------|------------------|
| Escaneo etiqueta | ✅ | ✅ | ✅ | ✅ |
| Experto en Vinos / IA conversacional | Limitado | CellarChat | No | ✅ **Fuerte** |
| Maridaje (incl. cocinas mundo) | ✅ | ✅ | No | ✅ |
| Bodega virtual | ✅ | ✅✅ | No | ✅ |
| Valoraciones / reseñas usuarios | ✅✅ | ✅✅ | ✅ | ❌ |
| Seguir usuarios / feed social | ✅ | ✅ | No | ❌ |
| Recomendaciones personalizadas | ✅ | ✅ | No | ✅ (por sesión) |
| Compra / enlaces | ✅ | No | ✅✅ | ✅ + guías locales |
| Guías locales por país | No | No | No | ✅ **Único** |
| Informes PDF (bodega, cata) | No | No | No | ✅ **Único** |
| Adaptador restaurantes / stock | No | No | No | ✅ **Único** |
| Dashboard analytics (tendencias) | No (interno) | No | No | ✅ |
| 13 idiomas + cobertura global | ✅ | Menos | ✅ | ✅ |
| Precio PRO | ~30 €/año | Suscripción | ~7 €/mes | 4,99 €/mes |

---

## 4. Qué nos falta (gaps)

Ordenado por **impacto típico** para el usuario:

1. **Valoraciones y reseñas de usuarios**  
   - Puntuar vino (ej. 1–5) y escribir notas de cata.  
   - Es el núcleo de Vivino y CellarTracker. Sin esto, no hay “comunidad” ni recomendaciones basadas en gustos de otros.

2. **Seguir a otros usuarios / feed social**  
   - Ver qué beben y recomiendan otros.  
   - Aumenta retención y sensación de “comunidad”.

3. **Wishlist / “quiero probar”**  
   - Lista de vinos que el usuario quiere probar.  
   - Muy común en apps de consumo; bajo coste si ya tienes bodega.

4. **Ventana de consumo / “cuándo beberlo”**  
   - En bodega: sugerencia de “listo para beber” o “aguantar X años”.  
   - CellarTracker y Vivino lo tienen; refuerza el valor de Mi Bodega.

5. **Comparador de precios entre tiendas**  
   - Ver mismo vino en varias tiendas con precio (como Wine-Searcher).  
   - Nosotros damos enlaces y guías, pero no agregación de precios.

6. **Integración con críticos / puntuaciones pro**  
   - Mostrar puntuaciones de Decanter, Parker, etc.  
   - Diferenciador de Wine-Searcher y Wine Spectator; requiere acuerdos o APIs.

7. **App nativa iOS/Android**  
   - Hoy somos web. Una app nativa (Fase 6A) mejora escaneo con cámara y notificaciones.

8. **Gamificación / juegos**  
   - Tipo “adivinar el vino” (Vivino). Opcional; más para engagement que para utilidad core.

---

## 5. Qué nos sobra o podría simplificarse

Cosas que **no** suelen tener las apps de consumo y que podrían ser “de más” si no hay uso real:

1. **Dashboard de analytics (tendencias, por país, preguntas frecuentes)**  
   - Muy útil para **ti** (negocio/producto), no para el usuario final.  
   - **Sugerencia:** mantenerlo pero como herramienta interna o “Panel admin”, no como bloque destacado para todos. No quitarlo; reposicionarlo.

2. **Adaptador para restaurantes**  
   - Muy diferenciador si hay clientes B2B (restaurantes).  
   - **Sugerencia:** si no hay restaurantes usando, no invertir más por ahora; si hay demanda, es un argumento de venta PRO fuerte. No sobra; depende del enfoque B2B.

3. **Informes PDF (bodega, cata)**  
   - Poco común en apps de vino; más típico de herramientas “pro” o regalo.  
   - **Sugerencia:** mantener como valor añadido PRO; no quitar. Puede sobrar si nadie los descarga; en ese caso no promocionar tanto.

4. **Múltiples modos del experto en vinos (Nube vs IA local 8080)**  
   - La opción “IA local” es muy técnica para la mayoría.  
   - **Sugerencia:** mantener para PRO/power users; en la UI no hacerla el foco. No sobra; sobra solo si complica mucho el producto sin uso.

5. **Páginas o flujos duplicados**  
   - Revisar si “Registrar vino” y “Mi Bodega” solapan (añadir desde escaneo vs añadir manual).  
   - **Sugerencia:** un solo flujo “Añadir a mi bodega” (desde escaneo o desde cero); no eliminar registro si quieres que usuarios aporten vinos a la BD.

En resumen: **no hay que borrar nada grave**. Lo que “sobra” es sobre todo **énfasis** (dashboard muy visible, opciones muy técnicas) o **uso** (adaptador/PDF si no hay adopción). Ajustar prioridad en la UI y en la comunicación, más que eliminar funcionalidad.

---

## 6. Dónde somos fuertes (mantener y comunicar)

- **Experto en Vinos IA** con contexto, maridaje por cocina, recomendaciones por sesión y feedback.
- **Guías locales por país** (“dónde tomarlo”) en muchos mercados.
- **Adaptador restaurantes** (B2B) si apuestas por canal HORECA.
- **Informes PDF** como extra PRO.
- **Precio PRO** competitivo (4,99 €/mes).
- **Cobertura global** (idiomas + vinos de muchos países, incluidos Líbano, Marruecos, Israel, etc.).

---

## 7. Recomendaciones prioritarias

### Corto plazo (máximo impacto / esfuerzo razonable)

1. **Introducir valoraciones de usuarios**  
   - Puntuación 1–5 y opcionalmente nota de cata por vino.  
   - Mostrar media y número de valoraciones en ficha de vino.  
   - Base para luego “recomendaciones basadas en gente con tu gusto” (Fase 6B).

2. **Wishlist**  
   - Lista “Quiero probar” en perfil o bodega.  
   - Reutilizar lógica de bodega (lista de referencias a vinos).

3. **Ventana de consumo en Mi Bodega**  
   - Campo opcional “mejor entre año X–Y” o “listo para beber ya”; o estimación por tipo de vino.  
   - Refuerza el valor de la bodega sin depender de críticos externos.

### Medio plazo

4. **Feed social / seguir usuarios** (Fase 6B).  
5. **App nativa** (Fase 6A) para mejor escaneo y push.  
6. **Comparador de precios** si conseguís fuente de datos (scraping o acuerdos con tiendas).

### No priorizar por ahora

- Integración con críticos (coste legal/económico alto).  
- Spirits/cerveza (mantener foco vino).  
- Juegos/gamificación hasta tener base social y valoraciones.

---

## 8. Resumen en una frase

**Nos falta sobre todo comunidad (valoraciones, reseñas, seguir usuarios y feed); nos sobra sobre todo “énfasis” en cosas que el usuario final no ve (dashboard) o que son muy de nicho (adaptador/PDF si no hay uso). Nuestro núcleo fuerte es el experto en vinos IA + maridaje + guías locales + cobertura global; el siguiente paso con más impacto es añadir valoraciones y wishlist y, cuando tenga sentido, feed social y app nativa.**

---

*Documento generado para apoyo a decisiones de producto. Fuentes: funcionalidades actuales del codebase, Vivino, CellarTracker, Wine-Searcher, Wine Spectator y artículos sobre mejores wine apps 2024.*
