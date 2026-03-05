# Traducción en tiempo real – Comunidad sin barreras de idioma

La comunidad **Futuros Vineros** traduce el contenido en tiempo real al idioma preferido de cada usuario. Un vinero en Rusia puede escribir en ruso y un usuario en India verlo en hindi (o en cualquier otro idioma soportado).

## Backend

- **Servicio:** `services/translation_service.py`  
  Usa [LibreTranslate](https://libretranslate.com) (gratuito).  
- **Variables de entorno (opcionales):**
  - `LIBRETRANSLATE_URL`: URL del API (por defecto `https://libretranslate.com`). Puedes usar una instancia self-hosted.
  - `LIBRETRANSLATE_API_KEY`: Clave opcional para mayor cuota en el servicio público.
- **Endpoints:**
  - `POST /api/traducir`: body `{ "texto", "idioma_destino", "idioma_origen" (opcional) }` → `{ "traducido" }`
  - `POST /api/traducir-lote`: body `{ "textos": string[], "idioma_destino", "idioma_origen" (opcional) }` → `{ "traducidos" }` (máx. 50 textos)
- **Perfil de usuario:** El campo `idioma` en el perfil indica en qué idioma quiere el usuario **leer** el contenido de otros (es, en, ru, hi, etc.).

## App

- El usuario elige su **idioma de lectura** en **Mi perfil** (selector “Idioma para leer la comunidad”).
- Se guarda en el perfil (`idioma`) y en AsyncStorage (`@VinoPro:idioma`) como respaldo.
- **Feed:** Los textos de actividad (nombre del vino, título y texto de eventos) se traducen al idioma del usuario al cargar/actualizar.
- **Perfil público:** La bio y la ubicación del perfil visitado se traducen al idioma del visitante.

## Idiomas soportados (ejemplos)

Español, inglés, francés, alemán, italiano, portugués, ruso, hindi, árabe, chino, japonés, coreano, turco, hebreo, tailandés, vietnamita y otros según LibreTranslate.
