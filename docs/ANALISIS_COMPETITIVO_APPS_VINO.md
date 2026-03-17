# Análisis competitivo: VINO PRO IA vs otras apps de vino

**Fecha:** Marzo 2025  
**Objetivo:** Situar a VINO PRO IA en el mapa de apps de escaneo y asesoría enológica.

---

## 1. Competidores principales

| App | Tipo | Usuarios / Alcance | Escaneo | Base de datos | Maridaje / IA | Precio |
|-----|------|---------------------|---------|----------------|----------------|--------|
| **Vivino** | Consumidor masivo | 65–70 M usuarios, 16 M+ vinos | Sí, muy usado | 16 M vinos, 245k bodegas | Valoraciones, reseñas, maridaje | Freemium + compras |
| **Delectable** | Consumidor / pro | Menor que Vivino | Sí, OCR potente | ~8 M etiquetas | Reseñas críticos (Vinous), listas | Freemium, Premium ~8 €/mes |
| **Vinora** | Indie / IA | Nicho | Escaneo con IA | Celular digital, preferencias | IA sommelier, maridaje, perfiles | Freemium |
| **Vinozo** | Indie / IA | Nicho | Escaneo IA | Bodega personal, ventanas de consumo | IA, maridaje, precios | Freemium |
| **Sommo** | Indie / formación | Nicho | Escaneo + WSET | Diario personal | Notas WSET, “Wine Character” | Freemium |
| **WineIQ** | Indie | Solo iOS | Escaneo rápido | Bodega propia | Recomendaciones por lo que tienes | Freemium |
| **Wine-Searcher Pro** | B2B / trade | Profesionales | No es el foco | Máxima precisión de añada | Datos técnicos (desgorge, códigos) | Suscripción pro |

---

## 2. Comparativa de capacidades

### Escaneo e identificación
- **Vivino / Delectable:** Bases propias enormes; identificación sobre todo por imagen/etiqueta. Vivino ~89 % detección; Delectable destaca en OCR difícil (texto borroso, relieve).
- **VINO PRO IA:** OCR (Gemini cuando aplica) + **código de barras** (EAN) con **Open Food Facts** y BD local (JSON). Identificación por texto, imagen o EAN. Menos volumen que los gigantes, pero **multi-fuente** (local + OFF) sin depender de una sola API cerrada.

