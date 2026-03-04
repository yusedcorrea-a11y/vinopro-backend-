from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import requests
import uvicorn

app = FastAPI(title="DEBUG 2")

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    try:
        prompt = f"Analiza: {text}"
        
        payload = {
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1}
        }
        
        print(f"Enviando a Ollama: {text[:20]}...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        print(f"Status: {response.status_code}")
        
        result = response.json()
        raw = result.get("response", "NO RESPONSE")
        
        return JSONResponse(content={
            "status": response.status_code,
            "raw": raw,
            "raw_repr": repr(raw)  # Muestra caracteres especiales
        })
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    print("🔍 DEBUG 2 - Timeout 60s")
    uvicorn.run(app, host="0.0.0.0", port=8000)
