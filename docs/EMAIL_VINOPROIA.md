# Email profesional hola@vinoproia.com

Para que **hola@vinoproia.com** reenvíe a **yusedcorrea@gmail.com** puedes usar **Cloudflare Email Routing** (gratis) ya que el dominio está en Cloudflare.

---

## Pasos en Cloudflare

1. **Entra en Cloudflare** → selecciona el dominio **vinoproia.com**.

2. **Email** → En el menú lateral, entra en **Email** → **Email Routing** (o **Workers & Pages** según la versión; si no ves "Email Routing", busca "Email" en el panel).

3. **Activar Email Routing**  
   - Si es la primera vez, Cloudflare te pedirá activar el routing.  
   - Tendrás que añadir los **registros MX** que te indique (normalmente Cloudflare los propone y los aplicas con un clic).

4. **Crear una dirección de reenvío**  
   - En **Custom addresses** (o **Destination addresses** / **Forwarding**), añade:  
     - **Dirección:** `hola` (o el nombre que quieras; el dominio será @vinoproia.com).  
     - **Destino:** `yusedcorrea@gmail.com`  
   - Guarda.

5. **Verificación**  
   - Cloudflare puede enviar un correo de verificación a **yusedcorrea@gmail.com**.  
   - Abre el enlace para confirmar que aceptas recibir los reenvíos.

---

## Alternativa: Gmail con dominio propio

Si prefieres **enviar** también desde hola@vinoproia.com (no solo recibir):

- Opción **Google Workspace** (de pago): permite usar @vinoproia.com con Gmail.  
- Opción **gratuita**: solo reenvío con Cloudflare (recibir en Gmail y responder desde yusedcorrea@gmail.com); los destinatarios verán “Enviado desde yusedcorrea@gmail.com” a menos que configures “Enviar como” en Gmail con una dirección verificada (para “Enviar como” hola@vinoproia.com Gmail suele pedir SMTP o Workspace).

Para **solo recibir** en Gmail y que todo llegue a yusedcorrea@gmail.com, con **Cloudflare Email Routing** es suficiente.

---

## Resumen

| Qué quieres              | Cómo                          |
|--------------------------|--------------------------------|
| Recibir en Gmail         | Cloudflare Email Routing → reenviar hola@ a yusedcorrea@gmail.com |
| Enviar desde hola@       | Google Workspace o SMTP externo (no solo Cloudflare Routing)      |

Si al entrar en Cloudflare no ves “Email” o “Email Routing”, revisa la documentación actual:  
https://developers.cloudflare.com/email-routing/
