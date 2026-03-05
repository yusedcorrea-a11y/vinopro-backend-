# Mejoras pendientes – Futuros Vineros y app

## Prioridad alta

### 1. **Notificaciones en la app**
- **Estado:** El backend ya tiene `GET /api/notificaciones` y `POST /api/notificaciones/leer`; la app **no** los usa.
- **Falta:** Pantalla o drawer de notificaciones (nuevo seguidor, nuevo mensaje) y, si hay un mensaje, enlace directo al chat con ese usuario.
- **Opcional:** Badge con número de no leídas en el icono de Mensajes o en el header del Feed.

### 2. **Actividad "probado" en el feed**
- **Estado:** Al valorar o añadir a “deseado” ya se registra actividad. Al **añadir a Mi Bodega** no se registra “probado”.
- **Falta:** En la ruta de bodega (al añadir botella), si el usuario tiene perfil de comunidad, llamar a `feed_svc.add_actividad(username, "probado", vino_key, vino_nombre=...)` para que en el feed salga “X probó Y”.

### 3. **Chat: ver mensajes nuevos sin salir**
- **Estado:** Para ver mensajes nuevos hay que salir del chat y volver a entrar (o hacer pull-to-refresh si lo añadimos).
- **Mejora:** Añadir pull-to-refresh en ChatScreen y/o polling cada X segundos mientras la pantalla está abierta, para actualizar mensajes entrantes.

## Prioridad media

### 4. **Push notifications**
- Nuevo mensaje o nuevo seguidor podrían llegar como push (Expo Notifications / FCM) aunque la app esté cerrada.
- Requiere configuración en Expo/Firebase y un job en el backend que envíe el push cuando se cree la notificación.

### 5. **Moderación y seguridad**
- Bloquear usuario (no ver su perfil ni recibir mensajes).
- Reportar usuario o contenido (guardar reporte y, en el futuro, revisión manual).
- Límite de mensajes por minuto para evitar spam.

### 6. **Eventos destacados en el feed**
- El feed ya mezcla “eventos” y “actividad”. Si `get_eventos_destacados()` devuelve vacío, solo se ve actividad de usuarios.
- Añadir datos de ejemplo en `data/actividad.json` con tipo "evento" (titulo, texto, link) o un JSON específico de eventos para que el feed tenga contenido destacado (cata, oferta, etc.).

## Prioridad baja / nice to have

### 7. **Caché de traducciones**
- Evitar traducir dos veces el mismo texto al mismo idioma: guardar en memoria o en disco (clave: hash(texto)+idioma) para feed y chat.

### 8. **Onboarding**
- Primera vez: explicar en 1–2 pantallas Mi Bodega, Futuros Vineros, idioma y chat (“cada uno escribe en su idioma”).

### 9. **Fotos**
- El modelo tiene `avatar_path` y `foto_path` en valoraciones; la app podría permitir subir foto de perfil y de valoración si el backend expone upload y las rutas las usan.

### 10. **Offline / resilencia**
- Guardar última bodega y último feed en AsyncStorage para mostrar algo sin red; marcar claramente “sin conexión”.

---

Resumen ejecutivo: lo que más impacto tiene ahora es **notificaciones en la app** (que el usuario vea “nuevo mensaje” y pueda ir al chat) y **actividad “probado”** al añadir a bodega; después, refresco de mensajes en el chat y, si quieres, push y moderación.
