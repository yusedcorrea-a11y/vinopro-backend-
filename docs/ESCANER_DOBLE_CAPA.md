# Escáner de Doble Capa — VINO

Arquitectura de escaneo infalible: OCR local + fallback con IA de visión.

## Flujo

1. **OCR local**: OpenCV (CLAHE, bilateral, sharpen) + Tesseract (spa+eng)
2. **Fallback**: Si OCR vacío, corto (<15 chars) o baja confianza → GPT-4o o Claude 3.5 Sonnet
3. **Refinamiento**: Normalización (2O22→2022, etc.) y estructura JSON consistente

## Variables de entorno

Añade a tu `.env` **al menos una** para activar el fallback con IA:

```env
# OpenAI (prioridad)
OPENAI_API_KEY=sk-...

# Anthropic (fallback si no hay OpenAI)
ANTHROPIC_API_KEY=sk-ant-...
```

## Instalación de librerías de IA

```powershell
pip install openai>=1.0.0 anthropic>=0.18.0
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

- **Dockerfile**: Incluye openai y anthropic. Añade `OPENAI_API_KEY` o `ANTHROPIC_API_KEY` en Render/Railway.
- **Sin API keys**: El OCR local sigue funcionando. El fallback con visión solo se activa si hay clave configurada.
