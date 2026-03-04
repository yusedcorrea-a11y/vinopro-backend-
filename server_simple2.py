from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import requests
import uvicorn

app = FastAPI(title="VINO PRO")

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    prompt = f"Analiza este vino y di su nombre: {text}"
    
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=30)
    result = response.json()
    
    return JSONResponse(content={
        "respuesta": result.get("response", ""),
        "status": response.status_code
    })

if __name__ == "__main__":
    print("✅ Servidor iniciado - Puerto 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
