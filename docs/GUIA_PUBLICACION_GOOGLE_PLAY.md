# Guía completa: Publicar Vino Pro IA en Google Play

Solo instrucciones, sin código. Prioridad: lo urgente primero.

---

# PARTE 1 — TEXTOS PARA LA FICHA

## 1.1 Título de la app (máx. 30 caracteres)

**Usar exactamente:**
```
VINO PRO
```
(9 caracteres. Si quieres más contexto: **VINO PRO – Experto en Vinos** [22 caracteres])

---

## 1.2 Descripción corta / Subtítulo (máx. 80 caracteres)

**Opción recomendada (79 caracteres):**
```
Experto en Vinos en el bolsillo: escanea etiquetas, bodega y comunidad. 14 idiomas.
```

**Alternativa (68 caracteres):**
```
Escanea vinos, gestiona tu bodega y únete a la comunidad. 14 idiomas.
```

---

## 1.3 Descripción larga

Copia y pega este bloque en el campo "Descripción larga" de la ficha:

```
VINO PRO es la herramienta que todo experto en vinos y amante del vino quería: escanear etiquetas al instante, llevar tu bodega personal y formar parte de una comunidad global, todo en una sola app.

🤖 SUMILLER CON IA
Recomendaciones personalizadas sobre vinos, maridajes y preguntas. Respuestas adaptadas a tu nivel.

📷 ESCÁNER DE ETIQUETAS
Enfoca la etiqueta: reconocimiento óptico (OCR) y datos enriquecidos con Open Food Facts. También reconocimiento de voz.

📦 MI BODEGA
Guarda los vinos que has probado, los que quieres probar y tus valoraciones. Organiza tu colección.

👥 COMUNIDAD SOCIAL
Perfiles públicos, feed de actividad, seguir a otros y ver sus reseñas y recomendaciones.

📍 MAPAS
Encuentra restaurantes, vinotecas y bares cerca. Geolocalización o búsqueda por ciudad.

🔗 QR NETWORKING
Comparte tu perfil con un QR personalizado para contactos y eventos de vino.

🌍 14 IDIOMAS
Español, inglés, francés, alemán, italiano, portugués, árabe, ruso, turco, chino, japonés, coreano, hindi y hebreo.

🌓 MODO CLARO Y OSCURO
Adapta la interfaz a tu gusto.

💳 PLAN PRO
Plan Gratis para empezar. Plan PRO con más funciones. Pagos seguros con Stripe; no guardamos datos de tarjeta.

Descarga VINO PRO y lleva el experto en vinos en el bolsillo. Ideal para profesionales, estudiantes y aficionados.
```

---

## 1.4 Categoría sugerida

- **Principal:** **Comida y bebida** (Food & Drink).
- Alternativa si no encaja: **Herramientas** (Tools). Para una app de vinos, Comida y bebida es la más adecuada.

---

## 1.5 Etiquetas / Palabras clave (para ti; Play ya no muestra keywords públicos)

Usa estas ideas en la descripción larga y en el título/descripción corta para que la busquen mejor:

- experto en vinos, wine expert, vino, wine, escáner etiquetas, OCR vino, bodega virtual, maridaje, catas, comunidad vino, vinoteca, restaurante vino, 14 idiomas, IA vino

---

# PARTE 2 — CAPTURAS DE PANTALLA

## Requisitos técnicos de Google

- **Mínimo:** 2 capturas de pantalla (teléfono).
- **Recomendado:** 4–6.
- **Formato:** PNG o JPEG, sin transparencia.
- **Tamaño:** 320–3840 px en el lado más corto (por ejemplo 1080×1920 o similar en 16:9).

## Qué capturar y en qué orden

| Orden | Pantalla | Qué debe verse | Texto opcional (si añades marcos) |
|-------|----------|----------------|-----------------------------------|
| 1 | **Inicio** | Los dos botones principales: Preguntar al experto en vinos y Escanear. Interfaz limpia. | "Tu experto en vinos en el bolsillo" |
| 2 | **Escáner / Escanear** | Pantalla de escaneo (cámara o resultado de un escaneo con datos del vino). | "Escanea etiquetas al instante" |
| 3 | **Mi Bodega** | Lista de vinos en la bodega (o pantalla vacía con mensaje “Añade tu primer vino”). | "Gestiona tu colección" |
| 4 | **Comunidad / Feed** | Feed de actividad o evento (ej. Catas Divertidas). | "Comunidad de amantes del vino" |
| 5 | **Mapa** | Mapa con “Lugares recomendados” o resultados de búsqueda (restaurantes/vinotecas). | "Encuentra lugares cerca" |
| 6 | **Preguntar al experto en vinos** | Pantalla de chat o pregunta con una respuesta del experto en vinos. | "Pregunta lo que quieras" |

