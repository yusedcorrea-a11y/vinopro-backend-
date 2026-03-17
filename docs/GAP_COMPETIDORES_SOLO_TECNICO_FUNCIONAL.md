# Qué tienen ellos que nosotros no (solo técnico y funcional)

**Excluido de la comparación:** tamaño de base de datos y notoriedad de marca.  
**Objetivo:** Listar funciones y capacidad técnica que los competidores ofrecen y nosotros aún no, para igualar o superar.

---

## 1. Resumen ejecutivo

- **Ya estamos muy alineados** en: escaneo (imagen + EAN + OFF), experto/sumiller, maridaje (Spoonacular + BD), certificaciones (OFF), noticias (GNews), comunidad (perfil, seguir, feed, chat), valoraciones, wishlist, bodega virtual, QR, ofertas, compra/enlaces, informes PDF, analytics, planes Stripe, geolocalización, multiidioma.
- **Gaps a cerrar** para estar a nivel o por encima (solo técnica y funcionalidad) son los siguientes.

---

## 2. Gaps por competidor (solo técnico / funcional)

### Vivino

| Lo que tienen ellos | Nosotros | Acción posible |
|---------------------|----------|----------------|
| **Comparador de botellas** (Quick Compare: varios vinos lado a lado, ratings, región, precio, maridaje) | No tenemos comparador en UI | Añadir vista “Comparar” con 2–4 vinos seleccionables desde ficha o búsqueda |
| **Perfil de gusto visual** (estilo, región, uva según lo que valoras) | Tenemos historial (vistos, likes, búsquedas) y recomendaciones por sesión; no un “perfil de gusto” mostrado al usuario | Definir perfil (por valoraciones/búsquedas) y una pantalla “Tu perfil de gusto” (estilo/región/uva) |
| **Puntuación de afinidad “Match for You”** (0–100 % “cuánto te puede gustar este vino” tras X valoraciones) | Recomendaciones por sesión; no un % de match por botella | Calcular score de afinidad por vino (reglas o modelo) y mostrarlo en ficha (ej. “85 % para ti”) |
| **Características de sabor visuales** (dulzor, cuerpo, acidez + descriptores de la comunidad) | Ficha con notas/maridaje; no gráficos de perfil sensorial | Opcional: bloques “Cuerpo”, “Dulzor”, “Fruta” en ficha (datos de BD o OFF si hay) |
| **Maridaje que usa tu perfil de gusto** | Maridaje por tipo/plato (Spoonacular + BD), no filtrado por gusto del usuario | En futuro: filtrar o ordenar maridajes según perfil de gusto |
| **Cajas curadas / Mixed Case** (comprar caja de 6 vinos similares) | Enlaces de compra y ofertas; no “caja curada” como producto | Opcional: “Pack recomendado” (varios vinos) con enlace a compra |

### Delectable

| Lo que tienen ellos | Nosotros | Acción posible |
|---------------------|----------|----------------|
| **Reseñas de críticos integradas** (ej. Vinous) | No tenemos integración con críticos/pros | Si hay API o feed de críticos: mostrar “Crítico: …” en ficha |
| **Listas curatoriales** (Top 10 Rioja, Mejores para carne, etc.) | Feed y canales; no listas “curated” por tema | Crear entidad “Lista” (nombre, descripción, lista de keys) y vista “Listas” (por región, maridaje, etc.) |
| **Cerveza y destilados** (misma app) | Solo vino | Decisión de producto: mantener solo vino o ampliar categorías más adelante |
| **Alertas estado de añada** (“mejor beber antes de 2028”) | Bodega con alertas; no “vintage condition” explícito por añada | Opcional: campo “Ventana de consumo” en ficha y alertas en bodega |
| **OCR muy robusto** para etiquetas borrosas/relieve | OCR + Gemini; no especializado en “difíciles” | Mejorar preprocesado de imagen o modelo cuando tengamos casos reales |

