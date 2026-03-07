# Fase 6 – Roadmap: App Nativa, Comunidad Social y Cobertura Global

Este documento describe el estado de la Fase 6 y el plan para las subfases **6A (App Nativa)** y **6B (Comunidad Social)**.

---

## ✅ Hecho en el backend (Cobertura global)

- **Nuevos catálogos de vinos** (se cargan automáticamente con el resto en `cargar_todos_los_vinos()`):
  - `data/libano.json` – Château Musar, Ixsir, Massaya (5 vinos)
  - `data/marruecos.json` – Domaine des Ouled Thaleb, Volubilia, etc. (4 vinos)
  - `data/argelia.json` – Coteaux de Mascara, Beni Mtir (2 vinos)
  - `data/tunez.json` – Domaine Mornag, Magon, Sidi Rais (3 vinos)
  - `data/israel.json` – Golan Heights, Dalton, Recanati, Tabor (5 vinos)

- **Guías locales** en `services/enlaces_service.py` (`GUIA_VINO_POR_PAIS`):
  - **RU** – Rusia  
  - **LB** – Líbano (Château Musar)  
  - **MA** – Marruecos  
  - **DZ** – Argelia  
  - **TN** – Túnez  
  - **IL** – Israel (Golan Heights)

- **Traducciones**: claves `pais_LB`, `pais_MA`, `pais_DZ`, `pais_TN`, `pais_IL` en los 14 idiomas (es, en, pt, fr, de, it, ar, ru, tr, zh, ja, ko, hi, he).

- **Experto en Vinos**: en `PAIS_REGION_PALABRAS` se añadieron Líbano, Marruecos, Argelia, Túnez e Israel para recomendaciones por país/región.

---

## 📱 Fase 6A: App Nativa (React Native)

Objetivo: app móvil iOS/Android que reutilice el backend actual.

### Recomendación de división

1. **Proyecto aparte**: crear un repo o carpeta `vino-pro-mobile/` (React Native + TypeScript), no dentro del backend.
2. **API**: usar solo la API REST existente (mismo backend). No hace falta duplicar lógica.

### Tareas sugeridas

| Orden | Tarea | Notas |
|-------|--------|--------|
| 1 | Inicializar proyecto React Native (TypeScript) | `npx react-native init VinoProIA --template react-native-template-typescript` o Expo |
| 2 | Configurar API base URL (env) y cliente HTTP (fetch/axios) | Apuntar a tu backend (ej. `https://api.vinopro.com` o IP local en dev) |
| 3 | Pantalla Experto en Vinos: chat + envío de pregunta + voz (opcional) | GET `/preguntar-sumiller?texto=...`, header `X-Session-ID` |
| 4 | Pantalla Escanear: cámara + subida de imagen o texto | POST a `/analyze/image` o `/analyze/text` según rutas actuales |
| 5 | Pantalla Mapa / Lugares cercanos | Reutilizar lógica de geolocalización del backend |
| 6 | Pantalla Mi Bodega | Endpoints de bodega existentes; auth/sesión según tu modelo |
| 7 | Perfil / Configuración (idioma, modo oscuro) | i18n con los 13 idiomas; leer idioma desde backend o bundle local |
| 8 | i18n en la app | 13 idiomas alineados con `data/translations/*.json` (exportar JSON o endpoint de traducciones) |
| 9 | Modo oscuro/claro | Preferencia local + enlace con tema del backend si aplica |
| 10 | Notificaciones push | Servicio (FCM/APNs); backend: endpoint para registrar token y enviar recomendaciones/ofertas |
| 11 | Build iOS / Android y publicación en stores | Certificados, provisioning, Google Play / App Store |

### Endpoints del backend que la app puede usar

- `GET /preguntar-sumiller?texto=...&perfil=...` – Experto en Vinos (header `X-Session-ID`)
- `POST /api/feedback-vino` – Me gusta / No me gusta
- `POST /analyze/image` o `/analyze/text` – Escaneo
- Rutas de comprar, bodega, geolocalización, etc. (según documentación actual)

---

## 👥 Fase 6B: Comunidad Social

Objetivo: perfiles, seguir usuarios, valoraciones, feed y eventos.

### Recomendación de división

Implementar por capas en el **backend** primero; luego consumir desde web y/o app.

| Orden | Tarea | Backend | Notas |
|-------|--------|---------|--------|
| 1 | **Perfiles de usuario** | Modelo Usuario ampliado: nombre, foto URL, ubicación, bodega pública (lista de vinos) | Tabla o documento `perfiles`; actualizar desde registro/login |
| 2 | **Vinos favoritos** | Lista por usuario (IDs o keys de vino) | Endpoint `GET/POST /api/mi-bodega/favoritos` o similar |
| 3 | **Seguir / Seguidores** | Relación usuario → usuario | Tabla `seguidores`; `GET /api/usuarios/:id/seguidores`, `POST /api/usuarios/:id/seguir` |
| 4 | **Valoraciones y reseñas** | Puntuar vino (1–5), nota de cata, foto opcional | Tabla `valoraciones` (user_id, wine_key, puntuacion, nota, foto_url); promediar para “puntuación comunidad” |
| 5 | **Feed social** | Actividad reciente: “X valoró Y”, “X añadió Z a su bodega” | Endpoint `GET /api/feed?limit=20`; agregar eventos desde valoraciones y bodega |
| 6 | **Grupos / foros** | Grupos por región, tipo de vino, idioma | Tablas `grupos`, `mensajes`; CRUD grupos y mensajes |
| 7 | **Eventos / catas** | Crear evento, unirse, listar | Tabla `eventos` y `eventos_usuarios`; endpoints crear/listar/inscribirse |

### Consideraciones

- **Base de datos**: si hoy todo es JSON en disco, valorar migrar a SQLite/PostgreSQL para usuarios, perfiles, seguidores, valoraciones y feed.
- **Auth**: reutilizar o definir sesión (JWT, cookie) y asociar todas las acciones a `user_id` o `session_id`.
- **Fotos**: subida a almacenamiento (S3, local) y guardar URL en perfil y en valoraciones.

---

## 🌐 Idiomas adicionales

- **Hebreo (he)** para Israel: ✅ Implementado – `data/translations/he.json`, registro en i18n (idioma #14), bandera 🇮🇱, reconocimiento de voz `he-IL`, opción en selector de idioma (base.html).
- **Persa (fa)** / **Urdu (ur)**: para futuras expansiones (Irán, Pakistán), mismo patrón: nuevo JSON de traducciones y registro en i18n.

---

## Verificaciones rápidas

- [ ] Los nuevos JSON (libano, marruecos, argelia, tunez, israel) se cargan al arrancar el backend y los vinos aparecen en búsquedas.
- [ ] En “Comprar” / “Dónde tomarlo”, al detectar país LB, MA, DZ, TN, IL o RU se muestra la guía local correcta.
- [ ] Las traducciones de países nuevos se muestran en el selector de país según idioma.
- [ ] Preguntas al experto en vinos tipo “recomiéndame un vino libanés” o “israelí” devuelven vinos de los nuevos catálogos.

---

*Documento generado en el marco de la Fase 6 – Cobertura global (backend). Fase 6A y 6B son guías para implementación futura.*