### Base de datos y fuentes
- **Grandes:** Una sola base propietaria (Vivino, Delectable).
- **VINO PRO IA:** Catálogo propio (data/*.json) + **Open Food Facts** (abierta, sin API key). Enriquecimiento con certificaciones (Bio, Vegano, etc.) desde OFF. Posibilidad de sumar más fuentes abiertas o APIs con clave (ej. GNews, Spoonacular).

### Maridaje y “experto”
- **Vivino / Delectable:** Maridaje y recomendaciones basadas en su propia base y valoraciones.
- **Vinora / Vinozo / Sommo / WineIQ:** IA/sommelier, maridaje y notas de cata.
- **VINO PRO IA:** Maridaje en ficha desde **Spoonacular** (vino → platos; opcional plato → vinos) + maridaje estático en fichas de BD. Experto en vinos (sumiller) por sesión con reglas + contexto sobre el vino escaneado.

### Certificaciones y sellos (Bio, Vegano, etc.)
- La mayoría de apps no muestran explícitamente etiquetas OFF (Bio, Vegano, Sin gluten).
- **VINO PRO IA:** **Badges en ficha** a partir de OFF (`certificaciones`) e información extendida por EAN cuando el vino viene de BD local. Diferenciador claro para usuario que busca sostenibilidad o dieta.

### Noticias y contenido
- **VINO PRO IA:** Canal de noticias con **GNews** (filtro enológico, `lang=es`), sección VINEROs. Pocos competidores integran noticias de sector en la misma app.

### B2B / profesional
- **Wine-Searcher Pro:** Referente en trade (precisión añada, códigos exportación).
- **VINO PRO IA:** Enfoque en bodega virtual, QR, escaneos, informes, comunidad y (en roadmap) uso en punto de venta o hostelería. No compite con Wine-Searcher en datos de trade; sí en **herramienta todo-en-uno** para quien quiere escanear, preguntar, maridaje y contenido.

---

## 3. Dónde estamos nosotros (VINO PRO IA)

### Fortalezas
- **Multi-fuente:** BD local + Open Food Facts + Spoonacular + GNews. No dependemos de una sola base cerrada.
- **Sin bloqueo por una API:** OFF sin clave; GNews y Spoonacular con clave; flujo que degrada bien si falta una (fallbacks, mensajes claros).
- **Ficha “pro” en un solo lugar:** Descripción, notas, maridaje (BD + Spoonacular), **badges Bio/Vegano**, noticias, experto en vinos y exportación a PDF.
- **Idiomas y accesibilidad:** Multiidioma (p. ej. 14 idiomas en textos); posibilidad de enfatizar accesibilidad como valor.
- **Enfoque español/latino:** Noticias y contenido en español; maridaje y descripciones pensados para nuestro mercado.

### Debilidades vs competencia
- **Tamaño de catálogo:** Muy por debajo de Vivino/Delectable (miles vs millones de referencias). Mitigado por OFF cuando el producto tiene EAN.
- **Marca y distribución:** Sin presupuesto de marketing ni presencia en tiendas; competidores con app store optimization y partnerships.
- **App nativa:** Hoy web/adaptador; competidores con apps nativas iOS/Android (mejor cámara y UX de escaneo).

### Nicho en el que encajamos
- **Profesional / semi-pro / aficionado exigente:** Quien quiere ficha técnica, maridaje fiable, certificaciones y noticias en un solo sitio.
- **Proyecto “indie” con stack moderno:** Backend claro (FastAPI), APIs bien acotadas, integración de servicios externos y documentación (ej. revisión OFF/GWS, análisis como este). Útil para portfolio y entrevistas (ej. Ayesa).
- **MVP con margen de crecimiento:** Escaneo (imagen + EAN), experto, maridaje Spoonacular, badges OFF, noticias GNews y flujo de compra/registro ya montados. Siguiente paso: más fuentes, más datos por EAN, o app nativa.

---

## 4. Resumen: posición relativa

| Dimensión | Líderes (Vivino, Delectable) | Indie IA (Vinora, Vinozo, Sommo) | VINO PRO IA |
|-----------|------------------------------|-----------------------------------|-------------|
| Tamaño base de datos | Muy alto | Medio / bajo | Bajo (local) + OFF (alto por EAN) |
| Calidad escaneo/OCR | Muy alta | Alta | Buena (OCR + EAN + OFF) |
| Maridaje | Integrado | IA/sommelier | Spoonacular + BD |
| Certificaciones (Bio/Vegano) | Poco o nada | Poco o nada | **Sí (OFF + badges)** |
| Noticias de sector | No típico | No típico | **Sí (GNews)** |
| Multi-fuente / APIs abiertas | No | Parcial | **Sí** |
| Experto / chatbot vino | Limitado | IA | Reglas + contexto |
| B2B / bodega virtual / QR | No prioritario | Algunos | **Sí** |
| Coste para el usuario | Freemium | Freemium | Freemium / Premium |

**En una frase:** VINO PRO IA está en un **nicho intermedio**: más completo en ficha técnica, certificaciones y noticias que muchas apps indie; más pequeño en catálogo y marca que Vivino/Delectable, pero con arquitectura multi-fuente y enfoque profesional/indie que permite crecer sin depender de una sola base propietaria.

---

## 5. Próximos pasos sugeridos (producto)

- **Mantener y documentar** las integraciones actuales (OFF, Spoonacular, GNews) como argumento de “integración de múltiples fuentes”.
- **Medir** tasas de acierto por EAN vs por OCR para priorizar mejoras (más productos con EAN en BD local, o más refinamiento de OFF).
- **Valorar** app nativa (React Native / Flutter) para mejorar escaneo con cámara y notificaciones.
- **No priorizar** scraping o fuentes no oficiales (ej. Global Wine Score sin API); mantener fuentes con términos de uso claros.
