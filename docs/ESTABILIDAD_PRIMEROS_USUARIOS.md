# Estabilidad al inicio: buena impresión para los primeros usuarios

**Objetivo:** Que los primeros usuarios que entren desde Google Play tengan una experiencia estable y clara, sin pantallas en blanco ni errores que no entiendan. Plan para revisar/afinar mañana.

---

## 1. Qué ya tenemos cubierto

| Área | Qué hace la app |
|------|------------------|
| **Cold start (Render plan gratis)** | Tras ~15 min sin uso el servidor se duerme; la primera petición puede tardar **50–60 s**. |
| **Aviso "sin conexión"** | En `base.html` se hace `GET /api/status` con timeout **12 s**. Si falla (servidor dormido o red), se muestra un banner: *"No se pudo conectar al servidor. Comprueba la WiFi o que la URL sea correcta. Si es la primera vez, espera hasta 1 min."* + botón **Reintentar**. |
| **Registro e inicio de sesión** | Timeout **90 s** y mensaje *"Conectando… En plan gratuito la primera vez puede tardar hasta 1 minuto"*. Si hay timeout: *"El servidor está despertando. Espera unos segundos y vuelve a pulsar"*. |
| **Errores de IA (cuota / 429)** | En visión y sumiller se captura 429/quota y se muestra mensaje tipo *"Límite de uso de la IA alcanzado. Espera un minuto o escribe el nombre del vino abajo"*. |
| **Feed / Chat** | Tienen estados de carga (*"Cargando noticias de vino…"*, *"Cargando conversaciones…"*) y mensajes de error o vacío. |
| **Health** | `/health`, `/ready` y `/api/status` para monitoreo y para que el cliente sepa si el backend responde. |

Con esto la app **no se cae** ante cold start ni cuota; el usuario recibe mensajes entendibles y puede reintentar.

---

## 2. Dónde puede fallar la primera impresión

1. **Primera apertura en frío:** El usuario abre la app → la **primera** petición es la propia carga de la página (HTML). Esa la sirve Render cuando despierte. Si abren directo una URL que hace una petición API (ej. feed), esa petición puede tardar 50–60 s. Hoy el aviso solo sale si **`/api/status`** falla tras 12 s; si la página no hace ese fetch antes que otras acciones, el usuario podría tocar "Feed" o "Chat" y quedarse esperando sin mensaje claro.
2. **Timeout de 12 s vs cold start de 50 s:** Si **solo** hacemos ping a `/api/status` con 12 s, a los 12 s mostramos "No se pudo conectar" y "Reintentar". El servidor podría estar despertando y responder a los 50 s. Es decir: damos por perdida la conexión antes de que el cold start termine.
3. **Sin indicador de "conectando" al cargar:** En la primera carga no mostramos un "Conectando…" o spinner global; el usuario ve la página estática. Si el backend tarda, no hay feedback hasta que aparece el banner a los 12 s.

---

## 3. Qué añadir o afinar (para mañana)

### A. Rápido y muy efectivo (recomendado)

- **Dar una oportunidad al cold start en la primera carga**  
  - En `base.html`, donde se hace `fetch('/api/status')`, subir el timeout de **12 s a 55–60 s** solo para **la primera** petición de la sesión (por ejemplo guardar en `sessionStorage` que ya hicimos el primer intento; el primero 60 s, los siguientes 12 s).  
  - Así: primera vez que abren la app, esperamos hasta ~60 s; si responde, todo bien; si no, mostramos el banner "No se pudo conectar… Espera hasta 1 min" + Reintentar. No cortamos a los 12 s cuando el servidor podría despertar a los 50.

- **Mensaje claro mientras esperamos**  
  - Mostrar un pequeño texto o spinner tipo *"Conectando con VINO PRO…"* en la parte superior (o encima del contenido) **desde** que se hace el primer `fetch('/api/status')` **hasta** que responde OK o falla. Ocultarlo cuando `status === 'ok'` o cuando se muestre el banner de error. Así el usuario no cree que la app está colgada.

- **Revisar que el aviso se vea bien en móvil**  
  - El banner `.aviso-sin-conexion` está abajo, fijo. Comprobar que en pantalla pequeña se lee bien y que el botón "Reintentar" es fácil de pulsar.

### B. Muy recomendable (poco esfuerzo)

- **UptimeRobot (gratis)**  
  - Crear un monitor que haga **GET** a `https://vinopro-backend-1.onrender.com/api/status` (o `/health`) **cada 14 minutos**. Así la instancia de Render se despierta sola y muchos usuarios no llegarán a vivir un cold start de 50 s.

- **Checklist de “primer usuario”**  
  - Antes de dar por cerrado, probar una vez con el servidor **dormido** (sin abrir la app 15+ min):  
    1. Abrir la app (o la URL de la web) y esperar hasta 1 min.  
    2. Comprobar que aparece "Conectando…" o el banner con "espera hasta 1 min" + Reintentar.  
    3. Pulsar Reintentar tras ~1 min y ver que entra.  
    4. Registrar / Iniciar sesión (mensaje de “puede tardar hasta 1 min”).  
    5. Abrir Feed, Chat, Escanear y comprobar que no haya pantallas en blanco sin mensaje.

### C. Opcional (si da tiempo)

- **Página de inicio (/ o /inicio)**  
  - Si la primera pantalla hace alguna petición API al cargar, asegurar que tenga estado de carga y, si hay timeout, mensaje tipo "La app se está despertando. Espera un momento y vuelve a intentar."

- **Un solo punto de “warmup”**  
  - Que la única petición que usamos para “¿está vivo?” sea `/api/status` (o `/health`) y que todas las pantallas que dependan del backend muestren un estado de carga hasta tener respuesta (o el banner si falla). Así evitamos que el usuario toque algo y se quede sin feedback.

---

## 4. Resumen para mañana

| Prioridad | Acción | Efecto |
|-----------|--------|--------|
| 1 | Subir timeout del **primer** `/api/status` a **55–60 s** y dejar los siguientes en 12 s | No cortar la conexión antes de que termine el cold start. |
| 2 | Mostrar **"Conectando con VINO PRO…"** (o spinner) hasta que `/api/status` responda o falle | Primera impresión clara: el usuario sabe que está cargando. |
| 3 | Configurar **UptimeRobot** (ping cada 14 min a `/api/status` o `/health`) | Menos cold starts para los primeros usuarios. |
| 4 | Probar **una vez en frío** el flujo: abrir app → esperar/reintentar → registro → feed/chat/escanear | Confirmar que no hay pantallas en blanco ni mensajes confusos. |

Con esto los primeros usuarios tendrán una app que se siente **estable al inicio**: mensajes claros, una oportunidad real al cold start y menos probabilidad de encontrarse el servidor dormido si usas UptimeRobot.

Cuando termines de subir los vídeos a Play Console, si quieres que te baje a código concreto (por ejemplo el script de `base.html` con el timeout y el "Conectando…"), dímelo y lo afinamos paso a paso.
