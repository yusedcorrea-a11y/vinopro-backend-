# Conectar la app Expo al backend en Railway

## Situación

- **Backend:** ya está en Railway → `https://vinopro-backend-production.up.railway.app`
- **App Expo:** está en **otra carpeta** (no dentro de `backend_optimized`). Hay que localizarla.

---

## 1. Localizar la carpeta de la app Expo

En **Git Bash** o **PowerShell** (desde tu carpeta de usuario o desde `Documents`):

```bash
# Buscar app.json (típico de Expo)
Get-ChildItem -Path "C:\Users\yused\Documents" -Recurse -Filter "app.json" -ErrorAction SilentlyContinue | Select-Object FullName
```

O en Cursor: **Ctrl + Shift + F** (búsqueda global) y busca **`192.168.0.12`**. El archivo donde salga será donde está la URL del API (o cerca).

---

## 2. Dónde suele estar la URL del API en Expo

- **app.json** o **app.config.js** → sección `extra` → `apiUrl` o `apiBaseUrl`
- **.env** o **.env.production** → variable tipo `EXPO_PUBLIC_API_URL` o `API_URL`
- **config.js** / **config.ts** o **constants.js** → una constante con la base URL

---

## 3. Qué poner

Sustituir la URL antigua (ej. `http://192.168.0.12:8001` o `http://127.0.0.1:8001`) por:

```
https://vinopro-backend-production.up.railway.app
```

**Importante:** usar **HTTPS** (con *s*), sin barra final.

---

## 4. CORS en Railway (evitar bloqueos desde el móvil)

En **Railway** → tu servicio → **Variables**:

- **KEY:** `CORS_ORIGINS`
- **VALUE:** `*`

Guarda y deja que Railway reinicie el servicio.

---

## 5. Cuando tengas la ruta de la app

Si me dices la ruta (ej. `C:\Users\yused\Documents\VINO_PRO\app` o el repo de GitHub), te indico el archivo exacto y la línea a cambiar.
