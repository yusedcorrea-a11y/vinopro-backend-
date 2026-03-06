# Estrategia de Mejora del Escáner VINO — Visión Artificial y OCR

**Autor:** Ingeniero Senior en Visión Artificial  
**Fecha:** Marzo 2025  
**Objetivo:** Aumentar la tasa de éxito del OCR en etiquetas de vino (reflejos, curvatura, ruido) y garantizar JSON estructurado.

---

## 1. DIAGNÓSTICO DEL CÓDIGO ACTUAL

### 1.1 Flujo actual del escáner

```
Imagen → pyzbar (códigos) → [si EAN + OFF] → respuesta
       → Tesseract OCR (sin preprocesamiento) → normalizador → BD local / OFF
       → API4AI (solo logging, NO se usa para devolver)
```

### 1.2 Cuellos de botella identificados

| Problema | Ubicación | Impacto |
|----------|-----------|---------|
| **Sin preprocesamiento de imagen** | `ocr_service.py` | Tesseract recibe imagen cruda: reflejos, sombras y ruido degradan el OCR |
| **Reflejos en cristal** | — | Zonas quemadas/blancas impiden leer texto |
| **Curvatura de etiqueta** | — | Texto deformado; Tesseract asume texto plano |
| **Contraste bajo** | — | Etiquetas oscuras o iluminación irregular |
| **Ruido de compresión** | — | JPEG de móvil con artefactos |
| **API4AI no integrada** | `escaneo.py` | Se llama pero no se usa (evitar falsos positivos); no hay alternativa de visión |
| **Sin extracción de entidades** | — | No se extrae explícitamente Bodega, Añada, DO, Variedad del texto OCR |
| **JSON genérico** | — | Cuando no hay match, `vino` tiene campos genéricos; falta estructura fija |

### 1.3 Preprocesamiento actual (ocr_service.py)

```python
# Solo hace:
image.convert("RGB")
if max(w,h) > 1200: image.resize(...)
pytesseract.image_to_string(image, lang="spa+eng")
```

**No hay:** desenfoque gaussiano, CLAHE, binarización adaptativa, corrección de perspectiva, reducción de reflejos.

---

## 2. ESTRATEGIA DE MEJORA PROPUESTA

### Fase 1: Preprocesamiento con OpenCV (prioridad alta)

**Objetivo:** Mejorar la imagen antes de Tesseract para reflejos, ruido y contraste.

| Técnica | Propósito | Eficiencia en IdeaPad 3 |
|---------|-----------|-------------------------|
| Escala de grises | Reduce ruido cromático; Tesseract funciona mejor | ✅ Muy ligero |
| CLAHE (Contrast Limited AHE) | Iluminación irregular, sombras | ✅ Ligero |
| Bilateral filter | Reduce ruido preservando bordes (texto) | ✅ Aceptable |
| Morfología (opening) | Elimina ruido fino, refuerza trazos | ✅ Muy ligero |
| Sharpening (unsharp mask) | Texto más nítido | ✅ Ligero |
| Binarización adaptativa (Otsu/adaptativa) | Alternativa para etiquetas muy degradadas | ✅ Ligero |

**Implementación sugerida:** Crear `services/image_preprocessor.py` con varias pipelines y elegir la que dé mejor resultado (p. ej. combinando OCR en varias versiones y quedándose con la de más texto válido).

### Fase 2: OCR multi-paso

**Idea:** Ejecutar Tesseract sobre 2–3 versiones de la imagen y fusionar/priorizar resultados.

1. **Pipeline A:** Original → escala de grises → CLAHE → Tesseract  
2. **Pipeline B:** Original → bilateral → sharpen → Tesseract  
3. **Pipeline C:** Original → escala de grises → Otsu/adaptativa → Tesseract  

Criterio de selección: longitud de texto legible, presencia de palabras clave (bodega, crianza, reserva, etc.) o score interno de Tesseract si se usa `image_to_data`.

### Fase 3: Modelo de visión para extracción de entidades (prioridad media)

**Objetivo:** Cuando el OCR falle o sea ambiguo, usar GPT-4o o Claude 3.5 Vision para extraer entidades estructuradas directamente de la imagen.

**Ventajas:**
- Mejor con curvatura y reflejos
- Salida estructurada: Bodega, Nombre, Añada, DO, Variedad
- No depende de Tesseract

**Requisitos:**
- API key de OpenAI o Anthropic
- Llamada HTTP con la imagen en base64
- Prompt específico para etiquetas de vino

**Cuándo usarlo:** Solo si OCR + BD + OFF no dan resultado fiable, o como refuerzo para validar/rellenar campos.

### Fase 4: Estructura JSON unificada

**Esquema objetivo para toda respuesta de escaneo:**

```json
{
  "encontrado_en_bd": true,
  "consulta_id": "uuid",
  "vino": {
    "nombre": "Viña Pedrosa Crianza",
    "bodega": "Hnos Pérez Pascuas",
    "region": "Ribera del Duero",
    "pais": "España",
    "tipo": "tinto",
    "añada": 2021,
    "denominacion_origen": "Ribera del Duero",
    "variedad": "Tempranillo",
    "puntuacion": 92,
    "precio_estimado": "12-18€",
    "descripcion": "...",
    "notas_cata": "...",
    "maridaje": "..."
  },
  "vino_key": "vina_pedrosa_crianza",
  "entidades_extraidas": {
    "bodega": "Hnos Pérez Pascuas",
    "nombre": "Viña Pedrosa Crianza",
    "añada": 2021,
    "denominacion_origen": "Ribera del Duero",
    "variedad": "Tempranillo"
  },
  "mensaje": "...",
  "es_pro": false
}
```

