# Plan después de estar en Google Play

**Objetivo:** Qué hacer cuando la app ya esté publicada en Google Play. Orden sugerido por impacto y esfuerzo.

---

## 1. Inmediato (primera semana / primer mes)

| Acción | Para qué |
|--------|----------|
| **Revisar la ficha en Play** | Que no haya errores, que el vídeo y las capturas se vean bien en distintos dispositivos. |
| **Monitorear reseñas y valoraciones** | Responder a los primeros comentarios (aunque sean pocos); corrige bugs críticos que salgan. |
| **Revisar Analytics en Play Console** | Instalaciones, desinstalaciones, países; qué pantallas usan más (si tienes eventos). |
| **Comunicar que ya está disponible** | Landing, redes, email a quien se apuntó a "Avísame cuando esté lista"; enlace directo a la ficha en Play. |
| **ASO básico** | Título, descripción breve y palabras clave ya están en `docs/TEXTOS_GOOGLE_PLAY.md` y `DESCRIPCION_APP_GOOGLE_PLAY_COPIAR_PEGAR.md`; ir afinando según búsquedas que traigan instalaciones. |

---

## 2. Corto plazo (producto – máximo impacto)

Cosas que suman valor con esfuerzo razonable y que ya tenéis documentadas como prioridad:

| Prioridad | Qué hacer | Dónde está la idea |
|-----------|-----------|---------------------|
| **1** | **Valoraciones de usuarios** | Puntuación 1–5 y nota de cata por vino; mostrar media en la ficha. Base para "recomendaciones por gusto" y más comunidad. | `ANALISIS_VINO_PRO_VS_COMPETENCIA.md` §7 |
| **2** | **Wishlist visible** | Lista "Quiero probar" bien integrada en perfil o bodega (ya hay lógica de sesión; falta sobre todo UI y prioridad). | Mismo doc |
| **3** | **Ventana de consumo en Mi Bodega** | "Mejor entre año X–Y" o "listo para beber"; refuerza el valor de la bodega. | Mismo doc |
| **4** | **Notificaciones en la app** | Que el usuario sepa que tiene mensaje nuevo en el chat (y, si aplica, actividad en feed). | `MEJORAS_PENDIENTES_VINEROS.md` |

Con esto la app se siente más "viva" y la comunidad empieza a aportar valor (valoraciones, wishlist).

---

## 3. Medio plazo (crecimiento y retención)

| Opción | Descripción | Referencia |
|--------|-------------|------------|
| **App nativa (iOS/Android)** | Mejor escaneo con cámara, notificaciones push, sensación de app "de verdad". React Native o similar, consumiendo el mismo backend. | `FASE_6_ROADMAP.md` – Fase 6A |
| **Feed social / seguir usuarios** | Ver qué valoran y qué beben otros; recomendaciones basadas en gente con gusto similar. | `FASE_6_ROADMAP.md` – Fase 6B |
| **Comparador de precios** | Mismo vino en varias tiendas con precio (estilo Wine-Searcher). Depende de tener fuente de datos (acuerdos o APIs). | `ANALISIS_VINO_PRO_VS_COMPETENCIA.md` §7 |

Se puede hacer primero valoraciones + wishlist + notificaciones y luego decidir si priorizas app nativa o feed social según métricas y tiempo.

---

## 4. Largo plazo / opcional

- **App Store (iOS)** si el backend y la lógica ya sirven para una app; solo hace falta build iOS y cumplir requisitos de Apple.
- **Marketing** (Google Ads de app, redes, colaboraciones) cuando tengas un poco de tracción y quieras acelerar.
- **B2B / restaurantes**: si el Adaptador tiene demanda, darle más visibilidad y soporte.
- **Más idiomas o mercados** siguiendo el patrón que ya tenéis (traducciones, guías por país).

---

## 5. Resumen en una frase

**Inmediato:** publicar, vigilar reseñas y métricas, comunicar y afinar ASO. **Corto plazo:** valoraciones de usuarios, wishlist clara, ventana de consumo en bodega y notificaciones (chat/feed). **Medio plazo:** app nativa y/o feed social y comparador de precios si tiene sentido. Todo lo demás (App Store, marketing, B2B) cuando la base esté sólida y tengáis datos para decidir.

---

*Documento creado a partir de `FASE_6_ROADMAP.md`, `ANALISIS_VINO_PRO_VS_COMPETENCIA.md`, `CIERRE_AREA_GOOGLE_PLAY_RENDER.md` y `MEJORAS_PENDIENTES_VINEROS.md`. Actualizar según prioridades reales.*
