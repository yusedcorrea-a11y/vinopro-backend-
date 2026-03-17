# Cómo funciona cada función de la app (resumen sin tecnicismos)

Resumen de **todas** las funciones: qué hace cada una y dónde se usa (app móvil, web o ambos).

---

## 1. ESCANEO DE VINOS

| Función | Qué hace |
|--------|----------|
| **Escanear con cámara (código de barras o QR)** | La app abre la cámara; cuando detecta un código, lo envía al servidor. El servidor busca ese código en base de datos o en fuentes externas y devuelve el vino (nombre, bodega, tipo, etc.) o un mensaje si no lo encuentra. |
| **Escanear con foto (imagen de la etiqueta)** | El usuario hace una foto o elige una de la galería. La app envía la imagen al servidor. El servidor lee códigos de barras/QR en la imagen y también el texto de la etiqueta (OCR); con eso busca el vino en su base o en línea y responde. |
| **Buscar por texto (nombre del vino)** | Si la imagen no se reconoce, el usuario puede escribir el nombre del vino y pulsar “Buscar”. El servidor busca por ese texto y devuelve el vino si lo encuentra. |
| **Historial de escaneos** | El servidor guarda los últimos escaneos de cada sesión (por identificador de usuario). Se puede pedir ese historial para mostrarlo en la app o en la web. |
| **Registrar vino (alta manual)** | Permite dar de alta un vino que no está en la base (por ejemplo uno nuevo o muy local). Se usa desde la web; la app no lo usa por ahora. |

---

## 2. SUMILLER (EXPERTO EN VINOS)

| Función | Qué hace |
|--------|----------|
| **Preguntar al sumiller (chat)** | El usuario escribe una pregunta (maridajes, recomendaciones, dudas). El servidor responde con texto: si acabas de escanear un vino, responde sobre ese; si no, da recomendaciones o maridajes según lo que escribas y recuerda un poco el contexto de la conversación (mismo usuario/sesión). |
| **Preguntar sobre un vino escaneado** | Tras escanear, en la pantalla de resultado hay un campo para preguntar por ese vino. La app envía la pregunta junto con el “consulta_id” del escaneo; el servidor responde solo sobre ese vino (maridaje, temperatura, etc.). |
| **Ficha del sumiller (API)** | Devuelve datos para mostrar la “ficha” del experto (nombre, descripción, etc.) en la web o en futuras pantallas. |
| **Feedback del vino (me gusta / no me gusta)** | El usuario puede valorar si la recomendación del sumiller le gustó. El servidor guarda ese dato para mejorar o personalizar en el futuro. Se usa sobre todo en la web. |

---

## 3. MI BODEGA

| Función | Qué hace |
|--------|----------|
| **Ver mi bodega** | Lista todas las botellas que el usuario ha guardado. Cada una tiene nombre, cantidad y datos que se hayan guardado. El servidor asocia las botellas al identificador de sesión (X-Session-ID). |
| **Añadir botella** | Añade una botella a la bodega (nombre del vino y cantidad). El servidor valida el nombre, aplica el límite del plan (gratis tiene tope; PRO no) y la guarda. Se puede añadir desde la pantalla “Añadir botella” o desde el resultado de un escaneo (“Añadir a mi bodega”). |
| **Eliminar botella** | Quita una botella de la bodega por su id. |
| **Editar botella** | Permite cambiar cantidad u otros datos de una botella ya guardada (API PUT). La app móvil no muestra por ahora esta opción. |
| **Registros de hoy** | Indica cuántas veces ha “registrado” algo hoy el usuario (límite diario si existe). Sirve para mostrar un contador o aviso en la interfaz. |
| **Alertas de bodega** | El servidor puede devolver avisos (por ejemplo “te queda poco de X” o “caducidad”). La app puede mostrarlos si los usa. |
| **Valoración de bodega** | Endpoint para obtener o gestionar la valoración global de la bodega del usuario. |
| **Stock de bodega** | Pensado para que un restaurante o integrador consulte el “stock” de una bodega usando un token (X-API-Token). La app de usuario usa solo X-Session-ID. |

---

## 4. FEED Y COMUNIDAD

