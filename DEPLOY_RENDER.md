# Despliegue del backend VINO PRO en Render

## 1. Crear Web Service en Render

1. Entra en [Render](https://render.com) y conecta tu repositorio (GitHub/GitLab).
2. **New → Web Service**.
3. Elige el repo que contiene esta carpeta (`backend_optimized`).

## 2. Configuración del servicio

| Campo | Valor |
|-------|--------|
| **Name** | `vinopro-backend` (o el que quieras) |
| **Root Directory** | `backend_optimized` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python render_start.py` |
| **Plan** | Free (o el que uses) |

## 3. Variables de entorno (Environment)

Añade en **Environment** del servicio:

| Key | Valor | Notas |
|-----|--------|--------|
| `PORT` | *(no hace falta)* | Render lo inyecta automáticamente |
| `HOST` | `0.0.0.0` | Opcional; por defecto la app ya usa 0.0.0.0 |
| `CORS_ORIGINS` | `https://vinoproia.com` | En producción mejor tu dominio real; evita `*` si ya tienes frontend definido |
| `DATA_FOLDER` | `data` | Opcional; carpeta relativa para JSONs |
| `DEBUG` | *(vacío o 0)* | En producción mejor sin reload |
| `SUPPORT_EMAIL` | `soporte@vinoproia.com` | Correo dinámico de soporte |
| `GOOGLE_API_KEY` | `...` | Obligatoria para Gemini |
| `VINO_VISION_MODEL` | `gemini-2.0-flash` | Modelo de visión |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Ventana del rate limit |
| `RATE_LIMIT_DEFAULT_PER_MINUTE` | `90` | Límite general por sesión/IP |
| `RATE_LIMIT_HOT_PER_MINUTE` | `12` | Límite para rutas calientes |
| `ESCANEO_MAX_CONCURRENT` | `4` | Máximo de escaneos simultáneos |
| `ENABLE_API4AI_SCAN_HINTS` | `0` | Mantener apagado para ahorrar latencia |

Si usas Stripe, OCR en servidor, etc., añade también las variables que ya usabas en Railway.

## 3.1 Ajuste recomendado para free tier

Para una demo estable en Render Free:

- `RATE_LIMIT_WINDOW_SECONDS=60`
- `RATE_LIMIT_DEFAULT_PER_MINUTE=90`
- `RATE_LIMIT_HOT_PER_MINUTE=12`
- `ESCANEO_MAX_CONCURRENT=4`
- `ENABLE_API4AI_SCAN_HINTS=0`

Con esto reduces picos en `/escanear`, evitas saturación por abuso y mantienes una UX más predecible.

## 4. Datos (carpeta `data`)

- Los JSON de `data/` (vinos, perfiles, etc.) deben estar en el repo dentro de `backend_optimized/data/`, **o** montar un **Disk** en Render y apuntar `DATA_FOLDER` a esa ruta.
- En el **plan Free** no hay disco persistente: si no subes `data/` al repo, los datos se pierden al redeploy. Sube al menos los JSON necesarios (vinos, etc.) en `backend_optimized/data/`.

## 5. URL del backend

Tras el primer deploy, Render te dará una URL tipo:

```
https://vinopro-backend.onrender.com
```

Cópiala: la usarás en la app como **API base URL**.

## 6. Actualizar la app (Expo)

En la app VINO PRO:

1. Abre `app.json` y en `expo.extra.apiUrl` pon la URL de Render:
   ```json
   "extra": {
     "apiUrl": "https://TU-SERVICIO.onrender.com",
     ...
   }
   ```
2. O en `src/services/api.ts` cambia `API_BASE_URL` a esa URL si no usas `extra.apiUrl`.

Reconstruye o reinicia la app para que tome la nueva URL.

## 7. Comprobar que funciona

- `GET https://TU-SERVICIO.onrender.com/api/status` → debe devolver `{"status":"ok", ...}`.
- Desde la app: Inicio, escanear, bodega, etc., deben usar esa base URL.

## Notas

- En plan **Free**, el servicio se “duerme” tras inactividad; la primera petición puede tardar unos segundos.
- **POST /escanear** (imagen) puede tardar; ya tienes timeout 60 s en la app. Si Render corta la petición, revisa el límite de tiempo del plan.
- Si usas **Tesseract** (OCR) en el servidor, Render no lo trae por defecto; puedes usar un **Dockerfile** con imagen que incluya Tesseract o desactivar OCR y apoyarte en el texto que envía la app.
