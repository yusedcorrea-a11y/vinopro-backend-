# ✅ Backend en Railway – Qué queda para dejarlo perfecto

El backend ya está **ACTIVO** en Railway. Siguiente pasos recomendados.

---

## 1. Anotar la URL pública de Railway

- En **Railway** → tu servicio → **Settings** → **Networking** / **Domains**.
- Copia la URL tipo: `https://vinopro-backend-production.up.railway.app` (o la que te haya asignado).

---

## 2. Conectar el frontend (Expo / React Native)

Donde tengas la app móvil (Expo):

- Sustituir la URL local (`http://192.168.0.12:8001` o `http://127.0.0.1:8001`) por la URL de Railway en **HTTPS**.
- Suele estar en:
  - `app.json` → `extra.apiUrl` o `extra.apiBaseUrl`, o
  - Un archivo de config / `.env` (ej. `EXPO_PUBLIC_API_URL`).
- Ejemplo: `https://vinopro-backend-production.up.railway.app` (sin barra final).
- Después: **rebuild** de la app (o al menos reiniciar Expo con la nueva config).

---

## 3. CORS en Railway (Variables de entorno)

Para que la app pueda llamar al API desde el móvil o desde una web:

- En Railway → **Variables**.
- Añadir o editar:
  - `CORS_ORIGINS` = `*` (solo para pruebas) o, mejor, la URL de tu app/web (ej. `https://tuapp.expo.dev` o tu dominio).
- Redeploy si hace falta.

---

## 4. (Opcional) Dominio propio: api.vinoproia.com

1. **Cloudflare** → DNS del dominio `vinoproia.com`.
2. Crear registro:
   - Tipo: **CNAME**
   - Nombre: `api` (o el subdominio que quieras).
   - Destino: la URL de Railway **solo el host** (ej. `vinopro-backend-production.up.railway.app`).
3. En Railway → **Settings** → **Domains**: añadir dominio personalizado `api.vinoproia.com` si lo soporta.
4. En el frontend, usar `https://api.vinoproia.com` como URL del API en lugar de la URL `.up.railway.app`.

---

## 5. Comprobar que todo responde

- **Swagger:** `https://TU-URL.up.railway.app/docs`
- **Health/status:** si tienes ruta `/health` o `/api/status`, probarla desde el navegador o con la app.
- Probar **escanear un vino** desde la app con la nueva URL.

---

## Resumen rápido

| Paso | Acción |
|------|--------|
| 1 | Anotar URL de Railway |
| 2 | En la app Expo: cambiar URL del API a esa URL (HTTPS) |
| 3 | Poner `CORS_ORIGINS` en Railway si la app da error de CORS |
| 4 | (Opcional) CNAME `api.vinoproia.com` → Railway en Cloudflare |
| 5 | Probar /docs, /health y escaneo desde la app |

Cuando tengas la URL exacta de Railway (o `api.vinoproia.com`), actualiza el frontend con esa base y haz una prueba real de escaneo desde el móvil.
