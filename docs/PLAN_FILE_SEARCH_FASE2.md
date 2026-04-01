# VINO PRO IA — Fase 2: Google File Search + Evidence Engine Avanzado

**Estado:** PENDIENTE — Iniciar después de completar los 12 testers de Google Play  
**Fecha de creación del plan:** 2026-04-01  
**Referencia de investigación:** https://youtu.be/EKKMMVdhUys  

---

## ¿Qué es Google File Search y por qué lo queremos?

Google lanzó File Search en noviembre de 2025 como un sistema RAG (Retrieval Augmented Generation)
gestionado directamente dentro de la API de Gemini.

**Lo que hace:**
- Subes archivos (JSON, PDF, TXT, DOCX, Markdown)
- Google los fragmenta, crea embeddings semánticos y los indexa automáticamente
- Cuando el usuario pregunta, Gemini busca en TUS documentos por significado (no por palabras exactas)
- Devuelve la respuesta con citas automáticas: "Según [tu_archivo.pdf], sección X..."
- Si la respuesta no está en tus documentos, no la inventa

**Documentación oficial:** https://ai.google.dev/gemini-api/docs/file-search  
**Blog de lanzamiento:** https://blog.google/technology/developers/file-search-gemini-api  

---

## Por qué encaja con VINO PRO IA

### Evidence Engine actual (Fase 1 — ya construido)
```
Capa 1: 50 mitos documentados (búsqueda por tokens en mitos_vino.json)
Capa 2: 21 vinos con datos técnicos verificados (conocimiento_vinos.json)
Capa 3: Gemini libre → riesgo de alucinación → marcado [Estimación IA]
```

### Evidence Engine con File Search (Fase 2 — pendiente)
```
Capa 1: 50+ mitos (búsqueda semántica, entiende variaciones del lenguaje)
Capa 2: Documentos verificados completos (toda la normativa DO, OIV, etc.)
Capa 3: Gemini grounded en nuestros documentos → cita automática → cero alucinación
```

**La diferencia clave:**  
En Fase 1, Capa 3 dice `[Estimación IA]` porque Gemini responde sin contexto verificado.  
En Fase 2, Capa 3 diría `"Según DO Rioja reglamento 2023, art. 14..."` porque Gemini lee NUESTROS documentos.

---

## Comparación técnica

| Capacidad | Evidence Engine Fase 1 | Evidence Engine Fase 2 |
|---|---|---|
| Detección de mitos | Tokens manuales (50 mitos) | Semántica (miles de documentos) |
| Escala | JSON editado a mano | Subir un PDF y listo |
| Citación | Etiqueta manual `📚 La realidad:` | Cita automática con sección exacta |
| Latencia Capa 3 | 3-4 segundos (Gemini libre) | Similar (Gemini + búsqueda vectorial) |
| Coste | Gratis (código local) | Gratis en consulta; $0.15/M tokens al indexar |
| Mantenimiento | Editar JSONs manualmente | Subir nuevos PDFs a medida que aparecen |

---

## Infraestructura — ya la tenemos

El File Search usa el mismo `GOOGLE_API_KEY` que ya está en Render.  
No necesitamos nuevas cuentas ni nuevos servicios.

Código de integración (Python, usando la misma librería `google-genai` que ya usamos):

```python
# En sumiller_gemini_service.py — versión Fase 2
from google import genai
from google.genai import types

client = genai.Client(api_key=GOOGLE_API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=pregunta_usuario,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=["vino-pro-ia-knowledge"]
                )
            )
        ],
        max_output_tokens=500,
        temperature=0.3,  # Temperatura baja para máxima fidelidad al documento
    )
)
# response.text incluye citas automáticas del documento fuente
```

---

## Hoja de Ruta — Fase 2

### Paso 1: Preparar el "File Search Store"
Crear el store en la API de Gemini con nombre `vino-pro-ia-knowledge`.  
Subir los documentos que ya tenemos:
- `data/mitos_vino.json` (50 mitos verificados)
- `data/conocimiento_vinos.json` (21 tipos de vino con datos técnicos)