## Consejos

- Usa el **modo claro** para la mayoría (o el que mejor se vea).
- Asegúrate de que no salgan datos personales reales ni emails.
- Si añades marcos con texto, que sea breve y en el mismo idioma que la ficha (o el principal del país).

---

# PARTE 3 — FORMULARIO DE SEGURIDAD DE DATOS

En Play Console, en **Política de la app → Seguridad de los datos**, tendrás que declarar qué datos recoges. Respuestas alineadas con tu política de privacidad:

## 3.1 ¿Recopilas o compartes alguno de los datos de los usuarios?

**Respuesta:** Sí.

## 3.2 Datos que SÍ recoges (marcar y describir)

| Tipo de dato | ¿Se recoge? | ¿Se comparte con terceros? | Finalidad (resumen para el formulario) |
|--------------|-------------|----------------------------|----------------------------------------|
| **Identificadores** (ID de sesión / dispositivo) | Sí | No | Identificador anónimo para bodega, valoraciones y preferencias sin cuenta. No identifica a la persona. |
| **Información de la app** (búsquedas, escaneos, uso) | Sí | No (solo agregada/anónima si algo se analiza) | Prestar el servicio y mejorar la app con datos agregados. |
| **Ubicación aproximada** | Sí (si el usuario usa el mapa) | No | Mostrar restaurantes y vinotecas cercanas. Opcional. |
| **Fotos o vídeos** | Sí (foto de etiqueta para escanear) | No | Solo para reconocimiento de texto (OCR) y búsqueda del vino. No se almacenan de forma identificable de forma indefinida. |
| **Información financiera** | No (los pagos los procesa Stripe) | N/A | No recoges ni almacenas datos de tarjeta. Stripe procesa el pago. En el formulario suele preguntarse “¿comparte datos de pago?”: No, el procesador (Stripe) los procesa según su política. |
| **Correo electrónico** | Sí (si usa “Avísame” en web o contacto con oferentes) | No | Avisar cuando la app esté en tienda; poner en contacto compradores y oferentes según la función de la app. |

## 3.3 ¿Los datos se cifran en tránsito?

**Respuesta:** Sí (HTTPS).

## 3.4 ¿Los usuarios pueden solicitar que se eliminen sus datos?

**Respuesta:** Sí. Indicar que pueden contactar por los medios de la app o de la ficha en la tienda para ejercer derechos (acceso, rectificación, supresión, etc.), según tu política de privacidad.

## 3.5 URL de la política de privacidad

**Usar exactamente:**
```
https://vinoproia.com/privacidad
```

## 3.6 Terceros con acceso a datos

- **Stripe:** procesamiento de pagos (no guardas tarjeta; ellos tienen su política).
- **Expo / EAS:** compilación y entrega de la app (datos de build, no de usuarios finales en tiempo de ejecución, según sus términos).
- **Open Food Facts:** consultas para enriquecer datos de vinos (no envías datos personales del usuario).

En el formulario, declara solo los que apliquen a “datos del usuario” (por ejemplo Stripe para “pago” si la pregunta lo menciona). Para “datos que compartes con terceros”, si solo Stripe procesa pago y no les pasas datos personales identificables más allá del necesario para el pago, suele marcarse como “procesamiento de pago” sin listar datos sensibles como tarjeta (porque no los tienes tú).

---

# PARTE 4 — CLASIFICACIÓN DE CONTENIDO

## 4.1 Cuestionario de clasificación (IARC / cuestionario de Play)

- **Edad recomendada:** La app trata sobre vino (contenido de alcohol). Lo habitual es **mayores de 18 años** o la opción que en tu país/cuestionario corresponda a “contenido relacionado con alcohol”. Responde con sinceridad según las preguntas exactas del cuestionario.
- **Contenido generado por usuarios:** **Sí** (comunidad: perfiles, feed, valoraciones, posibles comentarios). En el cuestionario marca que hay UGC y que puede ser moderado/revisado según tu política.
- **Compras dentro de la app:** **Sí** (suscripción Plan PRO, pago con Stripe). Marca “contiene compras dentro de la app” o “suscripciones”.
- **Publicidad:** Marca **Sí** solo si realmente muestras anuncios de terceros en la app. Si no hay anuncios, **No**.

## 4.2 Resumen rápido

