from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import requests
import uvicorn
import json
import re

app = FastAPI(title="VINO PRO - Reinicio")

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    # SYSTEM PROMPT EXPLÍCITO (para evitar italiano)
    prompt = f"""<|start_header_id|>system<|end_header_id|>
Eres un sommelier experto. Analiza textos sobre vino y extrae datos.
Responde SOLO en español y SOLO con JSON.<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Extrae JSON con: nombre, bodega, año, color, aroma.
Texto: {text}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
    
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 200}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            raw = result.get("response", "").strip()
            
            # Buscar JSON
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                try:
                    datos = json.loads(json_match.group(0))
                    return JSONResponse(content={"exito": True, "datos": datos})
                except:
                    pass
            
            return JSONResponse(content={"exito": False, "raw": raw[:200]})
        else:
            return JSONResponse(content={"error": f"HTTP {response.status_code}"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    print("🔄 VINO PRO - Reiniciado")
    uvicorn.run(app, host="0.0.0.0", port=8000)