| Función | Qué hace |
|--------|----------|
| **Feed (para_ti / noticias / eventos / etc.)** | Devuelve una lista de “posts”: noticias con imagen, actividad de usuarios (valoró X, probó Y, quiere Z) y eventos. La app muestra el canal “para_ti” en la sección Comunidad con imágenes a ancho completo y texto debajo. |
| **Noticias** | Canal solo de noticias de vino (titular, descripción, imagen, enlace). El feed puede mezclar estas noticias con el resto. |
| **Crear perfil** | El usuario puede crear un perfil público (nombre, bio, etc.) para la parte social. La app tiene “Mi perfil” en Más pero está como “Próximamente”. |
| **Ver / editar mi perfil** | Ver o actualizar los datos del perfil del usuario que tiene la sesión. |
| **Ver perfil de otro usuario** | Ver el perfil público de otro usuario por su nombre de usuario. |
| **Seguir / dejar de seguir** | Seguir o dejar de seguir a otro usuario. Afecta al feed “para_ti” (actividad de los que sigues). |
| **Lista de seguidores / seguidos** | Devuelve quién te sigue y a quién sigues. |
| **Conversaciones / chat** | Lista de conversaciones y mensajes con otros usuarios. En la web hay chat; en la app está previsto para más adelante. |
| **Traducir texto / comentario** | Traduce un texto o un comentario al idioma del usuario (comunidad sin barrera de idioma). |
| **Notificaciones** | Lista de notificaciones del usuario (likes, nuevos seguidores, etc.). Marcar como leídas. |
| **Valoraciones y actividad de un perfil** | Ver las valoraciones públicas y la actividad (probado, valorado, deseados) de un usuario. |

---

## 5. MAPA Y LUGARES

| Función | Qué hace |
|--------|----------|
| **Lugares destacados** | Lista de sitios recomendados (partners: bares, vinotecas, restaurantes) con nombre, dirección, descripción, teléfono, email, coordenadas. La app en la pestaña “Mapa” llama a esta función y muestra las tarjetas; “Ver ruta” abre Google Maps con el destino. |
| **Lugares cerca (por coordenadas o ciudad)** | Busca sitios cerca de un punto (lat/lon) o de una ciudad (geocodifica y luego busca). Devuelve lista de lugares en ese radio. La web lo usa; la app podría usarlo para “cerca de mí”. |
| **Geocode** | Dado un nombre de ciudad o dirección, devuelve coordenadas (lat, lon). Sirve para buscar “lugares cerca” por ciudad. |

---

## 6. PLANES Y LÍMITES

| Función | Qué hace |
|--------|----------|
| **Comprobar límite (check-limit)** | Indica si el usuario ha llegado al límite de su plan (por ejemplo número de botellas en bodega o de escaneos). La web o la app pueden usarlo para mostrar “pásate a PRO”. |
| **Páginas de planes** | La web tiene páginas que explican planes Gratis y PRO. La app en “Más” tiene “Planes PRO” como “Próximamente”. |

---

## 7. PAGOS (STRIPE)

| Función | Qué hace |
|--------|----------|
| **Crear sesión de pago (checkout)** | El usuario elige plan PRO; el servidor crea una sesión de Stripe y devuelve la URL para ir a pagar. El usuario paga en la página de Stripe. |
| **Pago exitoso / cancelado** | Páginas a las que Stripe redirige tras pagar o cancelar. El servidor puede registrar que el usuario ya es PRO. |
| **Webhook de Stripe** | Stripe avisa al servidor cuando un pago se completa; el servidor actualiza el estado del usuario (por ejemplo a PRO). |

---

## 8. AUTH (REGISTRO Y LOGIN)

| Función | Qué hace |
|--------|----------|
| **Registro** | Crear cuenta (email, contraseña, etc.). El servidor guarda el usuario. |
| **Login** | Iniciar sesión; el servidor devuelve un token o confirma la sesión. |
| **Eliminar cuenta** | Solicitar borrado de cuenta y datos. Hay página en la web para cumplir con Google Play; el servidor procesa la baja. |

La app móvil hoy usa solo un **identificador de sesión** (X-Session-ID) generado en el dispositivo; no obliga a registrarse para escanear, sumiller o bodega.

---

## 9. VALORACIONES Y WISHLIST

| Función | Qué hace |
|--------|----------|
| **Valorar vino** | Enviar una valoración (puntuación, comentario) de un vino. Se usa en la web y en flujos de comunidad. |
| **Ver valoraciones de un vino** | Listar las valoraciones públicas de un vino por su id. |
| **Añadir a wishlist** | Añadir un vino a “quiero probarlo”. |
| **Quitar de wishlist** | Quitar un vino de la wishlist. |
| **¿Está en wishlist?** | Comprobar si un vino está en la wishlist del usuario. |
| **Listar wishlist** | Devolver toda la wishlist del usuario. |
| **Editar / eliminar valoración** | Modificar o borrar una valoración ya hecha. |

La app muestra “Valoraciones” en Más como “Próximamente”.

---

## 10. INFORMES

| Función | Qué hace |
|--------|----------|
| **Informe de bodega (PDF)** | Genera un PDF con el contenido de la bodega del usuario. La app tiene botón “Exportar PDF” que avisa que en la versión web se puede descargar; la petición va a este endpoint. |
| **Informe de cata** | Crear o generar un informe de cata (por ejemplo notas, puntuación). Se usa desde la web. |

---

## 11. COMPRAR Y ENLACES

| Función | Qué hace |
|--------|----------|
| **Página “Comprar” por vino** | Página web que muestra opciones para comprar ese vino (enlaces a tiendas, etc.). |
| **Enlaces de compra de un vino** | API que devuelve enlaces donde se puede comprar el vino (por id o clave). La app puede mostrar “Buscar en Vivino” u otros enlaces tras el escaneo. |

