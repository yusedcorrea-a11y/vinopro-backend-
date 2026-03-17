# Resumen de lo hecho hasta ahora y próximos pasos

## 1. Chat Vineros (completado)

- **Diseño tipo WhatsApp**: burbujas (tuyas en burdeos, del otro en gris), fondo que transmite calma/seguridad, barra de escritura abajo con input y botón circular de enviar.
- **“Conversación privada”**: texto con candado en el header del hilo, traducido en 14 idiomas.
- **Barra de escritura**: estilo WhatsApp con toque VINO PRO (wrapper, focus burdeos/dorado, safe-area en móvil).
- **Saltos de línea**: los mensajes con varias líneas se muestran correctamente (\\n → &lt;br&gt;).
- **Lista de conversaciones**: se muestra hora relativa del último mensaje (Hace X min, Ayer, Hoy, etc.).
- **Estado vacío**: si no hay mensajes con ese usuario, se muestra “Envía un mensaje para empezar la conversación”.
- **i18n en JS**: errores y botones (Registrarme, Iniciar sesión, Usuario no encontrado, etc.) usan traducciones desde el servidor (ES, EN, FR, DE, PT, IT y fallback).

---

## 2. Onboarding (completado)

- **Paso 1 – Ubicación**: primera pantalla pide permiso de ubicación; el texto está en el idioma del navegador (Accept-Language).
- **Paso 2 – Idioma**: el usuario elige idioma de la app (14 idiomas); se guarda en cookie y se preselecciona el idioma actual.
- **Paso 3 – Registro**: pantalla “Crea tu cuenta” con botón que lleva a /signup; al pulsar se marca onboarding como hecho y se redirige a registro.
- **Cookies**: `vino_pro_onboarding_done` (al completar paso 3), `vino_pro_lang` (en paso 2).
- **Redirección**: si no tiene onboarding hecho, / y /inicio redirigen a /onboarding. Modal de idioma y age gate no se muestran en /onboarding.
- **Detalles**: safe-area móvil, focus visible, estilos modo oscuro.

---

## 3. Monetización futura (subido a repo)

- Archivos incluidos en commit: `.env.example`, `docs/AFILIADOS_TIENDAS.md`, `services/enlaces_service.py`.
- Base para futura monetización (afiliados, tiendas, enlaces).

---

## 4. Plan gratuito – Canales de noticias Vineros (completado)

- **Fuentes gratuitas** añadidas en `data/canales_feed.json` (array `noticias`):
  - **Vinetur**: 5 entradas (noticias, guías, publicar notas de cata, DO, bodegas y cosechas).
  - **Wine News TV**: 2 entradas (vídeos y lives en YouTube).
  - **Colectivo Decantado**: 2 entradas (canal YouTube).
  - **Diario de Jerez / Jerez Televisión**: 2 entradas (sección vino y portada).
- Sin API de pago: cuando no hay GNEWS_API_KEY, el feed usa este contenido estático.
- Las nuevas entradas tienen `created_at` más reciente para aparecer primero en el feed.

---

## 5. Commits y push realizados

- Commit chat (diseño WhatsApp, fondo, barra, traducción “Conversación privada”).
- Commit onboarding + mejoras chat (i18n JS, hora en lista, estado vacío, safe-area).
- Commit monetización futura (afiliados/tiendas, enlaces_service, .env.example).
- Los canales nuevos (Vinetur, YouTube, Jerez) están en el repo pero aún no se ha hecho commit específico de `canales_feed.json` si quieres subirlo en el siguiente.

---

## 6. Próximos pasos propuestos

### 6.1 Cristalería e implementos para el vino experto (nuevo)

**Objetivo:** Añadir enlaces de venta de cristalería e implementos (copas, decantadores, sacacorchos, termómetros, etc.) para que el usuario experto o aficionado pueda encontrar dónde comprar.

**Opciones:**

- **A) Nuevo canal en el feed**  
  Crear en `canales_feed.json` una sección nueva, por ejemplo `"equipamiento"` o `"cristalería"`, con entradas tipo:
  - titulo, descripcion, link (tienda o categoría), fuente (Amazon, Vinum, etc.), badge "Equipamiento" o "Comprar".
  - El feed o una pestaña “Equipamiento” / “Para tu bar” mostraría estos enlaces.

- **B) Dentro de “noticias”**  
  Añadir entradas en `noticias` con fuente “Cristalería”, “Equipamiento”, etc., y enlace a tiendas o guías de compra. Menos cambios en código; mismo formato que ahora.

- **C) Sección dedicada en la app**  
  Una página o bloque “Para el experto” (cristalería, implementos, libros) que liste enlaces a tiendas afiliadas o recomendadas. Reutilizaría la lógica de enlaces/afiliados que ya tienes.

**Recomendación:** Empezar por **B** (entradas en noticias con badge “Equipamiento” o “Comprar”) o **A** (canal `equipamiento` en canales_feed y mostrarlo en el feed junto a noticias/eventos/enoturismo). Si más adelante quieres afiliados (Amazon, Vinum, etc.), esos enlaces pueden ser los de afiliado.

### 6.2 Otras tareas posibles

- **Commit** de `canales_feed.json` (nuevos canales Vinetur, YouTube, Jerez).
- **Fase 2 plan gratuito**: si Vinetur o YouTube ofrecen RSS/API, automatizar la actualización de noticias/vídeos.
- **Traducciones**: añadir las nuevas claves de chat (error_perfil, hace_min, etc.) en los idiomas que aún usan fallback (ru, tr, zh, ja, ko, hi, ar, he) si quieres que todo esté traducido.

---

## Resumen ejecutivo

| Área           | Estado   | Descripción breve                                              |
|----------------|----------|----------------------------------------------------------------|
| Chat           | Hecho    | Estilo WhatsApp, i18n, hora en lista, vacío, safe-area        |
| Onboarding     | Hecho    | 3 pasos: ubicación → idioma → registro                        |
| Monetización   | En repo  | Afiliados/tiendas, enlaces_service, .env.example              |
| Canales Vineros| Hecho    | Vinetur, Wine News TV, Colectivo Decantado, Jerez en noticias |
| Cristalería/implementos | Pendiente | Definir: canal nuevo o entradas en noticias + enlaces venta |

Cuando definamos cómo quieres que se vea (solo enlaces en noticias vs canal “Equipamiento” vs página “Para el experto”), se puede bajar a cambios concretos en `canales_feed.json` y en el front del feed.
