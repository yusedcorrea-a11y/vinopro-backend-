# QR personalizados – Networking Turín

Sistema para generar códigos QR únicos por contacto. Al escanear, la persona ve una página web personalizada con mensaje de agradecimiento, presentación de Vino Pro IA, beneficios y tus datos de contacto. Tú recibes seguimiento (quién escaneó, cuándo, desde qué país).

## Uso rápido

1. **Panel:** Menú → **QR networking** (o `/qr`). Responsive para móvil.
2. **Crear QR:** Nombre de la persona, empresa (opcional), idioma del mensaje (IT/ES/EN). Pulsar **Generar QR**.
3. **Descargar:** Se muestra la imagen QR; **Descargar imagen** guarda un PNG para imprimir o enviar.
4. **Seguimiento:** La tabla inferior lista todos los contactos: escaneado sí/no, fecha y país del escaneo.

## URL pública

- Página que ve el contacto: `https://vinoproia.com/c/CODIGO` (ej. `/c/a1b2c3d4`).
- El idioma de la página se puede cambiar con enlaces (Italiano / Español / English).

## Variables de entorno (opcional)

En `.env` puedes definir:

| Variable | Uso |
|----------|-----|
| `QR_EMAIL` | Email que aparece en "Contacto" (por defecto hola@vinoproia.com) |
| `QR_LINKEDIN` | URL de tu perfil LinkedIn |
| `QR_WHATSAPP` | Número con código de país (sin +), ej. 34600000000. Se muestra como enlace wa.me |
| `QR_CALENDLY` | URL de Calendly (u otra herramienta) para "Agendar reunión" |
| `QR_WEBHOOK_URL` | URL a la que se envía un POST (JSON) cada vez que alguien escanea su QR. Útil para Slack o un bot de Telegram. |

## Notificaciones

- Cada escaneo se registra en **consola** y en `data/qr_escaneos.log`.
- Si defines `QR_WEBHOOK_URL`, se envía un POST con: `{ "text", "nombre", "codigo", "pais" }`. Puedes conectar un Incoming Webhook de Slack o un bot de Telegram que acepte JSON.

## Datos

- Contactos: `data/contactos_qr.json`
- Log de escaneos: `data/qr_escaneos.log`

## País del escaneo

En producción con **Cloudflare**, el país se obtiene del header `CF-IPCountry`. Sin Cloudflare, el campo quedará vacío o "N/A".
