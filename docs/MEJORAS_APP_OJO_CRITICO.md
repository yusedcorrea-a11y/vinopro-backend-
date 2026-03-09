# Mejoras de la app — Ojo crítico (mientras esperamos permisos Google)

Análisis del backend y flujos de usuario para priorizar qué falta y qué se puede mejorar antes (o justo después) de salir en Play.

---

## 1. Lo que ya está bien

- **Registro y login** con email + contraseña + avatar; sesión y perfil VINEROs creados.
- **Feed** con canales, traducción, spot, slots de publicidad.
- **Chat** con traducción en tiempo real y rutas claras.
- **Menú** con botella CHAT, ☰, enlace "Ver mi perfil".
- **Escaneo** con imagen, cámara, texto y código de barras; mensajes de carga y error en pantalla.
- **Seguridad**: variables de entorno, anonimización IP, rate limiting, ofuscación documentada.
- **Observabilidad**: logger internacional, persistencia visitas_beta.json, CI/CD.

---

## 2. Qué falta o conviene mejorar

### 2.1 Recuperar contraseña

- **Ahora:** No existe "¿Olvidaste tu contraseña?" ni flujo de reset.
- **Riesgo:** Usuarios que pierden acceso y no pueden entrar.
- **Idea:** En `/signup` (formulario de login) añadir enlace "¿Olvidaste tu contraseña?" que lleve a una página (ej. `/recuperar-password`) donde se pide email y se envía un enlace o código por correo (requiere configurar envío de emails, ej. SMTP o SendGrid). Si no quieres montar email aún, al menos enlace "¿Olvidaste tu contraseña? Contacta con soporte: soporte@vinoproia.com".

### 2.2 Feed sin sesión / sin perfil

- **Ahora:** Si la API devuelve 401 o no hay posts, se muestra "feed vacío" y enlace a bodega.
- **Problema:** Quien no tiene cuenta no tiene bodega; el mensaje puede desorientar.
- **Idea:** En el bloque "feed sin perfil" distinguir: (1) "Crea tu perfil para ver el feed" con botón/link a **Registrarse** (`/signup`) y (2) "¿Ya tienes cuenta? Inicia sesión". Mantener también el enlace a bodega para quien sí tiene sesión pero no ha creado perfil.

### 2.3 Páginas de error 404 y 500

- **Ahora:** Las rutas HTML devuelven 404/500 sin una página amigable (FastAPI por defecto).
- **Idea:** Registrar manejadores de excepción en `app.py` para `HTTPException(404)` y para errores 500 que devuelvan HTML (ej. `templates/404.html` y `templates/500.html`) con mensaje claro y enlace a inicio/buscar.

### 2.4 Inicio de sesión desde la home

- **Ahora:** En `/inicio` solo está "Entrar en VINEROs" → `/signup`. Quien ya tiene cuenta debe ir a signup y cambiar al formulario de login.
- **Idea:** En la home añadir una línea tipo "¿Ya tienes cuenta? Iniciar sesión" que lleve a `/signup` (o a `#login` si el login está en la misma página), o exponer una ruta `/login` que muestre solo el formulario de login.

### 2.5 Chat sin sesión: redirigir a registro

- **Ahora:** Al entrar en `/comunidad/chat` sin sesión, el JS muestra "Necesitas perfil para usar el chat".
- **Idea:** Si la API devuelve 401, además del mensaje, mostrar un botón "Registrarme" o "Iniciar sesión" que lleve a `/signup` (y opcionalmente guardar `?next=/comunidad/chat` para redirigir después del login).

### 2.6 Validación de avatar en el registro

- **Ahora:** El backend limita tamaño (5 MB) y tipo de imagen; el front solo tiene `accept="image/..."`.
- **Idea:** En el cliente (signup), comprobar tamaño antes de enviar y mostrar "Máx. 5 MB" junto al input de la foto; si el archivo es demasiado grande, avisar y no enviar el formulario.

### 2.7 Rate limit: mensaje claro al usuario

- **Ahora:** El middleware de rate limit devuelve 429; hay que comprobar si el front (escaneo, feed, etc.) muestra un mensaje legible.
- **Idea:** Asegurar que las respuestas 429 tengan un cuerpo (JSON o HTML) con un texto tipo "Demasiadas peticiones. Espera un momento e inténtalo de nuevo." y que el JS que haga fetch muestre ese mensaje en lugar de un error genérico.

### 2.8 Escaneo: botón "Reintentar"

- **Ahora:** Si el escaneo falla, se muestra el mensaje de error.
- **Idea:** Añadir un botón "Reintentar" o "Escaneo de nuevo" que limpie el error y vuelva a mostrar el formulario/cámara para mejorar la UX tras un fallo.

### 2.9 Google (y Facebook) login

- **Ahora:** Botones "Próximamente" en registro.
- **Idea:** Cuando tengas permisos y tiempo, activar al menos Google (client ID y callback en backend y en la app) para reducir fricción de registro. No bloquea publicación en Play.

### 2.10 Enlace "Privacidad" y cookies

- **Ahora:** En base hay enlace a `/legal` y se menciona privacidad; la política está en `/privacidad`.
- **Idea:** Revisar que en el footer o menú haya un enlace visible a "Privacidad" o "Política de privacidad" (ej. a `/privacidad`) para cumplir con Play y con buenas prácticas. Si usas cookies además de sesión en localStorage, considerar un aviso breve de cookies con enlace a la política.

---

## 3. Prioridad sugerida (mientras esperas Google)

| Prioridad | Mejora | Esfuerzo | Impacto |
|-----------|--------|----------|---------|
| Alta | Feed sin perfil: añadir "Registrarse" / "Iniciar sesión" en el mensaje | Bajo | Alto (no pierdes usuarios en la primera visita al feed) |
| Alta | Página 404 (y si puedes 500) amigable | Bajo | Medio (imagen de calidad) |
| Media | "¿Olvidaste tu contraseña?" → enlace a soporte o página futura | Bajo | Medio (soporte y confianza) |
| Media | Inicio: "¿Ya tienes cuenta? Iniciar sesión" | Bajo | Medio |
| Media | Chat 401: botón "Registrarme" / "Iniciar sesión" | Bajo | Medio |
| Baja | Validación tamaño avatar en front + "Máx. 5 MB" | Bajo | Bajo |
| Baja | Rate limit: mensaje claro en respuestas 429 | Bajo | Medio (si los usuarios llegan al límite) |
| Baja | Escaneo: botón "Reintentar" tras error | Bajo | Bajo |
| Más adelante | Recuperar contraseña con email real | Alto | Alto |
| Más adelante | Login con Google | Medio | Alto |

---

## 4. Resumen

- La base (registro, feed, chat, escaneo, seguridad, observabilidad) está sólida.
- Las mejoras más rentables con poco esfuerzo son: **mensaje del feed sin perfil** (con Registrarse/Iniciar sesión), **404 (y 500) amigables**, **"¿Olvidaste contraseña?"** (aunque sea con enlace a soporte), y **enlace claro a Privacidad**.
- Cuando tengas los permisos de Google, con estos retoques la app quedará más pulida para la revisión y para los primeros usuarios en Play.

Si quieres, el siguiente paso puede ser implementar solo las de prioridad alta (feed sin perfil + 404) y dejarlas listas para commit.
