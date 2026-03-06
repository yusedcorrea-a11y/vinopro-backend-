# Resumen de cambios — Mejoras del escáner OCR

## Archivos modificados

### Nuevos archivos
- **`services/image_preprocessor.py`**: Preprocesamiento OpenCV (CLAHE, bilateral, sharpen, binarización adaptativa) para mejorar OCR en etiquetas con reflejos, ruido y contraste bajo.
- **`services/entity_extractor.py`**: Extracción de entidades desde texto OCR: Bodega, Nombre del vino, Añada, Denominación de Origen, Variedad de uva.

### Modificados
- **`services/ocr_service.py`**: OCR multi-paso con preprocesamiento. Ejecuta Tesseract sobre 3 pipelines (CLAHE, bilateral+sharpen, adaptativo) + imagen original y elige el mejor resultado por puntuación heurística.
- **`routes/escaneo.py`**: Inclusión de `entidades_extraidas` en todas las respuestas del endpoint `/escanear`. La app móvil puede mostrar Bodega, Nombre, Añada, DO y Variedad aunque no haya match en BD.
- **`requirements.txt`**: Añadido `opencv-python-headless>=4.8.0`.

## Comportamiento

1. **Preprocesamiento**: Si OpenCV está instalado, la imagen se procesa con CLAHE (contraste), filtro bilateral (ruido) y sharpen antes de OCR. Fallback a imagen original si OpenCV no está disponible.
2. **OCR multi-paso**: Se ejecuta Tesseract sobre varias versiones de la imagen y se selecciona el texto con mejor puntuación (palabras clave de vino + longitud).
3. **Entidades extraídas**: En cada respuesta JSON se incluye `entidades_extraidas` con los campos `bodega`, `nombre`, `añada`, `denominacion_origen`, `variedad` cuando se detectan en el texto.

## Comando para despliegue

```bash
pip install -r requirements.txt
```

## Compatibilidad

- Optimizado para CPU (Lenovo IdeaPad 3). Sin dependencias de GPU.
- Si OpenCV no está instalado, el OCR sigue funcionando con el flujo anterior (solo PIL + Tesseract).
