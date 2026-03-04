from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import requests
import uvicorn
import json
import re

app = FastAPI(title="VINO PRO - Mejorado")

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    # PROMPT MEJORADO - Instrucciones CLARAS
    prompt = f"""Extrae informacion de este texto sobre vino.

TEXTO: {text}

Devuelve SOLO un objeto JSON con estas claves exactas:
- "nombre"
- "bodega" 
- "ano"
- "color"
- "aroma"

Si un dato no esta en el texto, usa "" (vacio).
NO añadas explicaciones, texto, ni ```json```.
SOLO el objeto JSON:"""
    
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.05, "num_predict": 150}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            raw_text = result.get("response", "").strip()
            
            # 1. Quitar ```json ``` y texto alrededor
            clean_text = re.sub(r'```json|```', '', raw_text)
            clean_text = re.sub(r'^.*?\{', '{', clean_text, flags=re.DOTALL)
            
            # 2. Buscar JSON
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    datos = json.loads(json_str)
                    return JSONResponse(content={"exito": True, "datos": datos})
                except:
                    pass
            
            return JSONResponse(content={"exito": False, "raw": raw_text[:200]})
            
        else:
            return JSONResponse(content={"error": "Ollama no responde"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    print("🚀 Servidor Mejorado - Puerto 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
