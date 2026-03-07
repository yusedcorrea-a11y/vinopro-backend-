# VINO PRO IA – Resumen de funcionalidades

Resumen básico de todo lo que hace la app (vinoproia.com). Para cuando el dominio esté activo.

---

## Para el usuario

### 1. **Escanear vino**
- Subir foto de la etiqueta, escribir el nombre del vino o introducir el código de barras.
- La app busca en la base de datos y en Open Food Facts.
- Muestra el vino encontrado con opciones: Comprar, Registrar, añadir a Mi Bodega.

### 2. **Registrar vino**
- Añadir vinos nuevos a la base (nombre, bodega, región, país, tipo, puntuación, descripción, maridaje).
- Búsqueda previa para rellenar datos automáticamente si el vino existe.
- Plan Premium: registrar vinos que no estén en la base y crear ofertas (foto + contacto) para que otros los compren.

### 3. **Preguntar al experto en vinos**
- Chat con el experto en vinos virtual: maridajes, recomendaciones por país o tipo de vino, preguntas sobre un vino escaneado.
- Modo Nube (IA) y modo Local (opcional).
- Perfiles: principiante, aficionado, profesional.
- Posibilidad de preguntar por voz.

### 4. **Mi Bodega**
- Bodega virtual por sesión (sin registro): añadir botellas, ver lista, exportar PDF.
- Plan Gratis: hasta 50 vinos. Plan PRO: ilimitado.
- Integración con el Adaptador para restaurantes (API de stock y webhooks).

### 5. **Comprar vino**
- Por cada vino: enlaces de compra según el país del usuario (detectado por IP o elegido).
- **Con Amazon:** enlace a Amazon del país (España, USA, México, Brasil, etc.) con opción de afiliados.
- **Sin Amazon:** enlaces a tiendas locales (Argentina, Chile, Israel, etc.) con opción de afiliados.
- Guía “¿Dónde tomarlo?” por país (vinotecas, bodegas, restaurantes).
- Ofertas de otros usuarios: contacto por email para comprar/recoger.

### 6. **Valoraciones y “Quiero probar”**
- Valorar vinos con estrellas (1–5) y nota opcional.
- Lista “Quiero probar” (wishlist) por sesión.
- Se muestran valoraciones en la ficha del vino.

### 7. **Lugares cerca (Mapa)**
- Buscar restaurantes, vinotecas y bares por ubicación o por ciudad.
- Ver ruta, llamar, web.

### 8. **Planes y pagos**
- **Gratis:** escaneo, experto en vinos, bodega (50 vinos), informes PDF.
- **PRO (4,99 €/mes):** bodega ilimitada, registrar vinos raros, ofertas con foto.
- **Restaurante:** adaptador para conectar con sistemas de gestión (stock, webhooks).
- Pagos con Stripe.

### 9. **Idiomas**
- 14 idiomas: español, inglés, portugués, francés, alemán, italiano, árabe, ruso, turco, chino, japonés, coreano, hindi, hebreo.
- Selector de idioma en la app; cookie para recordar preferencia.

### 10. **Landing y privacidad**
- **Página principal (vinoproia.com):** logo, descripción, “Probar la app web”, “Próximamente en Google Play”, formulario “Avísame cuando esté lista”.
- **Privacidad:** política de privacidad (requerida para Google Play) con datos, cookies, derechos y contacto.
- **Favicon** y metadatos para redes sociales (Open Graph).

---

## Técnico / Backend

- **Health check:** `/health` y `/ready` para monitoreo y despliegue.
- **API REST** para escaneo, experto en vinos, bodega, comprar, planes, valoraciones, wishlist, ofertas.
- **Base de datos:** catálogos de vinos en JSON (España, Francia, Italia, Argentina, Chile, Israel, Líbano, Marruecos, etc.) — más de 899 vinos.
- **Email profesional:** guía para configurar hola@vinoproia.com (reenvío a Gmail vía Cloudflare).
- **Monetización:** Amazon Associates por país; tiendas locales con afiliados en países sin Amazon (variables en .env).
- **Dominio:** configuración con BASE_URL y CORS para vinoproia.com.

---

## Resumen en una frase

**VINO PRO IA** es una app web que permite escanear etiquetas de vino, preguntar al experto en vinos virtual, llevar una bodega personal, comprar con enlaces por país (Amazon y tiendas locales) y recibir recomendaciones, en 14 idiomas, con planes Gratis y PRO.
