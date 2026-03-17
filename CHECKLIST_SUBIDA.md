# Checklist antes de producción / Google Play

**Backend (este repo):** ya en producción en Render → https://vinopro-backend-1.onrender.com

**Para publicar la app en Google Play**, sigue (en orden):

1. **Proyecto Expo:** `projectId` real en `app.json`, luego `eas build --platform android --profile production` → descargar AAB.
2. **Play Console:** crear app, ficha (textos en `docs/TEXTOS_GOOGLE_PLAY.md`), icono 512, feature graphic, capturas, URL privacidad, clasificación y seguridad de datos → subir AAB.

Guías completas: `docs/PREPARACION_SUBIDA_GOOGLE_PLAY.md`, `docs/GUIA_PUBLICACION_GOOGLE_PLAY.md`, `docs/RESUMEN_GOOGLE_PLAY.md`.  
Cierre del área en este repo: `docs/CIERRE_AREA_GOOGLE_PLAY_RENDER.md`.
