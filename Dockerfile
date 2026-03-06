# VINO PRO Backend – con Tesseract OCR para escaneo de etiquetas
# Optimizado para Render, Railway y despliegue local
FROM python:3.11-slim

WORKDIR /app

# Instalar Tesseract OCR y español (requerido para el escáner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Puerto por defecto (Render inyecta PORT)
ENV PORT=8000
EXPOSE 8000

# Mismo arranque que render_start.py (usa PORT de env)
CMD ["python", "render_start.py"]
