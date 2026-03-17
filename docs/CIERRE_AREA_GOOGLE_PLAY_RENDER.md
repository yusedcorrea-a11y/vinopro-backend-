# Cierre área Google Play + Render

**Objetivo:** Dejar cerrada la parte que corresponde a este repo (backend). Lo que queda para publicar en Play depende del proyecto Expo y de Play Console.

---

## ✅ Hecho en este repo (backend)

### Render
- Backend desplegado en **https://vinopro-backend-1.onrender.com**
- `render.yaml` con servicio web, Python, auto-deploy desde GitHub
- `render_start.py` para arranque
- Doc: `docs/RENDER.md` (URL, cold start, variables, logs)
- App web e inicio: `https://vinopro-backend-1.onrender.com/inicio`

### Google Play (documentación y soporte)
- **Textos ficha:** `docs/TEXTOS_GOOGLE_PLAY.md` (título, descripción corta/larga)
- **Guía paso a paso:** `docs/GUIA_PUBLICACION_GOOGLE_PLAY.md` (ficha, icono 512, feature graphic, capturas, privacidad, clasificación)
- **Preparación y orden:** `docs/PREPARACION_SUBIDA_GOOGLE_PLAY.md` (EAS, AAB, Play Console, mapping)
- **Resumen qué falta:** `docs/RESUMEN_GOOGLE_PLAY.md`
- **Ofuscación R8:** `docs/OBFUSCACION_GOOGLE_PLAY_R8_MAPPING.md`
- **Política de privacidad:** accesible vía web (requerida para Play)

### Backend listo para la app
- Health/ready, CORS, BASE_URL, idiomas, privacidad, funcionalidad completa descrita en los docs.

---

## ⏳ Pendiente (fuera de este repo)

| Dónde | Qué |
|-------|-----|
| **Proyecto Expo / Android** | Poner EAS `projectId` real en `app.json`, `eas build --platform android --profile production`, obtener AAB. Subir mapping.txt si usas R8. |
| **Google Play Console** | Cuenta desarrollador, crear app, rellenar ficha (textos de `TEXTOS_GOOGLE_PLAY.md` y guía), icono 512, feature graphic, capturas, URL privacidad, clasificación de contenido, seguridad de datos, público objetivo. Subir AAB y enviar a revisión. |
| **Opcional** | UptimeRobot (ping cada 14 min a `/api/status`) para reducir cold starts en plan gratuito. |

---

## Resumen en una frase

**En este repo:** área Google Play + Render **cerrada**: backend en Render operativo y toda la documentación para Play y despliegue está en `docs/`.  
**Siguiente paso cuando quieras publicar:** usar la app Expo (otra carpeta/repo) para el build Android y Play Console con los textos y guías de este repo.

---

## Próximo foco

Llamadas y videollamadas en el chat VINEROS → ver `docs/ANALISIS_LLAMADA_VIDEO_CHAT_VINEROS.md`.
