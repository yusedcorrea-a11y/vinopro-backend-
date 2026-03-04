from fastapi import FastAPI, Form, HTTPException
import requests, uvicorn, json
import re

app = FastAPI()

PROMPT_MEJORADO = """
Eres un experto enólogio. Analiza el texto sobre vino y devuelve SOLO un JSON válido con esta estructura:

{
  "nombre": "nombre del vino",
  "bodega": "bodega productora", 
  "anio": "año de cosecha o NV",
  "puntuacion": 0-100,
  "tipo": "tinto/blanco/rosado/espumoso",
  "descripcion": "breve descripción en español"
}

Texto: {texto_input}
"""

def limpiar_json(respuesta: str) -> dict:
    """Limpia respuesta para extraer solo JSON"""
    try:
        # Buscar entre { y }
        match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
    except:
        pass
    return {"error": "No se pudo procesar la respuesta"}

@app.post("/analyze/text")
async def analizar(texto: str = Form(...)):
    try:
        # Llamar a Ollama
        respuesta = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": PROMPT_MEJORADO.format(texto_input=texto),
                "stream": False,
                "options": {"temperature": 0.3}
            },
            timeout=30.0
        )
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            analisis = limpiar_json(datos.get("response", ""))
            
            return {
                "success": True,
                "analysis": analisis,
                "model": "llama3.2:3b"
            }
        else:
            raise HTTPException(status_code=500, detail="Error en modelo de IA")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
