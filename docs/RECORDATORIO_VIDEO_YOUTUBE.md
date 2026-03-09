# Recordatorio: implementar lo del video de YouTube

**Enlace:** https://youtu.be/f02ZOf76qwk (parámetro: `?is=At-gKtKdWCe-43w7`)

El usuario pidió que **en el futuro** se implemente lo que explica este video en la app. No ejecutar ahora; tenerlo pendiente para cuando lo pida.

- **Cuándo:** Cuando el usuario diga que quiere hacer "lo del video" o "lo que habíamos dejado pendiente del video".
- **Qué hacer:** Revisar el contenido del video (o pedir al usuario un resumen si no se puede acceder) e implementar los cambios en la app.

---

## Resuelto (marzo 2026): ofuscación R8/ProGuard y mapping

El video trata sobre **ofuscación en Google Play** (R8/ProGuard) y **subir el mapping** para que los crashes se vean legibles. Se ha creado la guía:

- **`docs/OBFUSCACION_GOOGLE_PLAY_R8_MAPPING.md`** — Checklist: habilitar minify/shrinkResources, reglas ProGuard para no romper la app (modelos, reflexión), y **subir mapping.txt** en Play Console por cada versión.

La implementación concreta (archivos `build.gradle`, `proguard-rules.pro`) se hace en el **proyecto Android** (o en el build que genera EAS/Expo). Este repo es el backend; la guía sirve de referencia para no quedarse en bragas cuando Google revise y ofusque la app.

---

*Creado: marzo 2026. App en camino a Google Play; usuario invierte medio día en mejoras y medio en búsqueda de trabajo remoto.*