---

## 12. OFERTAS (PREMIUM)

| Función | Qué hace |
|--------|----------|
| **Listar ofertas** | Ver ofertas creadas (por ejemplo “vendo/intercambio este vino”). |
| **Crear oferta** | Un usuario Premium crea una oferta (foto, texto, email). |
| **Contactar por oferta** | Enviar solicitud de contacto al creador de la oferta. |
| **Mis ofertas** | Listar las ofertas que ha creado el usuario. |
| **Marcar oferta como respondida** | Marcar que ya se respondió a los contactos. |
| **Eliminar oferta** | Borrar una oferta. |
| **Ver imagen de oferta** | Servir la imagen subida de una oferta (ruta de uploads). |

Esto está más orientado a la web; la app no tiene pantallas de ofertas por ahora.

---

## 13. QR Y CONTACTOS

| Función | Qué hace |
|--------|----------|
| **Página corta /c/{codigo}** | Redirige a un perfil o recurso según un código corto (para compartir “mi perfil” o un vino). |
| **Página de generación de QR** | Página web para generar un QR (por ejemplo con enlace a perfil o a un vino). |
| **Listar contactos (QR)** | Lista de contactos guardados para el QR (tarjetas de visita, etc.). |
| **Generar QR** | Genera un código QR con la URL o datos que indiques. |
| **Descargar QR** | Devuelve la imagen del QR para descargar. |

Uso principal en la web.

---

## 14. ADAPTADOR (RESTAURANTES / INTEGRADORES)

| Función | Qué hace |
|--------|----------|
| **Obtener token** | Un restaurante o integrador obtiene un token para usar la API (por ejemplo para consultar bodega/stock). |
| **Regenerar token** | Generar un nuevo token e invalidar el anterior. |
| **Configurar** | Enviar configuración del integrador (webhook, etc.). |
| **Probar webhook** | Probar que el webhook del integrador responde. |
| **Registrar venta** | Notificar una venta (por ejemplo “se vendió esta botella”); el servidor puede actualizar stock o analytics. |

No es para el usuario final de la app; es para negocios que integran con VINO PRO.

---

## 15. PAIRING (MARIDAJES POR API)

| Función | Qué hace |
|--------|----------|
| **Platos** | Lista de platos para maridaje (API para integradores o web). |
| **Vinos** | Lista de vinos para maridaje. |
| **Descripción de vino** | Descripción de un vino por id. |

Sirve para pantallas de “maridaje” o integraciones; la app de usuario usa sobre todo “preguntar al sumiller”.

---

## 16. ANALYTICS (INTERNO)

| Función | Qué hace |
|--------|----------|
| **Dashboard** | Resumen de uso (peticiones, escaneos, etc.) para administración. |
| **Tendencias** | Datos de tendencias de uso. |
| **Por país** | Uso por país. |
| **Preguntas frecuentes** | Estadísticas de preguntas más repetidas al sumiller. |

Uso interno o panel de administración; no es una pantalla de la app móvil.

---

## 17. OTROS ENDPOINTS Y PÁGINAS

| Función | Qué hace |
|--------|----------|
| **Health / Ready** | Comprueban que el servidor está vivo y con datos cargados (para monitoreo o balanceadores). |
| **Estado del API (/api/status)** | Devuelve versión, número de vinos cargados, uptime, límites de uso. Para soporte o clientes programáticos. |
| **Vino por consulta_id** | Dado un consulta_id de un escaneo, devuelve el vino asociado (para agentes o integraciones). |
| **Preguntar local (agente)** | Envía la pregunta a un “agente” local (otro servicio) para respuestas más avanzadas; si no responde, el servidor usa la lógica normal. Pensado para usuarios Premium. |
| **Landing: aviso Google Play** | En la web, el usuario deja su email para que le avisen cuando la app esté en Google Play; el servidor guarda el email. |
| **Páginas HTML (inicio, escanear, bodega, mapa, signup, legal, privacidad, eliminar cuenta, etc.)** | El servidor también sirve la versión web: cada ruta devuelve una página HTML (inicio, escanear, bodega, mapa, registro, legal, privacidad, eliminación de cuenta, etc.). |

---

## Resumen por “dónde lo ves”

- **App móvil (lo que usa hoy):** escanear (cámara, foto, texto), preguntar al sumiller, ver/añadir/eliminar bodega, feed Comunidad, lugares destacados en Mapa, enlace a informe PDF de bodega. El resto (auth, ofertas, valoraciones, wishlist, pagos, informes de cata, QR, adaptador, analytics, etc.) está en la web o preparado para futuras pantallas (“Próximamente”).

Si quieres, en el siguiente paso podemos bajar al detalle de **una sola función** (por ejemplo solo “Escanear” o solo “Mi Bodega”) y te explico paso a paso qué hace la app y qué hace el servidor.