| Pregunta | Respuesta |
|----------|-----------|
| ¿Contenido de alcohol? | Sí (información sobre vino). |
| ¿Edad mínima sugerida? | 18+ (o según resultado del cuestionario). |
| ¿Contenido generado por usuarios? | Sí (comunidad). |
| ¿Compras en la app? | Sí (suscripción PRO). |
| ¿Publicidad? | No (salvo que la tengas). |

---

# PARTE 5 — PASOS PARA LA PUBLICACIÓN

## Fase A — Cuenta de desarrollador (si aún no está hecha)

1. Entra en **Google Play Console:** https://play.google.com/console  
2. Inicia sesión con **yusedcorrea@gmail.com**.  
3. Si es la primera vez, acepta los términos del desarrollador.  
4. **Pago único de 25 USD:**  
   - En la consola te llevarán al pago (tarjeta o métodos que Google permita).  
   - Puede tardar hasta 48 h en activarse la cuenta (a veces menos).  
5. Verificación de identidad: si Google la pide, sigue los pasos (documento, etc.).

## Fase B — Crear la app en Play Console

1. En Play Console, **“Crear app”** (o “Create app”).  
2. Rellena:  
   - **Nombre de la app:** VINO PRO (o el título que elegiste).  
   - **Idioma predeterminado:** Español (España) o el principal.  
   - **Tipo:** Aplicación o juego → **Aplicación**.  
   - **Gratuita o de pago:** **Gratuita** (con compras dentro de la app para el Plan PRO).  
3. Declara que cumples las políticas (checkboxes) y crea la app.

## Fase C — Completar la ficha de la tienda (Store listing)

1. En el menú, **“Presencia en Play Store”** (o “Store presence”) → **“Ficha principal de la tienda”** (Main store listing).  
2. Elige el idioma (p. ej. Español – España).  
3. Rellena:  
   - **Nombre de la aplicación:** texto de la sección 1.1.  
   - **Descripción breve:** texto de la sección 1.2.  
   - **Descripción larga:** texto de la sección 1.3.  
4. **Gráficos:**  
   - **Icono de la aplicación:** 512 × 512 px (PNG, sin transparencia).  
   - **Gráfico de función (feature graphic):** 1024 × 500 px.  
   - **Capturas de pantalla:** sube al menos 2 (recomendado 4–6) según la Parte 2.  
5. **Categoría:** Comida y bebida (o la que elegiste).  
6. **Contacto:** email de contacto (ej. el de la cuenta o uno que revises).  
7. **URL de la política de privacidad:** https://vinoproia.com/privacidad  
8. Guarda los cambios.

## Fase D — Seguridad de los datos y contenido

1. **Política de la app** (o “App content”) → **“Seguridad de los datos”**.  
   - Responde el cuestionario con las respuestas de la Parte 3.  
   - Guarda.  
2. **Clasificación de contenido:**  
   - Entra en **“Clasificación de contenido”** y rellena el cuestionario (edad, UGC, compras, publicidad) según la Parte 4.  
   - Guarda.  
3. Si la consola lo pide: **“Público objetivo”** (edad y si va dirigida a niños: No).

## Fase E — Subir el AAB

1. En el menú, **“Producción”** (o “Release” → “Production” / “Production track”).  
2. **“Crear nueva versión”** (o “Create new release”).  
3. **“Subir”** (Upload) y selecciona el archivo **.aab** que descargaste de Expo.  
4. En “Notas de la versión”, escribe algo breve, por ejemplo: “Primera versión. Experto en Vinos IA, escáner, bodega, comunidad y mapas.”  
5. **Revisar versión** y, si todo está bien, **“Iniciar rollout para producción”** (o “Start rollout to production”).

## Fase F — Revisión de Google

- La **primera revisión** suele tardar **varios días** (1–7 o más, según carga).  
- Si rechazan la app, te llegarán un **email y un mensaje en la consola** con el motivo. Corrige lo que indiquen y vuelve a enviar.  
- Cuando esté **aprobada**, la app quedará **publicada** en la ficha que configuraste (países y dispositivos que hayas elegido).

## Orden recomendado (resumen)

1. Pagar 25 USD y tener la cuenta activa.  
2. Crear la app y rellenar la ficha (textos + icono + feature graphic + capturas).  
3. Añadir URL de privacidad y completar Seguridad de los datos y Clasificación de contenido.  
4. Subir el AAB a producción e iniciar el rollout.  
5. Esperar la revisión y responder a cualquier solicitud de Google.

---

**Última actualización:** Febrero 2026.  
Si algo no coincide con lo que ves en Play Console (nombres de menús o preguntas), adapta estos pasos al texto exacto de la consola; la lógica es la misma.
