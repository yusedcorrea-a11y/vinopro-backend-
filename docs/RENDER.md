# VINO PRO Backend en Render

## URL del servicio
- **Pública:** `https://vinopro-backend-1.onrender.com`
- Usa esta URL para abrir la app (inicio, signup, feed, etc.).

## Plan gratuito: inactividad
En plan **Gratis**, la instancia se **apaga tras ~15 min sin peticiones**. La primera petición después de eso puede tardar **50 segundos o más** (cold start).

### Qué hemos hecho en la app
- **Registro e inicio de sesión:** timeout de 90 s y mensaje tipo *"Conectando… en plan gratuito la primera vez puede tardar hasta 1 minuto"*. Si aun así da timeout, se indica *"El servidor está despertando. Espera unos segundos y vuelve a pulsar"*.
- El usuario puede esperar y volver a intentar; cuando la instancia esté despierta, responderá en segundos.

### Opcional: reducir cold starts
Si quieres que la instancia se despierte menos veces:
1. **UptimeRobot** (gratis): crea un monitor que haga GET a `https://vinopro-backend-1.onrender.com/api/status` cada 14 minutos.
2. **Cron job en Render:** en el dashboard, si tienes "Cron Jobs", puedes programar un ping cada 14 min a tu propia URL.

## Variables de entorno (Render)
En **Environment** del servicio, asegúrate de tener al menos:
- `PYTHON_VERSION` = `3.11` (o la que use tu build)
- Las que use tu app (p. ej. `GOOGLE_API_KEY`, `DATA_FOLDER`, etc.) según tu `.env.example`.

## Despliegue
- Con **Auto-Deploy** desde GitHub, cada push a la rama conectada (p. ej. `main`) despliega solo.
- **Despliegue manual:** en el dashboard, "Despliegue manual" → "Desplegar último commit".

## Logs
En **Troncos** (Logs) ves la salida del servidor. Si el registro falla, revisa ahí si hay excepciones o 500.
