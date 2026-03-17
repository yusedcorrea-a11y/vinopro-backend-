# Preparación para subir VINO PRO a Google Play

**Objetivo:** Tener todo listo para Play Console + AAB. Este repo es el **backend** (Render). El **AAB** se genera en el **proyecto Android/Expo** (carpeta `frontend/` u otro repo según tu estructura).

---

## 1. Dónde está cada cosa

| Qué | Dónde |
|-----|--------|
| **Backend en vivo** | Render → `https://vinopro-backend-1.onrender.com` (o tu `BASE_URL`) |
| **Política de privacidad (URL para Play)** | `https://vinoproia.com/privacidad` (o la que uses en producción) |
| **Textos ficha Play** | `docs/TEXTOS_GOOGLE_PLAY.md` |
| **Guía paso a paso Play Console** | `docs/GUIA_PUBLICACION_GOOGLE_PLAY.md` |
| **Resumen qué falta** | `docs/RESUMEN_GOOGLE_PLAY.md` |
| **Ofuscación R8 + mapping.txt** | `docs/OBFUSCACION_GOOGLE_PLAY_R8_MAPPING.md` |
| **Checklist backend antes de producción** | `CHECKLIST_SUBIDA.md` (raíz del repo) |

---

## 2. Orden recomendado (con DEEPSEEK / Cursor)

### A) Proyecto Android / Expo (donde está `app.json`)

1. **EAS / Expo**
   - Crear proyecto en [expo.dev](https://expo.dev) si no existe.
   - En `app.json` (o `app.config.js`): poner el **projectId** real en `extra.eas.projectId` (no dejar placeholder).
   - **Package Android:** `com.yused.vinopro` (según `RESUMEN_GOOGLE_PLAY.md`).
   - **API / dominio:** que la app apunte al backend en producción (`BASE_URL` o URL de Render en variables de entorno del build).

2. **Build de producción**
   ```bash
   eas build --platform android --profile production
   ```
   - Descargar el **.aab** (Android App Bundle).
   - Opcional: probar en dispositivo/emulador antes de subir.

3. **Mapping (desofuscación)**
   - Tras cada build release, localizar **mapping.txt** (salida de EAS o carpeta `android/app/build/outputs/mapping/...`).
   - Subirlo en Play Console en **Archivos de desofuscación** para esa versión (ver `OBFUSCACION_GOOGLE_PLAY_R8_MAPPING.md`).

### B) Google Play Console

1. **Cuenta** → [play.google.com/console](https://play.google.com/console) (cuenta ya pagada si te llegó el “en hora buena” de Google).
2. **Crear app** → Nombre, idioma, gratuita con compras in-app (PRO).
3. **Ficha principal** → Copiar textos de `docs/TEXTOS_GOOGLE_PLAY.md` y `GUIA_PUBLICACION_GOOGLE_PLAY.md`:
   - Icono **512×512** PNG sin transparencia.
   - **Feature graphic** 1024×500.
   - **Capturas** mínimo 2 (recomendado 4–6), ver tabla en la guía.
   - **URL privacidad:** la que uses en producción (ej. vinoproia.com/privacidad).
4. **Política de la app**
   - **Seguridad de los datos** → Cuestionario (sesión, bodega, email “Avísame”, etc.) alineado con `/privacidad`.
   - **Clasificación de contenido** → +18 / vino / sin público &lt;13.
   - **Público objetivo** → No dirigida a menores.
5. **Producción** → Crear versión → **Subir AAB** → Notas de versión → Rollout.
6. Esperar revisión (primeras veces pueden tardar varios días).

---

## 3. Checklist rápido antes de “Enviar a revisión”

- [ ] AAB generado con perfil **production** (no debug).
- [ ] App abre y habla con el backend correcto (Render o dominio final).
- [ ] Privacidad accesible por URL pública.
- [ ] Icono 512 + feature graphic + capturas subidas.
- [ ] Seguridad de datos y clasificación completados.
- [ ] **mapping.txt** de esa build subido (si aplica R8/ProGuard).

---

## 4. Si el proyecto Expo no está en este repo

El `RESUMEN_GOOGLE_PLAY.md` habla de `frontend/` con Expo 54. Si tu app la tienes en otra carpeta o repo:

- Abre ese proyecto con Cursor/DEEPSEEK.
- Misma lógica: `eas build --platform android`, subir AAB, rellenar Play Console con los docs de **este** repo (`docs/`).

---

## 5. Archivos clave a tener abiertos mientras subes

1. `docs/GUIA_PUBLICACION_GOOGLE_PLAY.md` — Fases A–F.
2. `docs/TEXTOS_GOOGLE_PLAY.md` — Copy-paste ficha.
3. `docs/OBFUSCACION_GOOGLE_PLAY_R8_MAPPING.md` — Cuando subas mapping.
4. `README_AMAZON.md` — Si la app muestra enlaces Amazon, el aviso legal ya está en `/inicio` (backend).

---

*Documento de preparación; la ejecución del build EAS y la subida del AAB se hacen en el entorno donde tengas el proyecto Android/Expo.*
