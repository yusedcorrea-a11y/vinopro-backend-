from fastapi import FastAPI, Form
import requests, uvicorn
app = FastAPI()
@app.post("/analyze/text")
async def analizar(texto: str = Form(...)):
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2:3b",
        "prompt": f"Extrae: nombre, bodega, anio. De: {texto}",
        "options": {"temperature": 0.1}
    })
    return {"resp": r.json().get("response", "")}
uvicorn.run(app, host="0.0.0.0", port=8001)