### Paso 2: Preparar "Documentos de Verdad" adicionales
Redactar documentos verificados en formato PDF o Markdown sobre:
- Reglamentos DO oficiales (Rioja, Ribera del Duero, Rías Baixas, Priorat...)
- Normativa de elaboración por tipo de vino
- Datos de la OIV (Organización Internacional de la Viña y el Vino)
- Tablas de temperatura de servicio y maridaje verificadas

**Prioridad sugerida para los primeros documentos:**
1. `DO_Rioja_guia_verificada.md` — la más consultada por usuarios
2. `mitos_ampliados_100.json` — ampliar de 50 a 100 mitos
3. `datos_quimicos_varietales.md` — perfil enológico de uvas principales

### Paso 3: Modificar `sumiller_gemini_service.py`
Reemplazar `buscar_vino_en_nube` para que use File Search como contexto.  
Mantener las Capas 1 y 2 del Evidence Engine actual (son más rápidas y no tienen coste).  
File Search entra solo en Capa 3 cuando Capas 1 y 2 no tienen respuesta.

### Paso 4: Actualizar la UI del sumiller (frontend Expo)
Mostrar la cita del documento en la respuesta:  
`📄 Fuente: conocimiento_vinos.json — Barolo` en lugar de `✅ Dato verificado`.

### Paso 5: Testing y ajuste de temperatura
Probar con las mismas 10 preguntas de mitos y las 3 preguntas de la Fase 1.  
Verificar que las citas son correctas y que no hay alucinaciones.

---

## Documentos a redactar ANTES de implementar

Para que File Search sea útil necesitamos documentos de calidad.  
Estos son los que produciremos en la fase de preparación:

| Documento | Formato | Contenido | Estado |
|---|---|---|---|
| mitos_vino_v2.json | JSON | 50 → 100 mitos | Pendiente |
| conocimiento_vinos_v3.json | JSON | 21 → 50 vinos + datos químicos | Pendiente |
| DO_Rioja_verificada.md | Markdown | Reglamento, zonas, crianzas | Pendiente |
| DO_RiberaDuero_verificada.md | Markdown | Reglamento, Tinto Fino, añadas | Pendiente |
| maridajes_verificados.md | Markdown | Tabla científica de maridajes | Pendiente |
| variedades_uva_ciencia.md | Markdown | Perfil químico de 20 varietales | Pendiente |

---

## Lo que Gemini analizó del video (notas de investigación)

*Referencia: análisis de Gemini sobre https://youtu.be/EKKMMVdhUys*

> "Ya no necesitamos montar una infraestructura gigante. Con File Search, podemos subir nuestros 
> documentos de Realidad Histórica (regiones, uvas, normativas) y Gemini se encarga de entenderlos."

> "Gemini responde basándose exactamente en los archivos subidos. Si no está en el documento, 
> no se lo inventa."

> "La IA puede decirte incluso la página o la sección de donde saca la información [minuto 07:27]. 
> Imagina que VINO PRO IA responda: 'Según el manual de la D.O. Rioja (pág. 12), este maridaje 
> es el recomendado'."

---

## Frase que nos define (post Fase 2)

> "No te decimos lo que creemos. Te decimos lo que sabemos.  
> Y cuando lo sabemos, te decimos exactamente de dónde viene."

---

## Prerequisitos para empezar

- [ ] 12 testers completados en Google Play (cerrar fase de pruebas)
- [ ] App publicada en producción en Google Play
- [ ] Documentos de verdad redactados (al menos 2-3 antes de implementar)
- [ ] Revisar si la API key de Gemini actual tiene acceso a File Search (puede requerir plan de pago)

---

*Este documento fue creado en base a la investigación conjunta con Gemini y DeepSeek.*  
*Siguiente revisión: al completar los 12 testers.*
