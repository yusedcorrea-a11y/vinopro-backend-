# Resumen rápido: qué tenemos y qué falta para Google Play

---

## Lo que ya tenemos hecho

### Backend y app web (vinoproia.com)
- **Funcionalidad:** Escanear, registrar, experto en vinos, mi bodega, comprar (Amazon + tiendas locales), planes Gratis/PRO, Stripe, valoraciones, wishlist, mapa, comunidad (perfiles, feed, seguir), QR networking.
- **Idiomas:** 14 (es, en, pt, fr, de, it, ar, ru, tr, zh, ja, ko, hi, he).
- **Landing:** Logo, “Probar la app web”, “Próximamente en Google Play”, formulario “Avísame”.
- **Privacidad:** Página `/privacidad` (política de privacidad) — **requerida para Google Play**.
- **Técnico:** `/health`, `/ready`, CORS, BASE_URL, favicon, Open Graph.
- **Catálogos:** Vinos por país (ES, FR, IT, AR, CL, IL, LB, MA, etc.) + tiendas locales por país.

### App móvil (Expo / React Native)
- **Proyecto:** Carpeta `frontend/` con Expo 54, React Native, expo-router.
- **Config Android:** `package`: `com.yused.vinopro`, icono, splash, permisos (cámara, almacenamiento).
- **Config iOS:** `bundleIdentifier`: `com.yused.vinopro`, textos de uso cámara/galería.
- **EAS:** En `app.json` el `projectId` está como placeholder (`your-project-id-here`).

---

## Lo que falta para meter la app en Google Play

### 1. App Android lista para subir
- [ ] **EAS Build:** Crear proyecto en [expo.dev](https://expo.dev) y poner el `projectId` real en `app.json` → `extra.eas.projectId`.
- [ ] **Build de producción:** `eas build --platform android --profile production` (o el perfil que uses) y generar el AAB/APK.
- [ ] **Probar** el AAB en un dispositivo o emulador antes de subir.

### 2. Cuenta y ficha en Google Play
- [ ] **Cuenta de desarrollador:** [Google Play Console](https://play.google.com/console) — pago único (~25 USD).
- [ ] **Ficha de la aplicación:**
  - Título: ej. “Vino Pro IA – Experto en Vinos virtual”
  - Descripción corta y larga (qué hace la app, idiomas, planes).
  - **Icono 512×512** (PNG, sin transparencia).
  - **Gráfico de función** (feature graphic) 1024×500.
  - **Capturas de pantalla** (mínimo 2, teléfono; tablet si soportas tablet).
- [ ] **URL de política de privacidad:** `https://vinoproia.com/privacidad` (ya la tienes).

### 3. Formularios obligatorios en Play Console
- [ ] **Clasificación de contenido:** Cuestionario (edad, tipo de contenido). Para una app de vinos suele ser +18 o similar según respuestas.
- [ ] **Seguridad de los datos:** Declarar qué datos recoges (sesión, bodega, valoraciones, email si usas “Avísame”, etc.) y para qué.
- [ ] **Público objetivo:** Edad y país(es) a los que va dirigida.

### 4. Opcional pero recomendado
- [ ] **Tests internos:** Subir el AAB a una pista interna, instalar y probar en varios dispositivos.
- [ ] **Versión:** Tener claro `versionCode` y `versionName` en el build (EAS lo gestiona desde `app.json` si lo tienes configurado).

---

## Resumen en una frase

**Tenemos:** Backend y web completos + app Expo/Android configurada.  
**Falta:** Hacer el build Android con EAS, crear la cuenta en Play Console, rellenar ficha (textos, icono 512, capturas, privacidad) y los formularios de contenido y datos; luego subir el AAB y publicar.

---

## Orden sugerido

1. Completar `app.json` con el EAS projectId real y revisar `version` (ej. `1.0.0`).
2. Generar icono 512×512 y feature graphic para la ficha.
3. Hacer `eas build --platform android` y descargar el AAB.
4. Abrir Play Console → Crear aplicación → Rellenar ficha, privacidad, clasificación y datos.
5. Subir el AAB a una pista (interna o producción) y enviar a revisión.

Cuando tengas el AAB subido y la ficha lista, Google suele tardar unos días en revisar la primera publicación.
