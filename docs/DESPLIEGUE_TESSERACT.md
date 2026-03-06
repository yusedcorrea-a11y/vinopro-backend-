# Despliegue con Tesseract OCR

Resumen de cómo asegurar que Tesseract esté disponible en cada entorno.

---

## Render (Cloud)

El proyecto usa **Docker** para Render. El `Dockerfile` instala `tesseract-ocr`, `tesseract-ocr-spa` y `tesseract-ocr-eng`.

**Pasos:**
1. Push al repositorio.
2. En Render, el servicio debe tener `runtime: docker` y `dockerfilePath: Dockerfile` (ya configurado en `render.yaml`).
3. Si creaste el servicio antes del cambio a Docker, en el dashboard: **Settings** → **Build & Deploy** → cambiar a **Docker** y apuntar al Dockerfile.
4. Redesplegar.

Tras el despliegue, el mensaje "El escaneo requiere un componente adicional" no debería aparecer.

---

## Railway

Railway usa Nixpacks por defecto. Para Tesseract, usa el Dockerfile:

1. Crea un `railway.toml` o en el dashboard configura **Dockerfile** como método de build.
2. El `Dockerfile` del proyecto ya incluye Tesseract.

---

## VPS / Linux manual (deploy.sh)

El script `scripts/deploy.sh` instala Tesseract con `apt-get` antes de las dependencias Python. Ejecuta:

```bash
./scripts/deploy.sh /var/www/vino-pro
```

---

## Windows local (Lenovo IdeaPad 3)

Ver `docs/INSTALAR_TESSERACT_WINDOWS.md` para comandos exactos de PATH y variable `TESSERACT_CMD`.