- `entidades_extraidas`: siempre presente cuando hay OCR o visión; permite al frontend mostrar “lo que leyó” aunque no haya match.
- `añada`, `denominacion_origen`, `variedad`: añadidos al modelo de vino donde la BD lo permita.

---

## 3. PLAN DE IMPLEMENTACIÓN

### Paso 1: Instalar dependencias

```powershell
cd c:\Users\yused\Documents\VINO_PRO_FINAL\backend_optimized

# OpenCV para preprocesamiento (ligero, sin contrib extra)
pip install opencv-python-headless>=4.8.0

# Actualizar requirements.txt
echo opencv-python-headless>=4.8.0 >> requirements.txt
```

### Paso 2: Crear módulo de preprocesamiento

Crear `services/image_preprocessor.py` con:

- `preprocesar_para_ocr(contenido: bytes) -> list[tuple[str, bytes]]`  
  Devuelve lista de `(nombre_pipeline, imagen_bytes)` para OCR multi-paso.

- Pipelines internos:
  - `_pipeline_grayscale_clahe()`
  - `_pipeline_bilateral_sharpen()`
  - `_pipeline_adaptive_binary()`

### Paso 3: Modificar ocr_service.py

- Llamar al preprocesador.
- Ejecutar Tesseract sobre cada versión.
- Fusionar resultados (por longitud, palabras clave o `image_to_data`).
- Mantener compatibilidad con la firma actual `extraer_texto_de_imagen(contenido, idioma)`.

### Paso 4: Servicio de extracción de entidades (opcional)

Crear `services/vision_entity_service.py`:

- `extraer_entidades_vision(imagen_bytes: bytes) -> dict | None`  
  Usa GPT-4o o Claude Vision con prompt tipo:

  ```
  Extrae de esta etiqueta de vino: Bodega, Nombre del vino, Añada (año), 
  Denominación de Origen, Variedad de uva. Responde solo JSON válido.
  ```

- Integrar en `escaneo.py` como fallback cuando OCR + BD + OFF no den resultado.

### Paso 5: Ajustar esquema JSON en escaneo.py

- Añadir `entidades_extraidas` cuando se disponga de OCR o visión.
- Mapear `region` → `denominacion_origen` cuando proceda.
- Añadir `añada` y `variedad` al objeto `vino` cuando existan en BD o en la extracción.

---

## 4. COMANDOS LISTOS PARA COPIAR Y PEGAR

### Instalación completa (Windows, IdeaPad 3)

```powershell
# 1. Entorno virtual (si no existe)
cd c:\Users\yused\Documents\VINO_PRO_FINAL\backend_optimized
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Dependencias Python
pip install opencv-python-headless>=4.8.0
pip install Pillow>=10.0.0 pytesseract>=0.3.10

# 3. Tesseract (si no está instalado)
# Descargar: https://github.com/UB-Mannheim/tesseract/wiki
# O: winget install UB-Mannheim.TesseractOCR

# 4. Idiomas Tesseract (spa + eng)
# En Windows, ejecutar como admin:
# cd "C:\Program Files\Tesseract-OCR"
# .\tessdata\download script for your language
# O descargar spa.traineddata de https://github.com/tesseract-ocr/tessdata

# 5. Verificar
python -c "import cv2; import pytesseract; print('OK')"
```

### Variables de entorno (.env)

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
DATA_FOLDER=data
# Opcional para visión:
OPENAI_API_KEY=sk-...
# o
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 5. PRIORIZACIÓN RECOMENDADA

| Orden | Tarea | Esfuerzo | Impacto |
|-------|-------|----------|---------|
| 1 | Preprocesamiento OpenCV (CLAHE + bilateral + sharpen) | Medio | Alto |
| 2 | OCR multi-paso (2–3 pipelines) | Bajo | Alto |
| 3 | Estructura JSON con `entidades_extraidas` | Bajo | Medio |
| 4 | Servicio de visión (GPT-4o/Claude) como fallback | Medio | Alto (casos difíciles) |
| 5 | Corrección de perspectiva/curvatura (opcional) | Alto | Medio (etiquetas muy curvas) |

---

## 6. NOTAS PARA LENOVO IDEAPAD 3

- **OpenCV** y **Tesseract** son adecuados para CPU: no requieren GPU.
- Evitar modelos locales pesados (EasyOCR, PaddleOCR) en este hardware.
- GPT-4o/Claude Vision se ejecutan en la nube; el backend solo envía la imagen y recibe JSON.
- `opencv-python-headless` evita dependencias de GUI y reduce tamaño.

---

## 7. PRÓXIMOS PASOS

1. Implementar `image_preprocessor.py` con los 3 pipelines.
2. Integrar en `ocr_service.py` y probar con fotos reales de etiquetas.
3. Añadir `entidades_extraidas` al flujo de `escaneo.py`.
4. (Opcional) Implementar `vision_entity_service.py` y usarlo como fallback.

Si quieres, el siguiente paso puede ser implementar el preprocesador y la integración en `ocr_service.py` paso a paso.
