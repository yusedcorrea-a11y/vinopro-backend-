# PROMPT OPTIMIZADO PARA ANÁLISIS DE VINO
# Estructura que funciona mejor con modelos pequeños

VINO_PROMPT = '''Eres un experto en vinos profesional español. Analiza este vino de forma concisa.

[DESCRIPCIÓN DEL VINO]
{text}

[ANÁLISIS ESTRUCTURADO]
1. **Apariencia**: 
2. **Nariz (Aromas)**: 
3. **Boca (Sabores)**: 
4. **Textura**: 
5. **Final**: 
6. **Maridaje sugerido**: 
7. **Puntuación (1-10)**:

[RESUMEN BREVE]
'''

# Versión minimalista para modelos pequeños
VINO_PROMPT_MINIMAL = '''Experto en vinos analiza: {text}

- Color:
- Aroma: 
- Sabor:
- Textura:
- Final:
- Marida con:
- Nota/10:

Respuesta:'''
