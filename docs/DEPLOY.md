# Despliegue de Vino Pro IA en producción

Guía paso a paso para poner Vino Pro IA en un servidor accesible desde internet (dominio, HTTPS, Stripe en vivo).

---

## 1. Comprar dominio

- **Recomendados:** [Namecheap](https://www.namecheap.com), [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/), [Hostinger](https://www.hostinger.es) (dominio + hosting).
- Elige un nombre (ej. `vinoproia.com`) y compra el dominio.
- Anota el panel de DNS donde añadirás registros (A, CNAME) en el siguiente paso.

---

## 2. Contratar hosting o VPS

Opciones habituales:

| Servicio | Tipo | Enlace | Notas |
|----------|------|--------|--------|
| **DigitalOcean** | VPS | [digitalocean.com](https://www.digitalocean.com) | Droplet Ubuntu 22.04, ~5–10 €/mes |
| **Hetzner** | VPS | [hetzner.com](https://www.hetzner.com) | Buena relación calidad/precio en Europa |
| **Hostinger** | VPS / hosting | [hostinger.es](https://www.hostinger.es) | Dominio + hosting en un solo sitio |
| **Railway / Render** | PaaS | [railway.app](https://railway.app), [render.com](https://render.com) | Despliegue desde Git, menos gestión de servidor |

Para un VPS (DigitalOcean/Hetzner):

1. Crea una cuenta y un servidor (Ubuntu 22.04 LTS).
2. Anota la **IP pública** del servidor.
3. Conéctate por SSH: `ssh root@TU_IP` (o el usuario que te den).

---

## 3. Configurar DNS

En el panel de tu registrador de dominio:

1. **A** (apuntar dominio al servidor):  
   - Nombre: `@` (o vacío)  
   - Valor: **IP de tu VPS**  
   - TTL: 300–3600

2. **A** o **CNAME** (www):  
   - Nombre: `www`  
   - Valor: misma IP (A) o `tudominio.com` (CNAME)  
   - TTL: 300–3600

Los cambios pueden tardar unos minutos u horas en propagarse. Comprueba con:

```bash
ping tudominio.com
```

---

## 4. Subir la app al servidor

### Opción A: Desde tu PC (Windows) con script

En PowerShell, desde la carpeta del proyecto:

```powershell
# Crear carpeta en el servidor vía SSH (si tienes OpenSSH)
# Luego copiar archivos con SCP o usar el script local primero y después SCP la carpeta

$env:DEPLOY_TARGET = "C:\temp\vino-pro-deploy"
.\scripts\deploy.ps1
# Luego sube C:\temp\vino-pro-deploy al servidor (SCP, SFTP, rsync, etc.)
```

### Opción B: En el servidor Linux (recomendado)

En tu VPS (Ubuntu):

```bash
# Instalar dependencias del sistema (Tesseract para OCR)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv tesseract-ocr tesseract-ocr-spa

# Crear directorio de la app
sudo mkdir -p /var/www/vino-pro
sudo chown $USER:$USER /var/www/vino-pro
cd /var/www/vino-pro

# Subir código (desde tu PC, en otra terminal):
# scp -r app.py routes services templates static data requirements_produccion.txt .env.example usuario@TU_IP:/var/www/vino-pro/
# No subas .env con claves; créalo en el servidor.

# En el servidor: entorno virtual e instalar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_produccion.txt
```

---

## 5. Variables de entorno y .env

En el servidor, en `/var/www/vino-pro/`:

```bash
nano .env
```

Contenido mínimo (sustituye por tus valores reales):

```env
HOST=0.0.0.0
PORT=8000
# Dominio final (para sitemap y enlaces)
BASE_URL=https://tudominio.com

# CORS: tu dominio (sin barra final)
CORS_ORIGINS=https://tudominio.com,https://www.tudominio.com

# Stripe PRODUCCIÓN (claves en vivo desde dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Opcional: OpenRouter para IA
# OPENROUTER_API_KEY=sk-or-v1-...
# OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

Guarda (Ctrl+O, Enter, Ctrl+X). **No subas este archivo a Git.**

---

## 6. Activar SSL (HTTPS)

Con el dominio ya apuntando al servidor, usa **Certbot** (Let's Encrypt):

```bash
sudo apt install -y certbot
# Si usas Nginx como reverso proxy (recomendado):
sudo apt install -y nginx
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

Certbot configurará Nginx y renovará el certificado automáticamente.

**Ejemplo de configuración Nginx** (tras Certbot puede generarla él mismo):

```nginx
# /etc/nginx/sites-available/vino-pro
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$server_name$request_uri;
}
server {
    listen 443 ssl;
    server_name tudominio.com www.tudominio.com;
    # ssl_* lo gestiona certbot

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Habilitar y recargar:

```bash
sudo ln -s /etc/nginx/sites-available/vino-pro /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 7. Iniciar la aplicación

En el servidor, con el venv activado:

```bash
cd /var/www/vino-pro
source venv/bin/activate
HOST=0.0.0.0 PORT=8000 nohup python3 app.py &
```

Para que sea un **servicio** (recomendado), crea una unidad systemd:

```bash
sudo nano /etc/systemd/system/vino-pro.service
```

Contenido (ajusta rutas y usuario):

```ini
[Unit]
Description=Vino Pro IA
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/vino-pro
Environment="PATH=/var/www/vino-pro/venv/bin"
EnvironmentFile=/var/www/vino-pro/.env
ExecStart=/var/www/vino-pro/venv/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vino-pro
sudo systemctl start vino-pro
sudo systemctl status vino-pro
```

---

## 8. Stripe en producción

1. En [Stripe Dashboard](https://dashboard.stripe.com) cambia a **Claves en vivo**.
2. Copia **Clave secreta** (`sk_live_...`) y **Clave publicable** (`pk_live_...`) a tu `.env`.
3. **Webhooks:** [Developers → Webhooks](https://dashboard.stripe.com/webhooks) → Añadir endpoint:
   - URL: `https://tudominio.com/webhook-stripe`
   - Eventos: `checkout.session.completed`
   - Copia el **Secreto de firma** (`whsec_...`) a `STRIPE_WEBHOOK_SECRET` en `.env`.
4. Reinicia la app: `sudo systemctl restart vino-pro`.

---

## 9. Comprobaciones finales

- **App:** `https://tudominio.com` → debe cargar la portada.
- **API:** `https://tudominio.com/api/status` → `{"status":"ok", ...}`.
- **HTTPS:** El navegador debe mostrar candado (certificado válido).
- **Sitemap:** `https://tudominio.com/sitemap.xml` → XML con las URLs.
- **Stripe:** Haz una suscripción de prueba (o real) y comprueba en Stripe Dashboard que el webhook se recibe y que el usuario pasa a PRO en Mi Bodega.

Puedes usar el script de pruebas:

```bash
cd /var/www/vino-pro
source venv/bin/activate
python scripts/test_produccion.py --base-url https://tudominio.com
```

---

## Solución de problemas

| Problema | Qué revisar |
|----------|-------------|
| 502 Bad Gateway | Que la app esté escuchando en `0.0.0.0:8000` y el servicio esté activo: `systemctl status vino-pro`. |
| CORS en frontend | Que `CORS_ORIGINS` en `.env` incluya exactamente la URL del front (con `https://`, sin barra final). |
| Webhook Stripe 400 | Que `STRIPE_WEBHOOK_SECRET` sea el del endpoint **en vivo** (no el de `stripe listen`). |
| No se marca PRO | Revisar logs: `journalctl -u vino-pro -f`. Que el webhook esté en `https://tudominio.com/webhook-stripe` y evento `checkout.session.completed`. |
| Certificado SSL | `sudo certbot renew --dry-run`. Que el dominio apunte a esta IP y Nginx esté bien configurado. |

---

## Resumen de comandos útiles

```bash
# Logs de la app
sudo journalctl -u vino-pro -f

# Reiniciar app
sudo systemctl restart vino-pro

# Ver variables (no muestra valores, solo que existen)
cd /var/www/vino-pro && grep -E '^[A-Z_]+' .env | cut -d= -f1
```

Con esto tendrás Vino Pro IA en producción con dominio, HTTPS y pagos Stripe en vivo.
