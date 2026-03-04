from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import requests
import uvicorn
import json
import re

app = FastAPI(title="VINO PRO")

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    prompt = f"Extrae JSON con: nombre, bodega, ano, color, aroma. Texto: {text}"
    
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return JSONResponse(content={"respuesta": result.get("response", "")})
        else:
            return JSONResponse(content={"error": "Ollama error"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    print("Servidor iniciado en puerto 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
