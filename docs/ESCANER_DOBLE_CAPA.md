# Escáner de Doble Capa — VINO

Arquitectura de escaneo infalible: OCR local + fallback con IA de visión.

## Flujo

1. **OCR local**: OpenCV (CLAHE, bilateral, sharpen) + Tesseract (spa+eng)
2. **Fallback**: Si OCR vacío, corto (<15 chars) o baja confianza → Google Gemini 2.0 Flash
3. **Refinamiento**: Normalización (2O22→2022, etc.) y estructura JSON consistente

## Variables de entorno

Añade a tu `.env` para activar el fallback con IA:

```env
GOOGLE_API_KEY=tu-clave-de-google-ai
```

(Obtén la clave en https://aistudio.google.com/apikey)

## Instalación de librerías de IA

```powershell
pip install google-genai
```

O con requirements:

```powershell
pip install -r requirements.txt
```

## Estructura JSON de salida

Siempre consistente (campos null si no se detectan):

```json
{
  "bodega": "Hnos Pérez Pascuas",
  "nombre": "Viña Pedrosa Crianza",
  "añada": 2021,
  "denominacion_origen": "Ribera del Duero",
  "variedad": "Tempranillo"
}
```

## Compatibilidad

- **Dockerfile**: Incluye google-generativeai. Añade `GOOGLE_API_KEY` en Render/Railway.
- **Sin API key**: El OCR local sigue funcionando. El fallback con visión solo se activa si hay clave configurada.
