# Conectar la app desde el móvil

Si en el ordenador se ve bien pero en **2 móviles** (o uno) la app se queda "activando" o cargando sin terminar, suele ser por **cómo** y **dónde** abres la app.

---

## Opción A: Usar la URL de producción (Recomendado)

**En el móvil abre la misma URL que usas en el navegador del PC**, por ejemplo:

- **Render:** `https://tu-servicio.onrender.com`  
  (sustituye por la URL real que te da Render en el panel del servicio)

**Importante:**

1. **Primera vez o tras mucho tiempo sin usar:** En plan gratuito el servidor puede estar "dormido". La **primera carga puede tardar 30–60 segundos**. Verás la pantalla en blanco o el indicador de carga hasta que responda. Es normal; la siguiente vez irá rápido.
2. **Misma URL en todos los dispositivos:** Los 2 móviles deben usar exactamente la misma URL (la de Render o tu dominio).
3. **HTTPS:** Usa siempre `https://` en el móvil; algunos navegadores bloquean contenido mixto si abres por `http://`.

Si tras **más de 1 minuto** sigue sin cargar, comprueba en el panel de Render que el último deploy esté en "Live" y que no haya errores en los logs.

---

## Opción B: Red local (PC + móviles en la misma WiFi)

Si quieres probar con el backend en tu PC y los móviles en la misma casa:

### 1. Arrancar el backend escuchando en toda la red

En el PC, en la carpeta del backend:

```bash
python main.py
```

Por defecto ya usa `HOST=0.0.0.0`, así que acepta conexiones desde otros dispositivos de la red.

### 2. Saber la IP de tu PC

En el mismo PC:

- **Windows (PowerShell o CMD):** `ipconfig`  
  Busca **Adaptador de LAN inalámbrica** o **Wi‑Fi** → **Dirección IPv4** (ej. `192.168.0.12`).
- **Mac/Linux:** `ifconfig` o `ip addr` y mira la IP de tu interfaz WiFi.

### 3. Abrir en el móvil

En el navegador del móvil (con la **misma WiFi** que el PC) escribe:

```
http://192.168.0.12:8001
```

(sustituye `192.168.0.12` por la IPv4 de tu PC; el puerto por defecto es `8001`).

### 4. Si no carga: firewall

En **Windows** puede estar bloqueando el puerto:

1. **Configuración** → **Red e Internet** → **Firewall de Windows** → **Configuración avanzada**.
2. **Reglas de entrada** → **Nueva regla** → **Puerto** → TCP, puerto **8001** → Permitir → Nombre p. ej. "VinoPro Backend".
3. O temporalmente (solo para probar): desactiva el firewall en redes privadas y prueba de nuevo.

---

## Resumen rápido

| Dónde abres la app | Qué hacer |
|--------------------|-----------|
| **URL de Render** en el móvil | Usar la URL exacta; esperar hasta 1 min la primera vez (cold start). |
| **IP del PC** (ej. `http://192.168.0.12:8001`) | PC y móvil en la misma WiFi; backend con `HOST=0.0.0.0`; permitir puerto 8001 en el firewall. |

Si sigue quedándose "activando", en la app web verás un aviso de "No se pudo conectar al servidor" con la opción de reintentar cuando el servidor esté disponible.