### Vinora / Vinozo / Sommo / WineIQ (indie IA)

| Lo que tienen ellos | Nosotros | Acción posible |
|---------------------|----------|----------------|
| **IA generativa (LLM) para respuestas de sommelier** (texto libre, muy natural) | Sumiller por reglas + contexto (sin LLM) | Integrar un LLM (ej. Gemini) para respuestas largas o preguntas abiertas, manteniendo reglas para datos concretos |
| **Perfil de gusto aprendido con IA** | Historial + recomendaciones por reglas | Igual que Vivino: perfil de gusto explícito; opcionalmente modelo que aprenda de valoraciones |
| **Diario de cata estructurado (estilo WSET)** | Notas en ficha e informes; no plantilla WSET | Opcional: plantilla “Diario de cata” (vista, nariz, boca, conclusiones) en informe o en comunidad |
| **“Wine Character” / patrones de paladar** (Sommo) | No | Versión ligera: resumen “Tus preferencias” a partir de valoraciones (igual que perfil de gusto) |
| **Ventanas de consumo** (“drink by 2028”) (Vinozo) | No en ficha | Campo opcional en BD + mostrar en ficha y bodega |
| **Seguimiento de precios** (Vinozo) | No | Si tenemos o conseguimos historial de precios: “Precio medio” / “Precio mínimo” por vino |

### Wine-Searcher Pro (B2B / trade)

| Lo que tienen ellos | Nosotros | Acción posible |
|---------------------|----------|----------------|
| **Precisión extrema de añada** (96 %, vintage exacto) | Añada en BD cuando existe; no verificación trade | Para B2B: integrar fuente fiable de añadas o dejar como “referencia profesional” |
| **Datos técnicos trade** (códigos exportación, desgorge, etc.) | No | Solo si hay demanda B2B clara: campos opcionales en ficha “pro” |

---

## 3. App nativa (común a casi todos)

| Lo que tienen ellos | Nosotros | Acción posible |
|---------------------|----------|----------------|
| **App nativa iOS/Android** (cámara en tiempo real, push, mejor UX escaneo) | Web + adaptador (PWA / TWA) | A largo plazo: React Native o Flutter para igualar UX de cámara y notificaciones |

---

## 4. Orden sugerido para “igualar y superar”

1. **Rápido y alto impacto**
   - **Comparador de botellas** (2–4 vinos lado a lado).
   - **“Match for You”** (puntuación de afinidad 0–100 % en ficha, basada en historial/valoraciones).
   - **Perfil de gusto** (pantalla “Tu perfil”: estilos/regiones/uvas más valorados).

2. **Medio**
   - **Listas curatoriales** (listas temáticas: por región, maridaje, tipo).
   - **IA generativa en sumiller** (LLM para respuestas abiertas, sin sustituir reglas para datos).
   - **Ventana de consumo** en ficha y en bodega (“mejor antes de…”).

3. **Más adelante**
   - Reseñas de críticos (si hay API/feed).
   - Cerveza/destilados (si se decide ampliar).
   - App nativa.
   - Seguimiento de precios y datos trade (si hay demanda).

---

## 5. Lo que ya tenemos y muchos no

- Certificaciones (Bio, Vegano, etc.) desde OFF y badges en ficha.
- Noticias de sector (GNews, filtro enológico, idioma).
- Multi-fuente (BD + OFF + Spoonacular + GNews) sin depender de una sola base.
- Comunidad (perfil, seguir, feed, chat, valoraciones, notificaciones).
- Bodega virtual, QR, ofertas, informes, analytics, planes Stripe.
- Experto en vinos (sumiller) con contexto del vino escaneado.
- Maridaje Spoonacular + maridaje en ficha.

Con esto, **quitando base de datos y marca**, el gap es sobre todo: comparador, Match %, perfil de gusto visible, listas curatoriales y (opcional) LLM en sumiller y app nativa. Cerrando esos puntos, estamos técnicamente al nivel o por encima en funcionalidad.
