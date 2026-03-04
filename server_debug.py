from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import requests
import uvicorn

app = FastAPI(title="DEBUG")

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    prompt = f'''Extrae JSON de: "{text}"'''
    
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.05}
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=30)
    result = response.json()
    
    # MOSTRAR RAW EXACTO que devuelve Ollama
    raw_response = result.get("response", "")
    
    return JSONResponse(content={
        "raw_exact": raw_response,
        "raw_length": len(raw_response),
        "first_10_chars": repr(raw_response[:50])
    })

if __name__ == "__main__":
    print("🔍 DEBUG Server - Puerto 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
